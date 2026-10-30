"""Módulo 3 – SIG: análisis espacial de parques industriales de Mendoza
y localización preliminar de la planta Square Housing.
Datos base: carpeta GIS de la cátedra (COGAR, parques_3_modificado_modificado.tif, Capas_shp)."""
import json, numpy as np, pandas as pd, geopandas as gpd
from shapely import wkt
from shapely.geometry import Point, box, MultiPoint
from shapely.ops import voronoi_diagram
import shapely

RAW = "/tmp/gis/raw"
OUT = "/tmp/gis/out"
import os; os.makedirs(OUT, exist_ok=True)
WGS, UTM = "EPSG:4326", "EPSG:32719"   # UTM 19S para medir en metros

# ---------- 1. Parques industriales (puntos) ----------
p = pd.read_csv(f"{RAW}/COGAR/COGAR/locaciones2.csv", sep=";")
p = p[["id", "Denom", "X", "Y"]]
# Santa Rosa no está en el CSV: se digitaliza sobre el raster georreferenciado
p.loc[len(p)] = [18, "Parque Industrial Santa Rosa", -68.1060, -33.3466]
p["origen"] = ["CSV cátedra"] * 17 + ["Digitalizado sobre parques_3.tif"]
parques = gpd.GeoDataFrame(p, geometry=gpd.points_from_xy(p.X, p.Y), crs=WGS).drop(columns=["X", "Y"])
parques = parques.rename(columns={"Denom": "nombre"})

# ---------- 2. Polígonos industriales ----------
def read_wkt(path, sep, name_col=None, fixed=None):
    d = pd.read_csv(path, sep=sep)
    g = gpd.GeoDataFrame(d, geometry=d["WKT"].apply(wkt.loads), crs=WGS)
    g["zona"] = fixed if fixed else g[name_col]
    return g[["zona", "geometry"]]
C = f"{RAW}/COGAR/COGAR"
polys = pd.concat([
    read_wkt(f"{C}/Capa Poligonos Industriales.csv", ",", fixed="Rodríguez Peña / Gral. Ortega / Alcoholera"),
    read_wkt(f"{C}/Capa Refineria Lujan de Cuyo (adicional).csv", ",", fixed="Refinería Luján de Cuyo"),
    read_wkt(f"{C}/Rivadavia.csv", ";", fixed="Zona Industrial Rivadavia"),
    read_wkt(f"{C}/San_Martin.csv", ";", fixed="Zona Industrial San Martín"),
], ignore_index=True)
pasip = json.loads(open(f"{RAW}/Uso_Suelo/Uso Suelo/qgis2web_2020_08_05-22_19_35_879323/data/PASIP_3.js").read().split("=", 1)[1])
pg = gpd.GeoDataFrame.from_features(pasip["features"], crs=WGS); pg["zona"] = "Parque de Servicios e Industrias Palmira (PASIP)"
polys = gpd.GeoDataFrame(pd.concat([polys, pg[["zona", "geometry"]]], ignore_index=True), crs=WGS)
polys["sup_ha"] = polys.to_crs(UTM).area / 1e4
polys["sup_ha"] = polys["sup_ha"].round(1)

# superficie asociada a cada parque (polígonos a menos de 3 km del punto)
pu = parques.to_crs(UTM)

# ---------- 3. Demanda: cabeceras departamentales (Censo 2022) ----------
dem = pd.DataFrame([
    ("Capital", -68.8458, -32.8895, 127160), ("Godoy Cruz", -68.8456, -32.9283, 195159),
    ("Guaymallén", -68.7870, -32.8990, 321966), ("Las Heras", -68.8290, -32.8506, 234401),
    ("Luján de Cuyo", -68.8773, -33.0366, 175056), ("Maipú", -68.7880, -32.9832, 219402),
    ("Lavalle", -68.5960, -32.7231, 47167), ("San Martín", -68.4680, -33.0810, 139792),
    ("Junín", -68.4880, -33.1450, 46604), ("Rivadavia", -68.4640, -33.1910, 63724),
    ("Santa Rosa", -68.1500, -33.2540, 19382)], columns=["departamento", "lon", "lat", "pob_2022"])
demanda = gpd.GeoDataFrame(dem, geometry=gpd.points_from_xy(dem.lon, dem.lat), crs=WGS).drop(columns=["lon", "lat"])
du = demanda.to_crs(UTM)

# centro de gravedad de la demanda (ponderado por población)
w = du["pob_2022"].values
cx, cy = (du.geometry.x * w).sum() / w.sum(), (du.geometry.y * w).sum() / w.sum()
cg = gpd.GeoDataFrame({"nombre": ["Centro de gravedad de la demanda"]}, geometry=[Point(cx, cy)], crs=UTM)

# ---------- 4. Área de estudio, Voronoi y Delaunay ----------
prov = gpd.read_file(f"{RAW}/Capas_shp/Capas_shp/Argentina.shp")
prov = prov[prov["JURISDICCI"].str.contains("Mendoza", case=False)].to_crs(UTM)
import rasterio
b = rasterio.open(f"{RAW}/parques.tif").bounds
area = gpd.GeoDataFrame(geometry=[box(*b)], crs=WGS).to_crs(UTM)
area = gpd.overlay(area, prov[["geometry"]], how="intersection")
A = area.geometry.iloc[0]

pts = MultiPoint(list(pu.geometry))
vor = voronoi_diagram(pts, envelope=A.buffer(20000))
cells = []
for c in vor.geoms:
    c2 = c.intersection(A)
    pid = pu[pu.geometry.within(c)]["id"].iloc[0]
    cells.append((pid, c2))
voronoi = gpd.GeoDataFrame(cells, columns=["id", "geometry"], crs=UTM).merge(parques[["id", "nombre"]], on="id")
voronoi["area_km2"] = (voronoi.area / 1e6).round(0)
# población que cae en cada celda = demanda "servida" por el parque más cercano
jj = gpd.sjoin(du, voronoi[["id", "geometry"]], predicate="within")
voronoi["pob_cercana"] = voronoi["id"].map(jj.groupby("id")["pob_2022"].sum()).fillna(0).astype(int)

tri = shapely.delaunay_triangles(pts, only_edges=True)
edges = gpd.GeoDataFrame(geometry=list(tri.geoms), crs=UTM)
edges["long_km"] = (edges.length / 1000).round(1)
# vecinos por parque
def ends(line):
    return [tuple(np.round(c, 3)) for c in (line.coords[0], line.coords[-1])]
key = {tuple(np.round((g.x, g.y), 3)): i for i, g in zip(pu["id"], pu.geometry)}
nb = {i: [] for i in pu["id"]}
for g, L in zip(edges.geometry, edges.long_km):
    a, b2 = [key[e] for e in ends(g)]
    nb[a].append(L); nb[b2].append(L)

# ---------- 5. Indicadores de localización ----------
D = np.array([[pt.distance(d) / 1000 for d in du.geometry] for pt in pu.geometry])   # km
parques["dist_media_pond_km"] = (D @ w / w.sum()).round(1)
parques["dist_cg_km"] = [round(pt.distance(cg.geometry.iloc[0]) / 1000, 1) for pt in pu.geometry]
gm = du["departamento"].isin(["Capital", "Godoy Cruz", "Guaymallén", "Las Heras", "Luján de Cuyo", "Maipú"]).values
parques["pob_15km"] = [int(w[D[i] <= 15].sum()) for i in range(len(pu))]
parques["vecinos_delaunay"] = parques["id"].map(lambda i: len(nb[i]))
parques["dist_media_vecinos_km"] = parques["id"].map(lambda i: round(np.mean(nb[i]), 1))
parques = parques.merge(voronoi[["id", "area_km2", "pob_cercana"]], on="id")
parques["ranking"] = parques["dist_media_pond_km"].rank(method="min").astype(int)
parques = parques.sort_values("ranking")

# ---------- 6. Exportar ----------
gpkg = f"{OUT}/Modulo3_SIG_SquareHousing.gpkg"
if os.path.exists(gpkg): os.remove(gpkg)
for name, g in [("parques_industriales", parques), ("poligonos_industriales", polys),
                ("demanda_cabeceras", demanda), ("centro_gravedad", cg.to_crs(WGS)),
                ("voronoi", voronoi.to_crs(WGS)), ("delaunay", edges.to_crs(WGS)),
                ("area_estudio", area.to_crs(WGS))]:
    g.to_file(gpkg, layer=name, driver="GPKG")
parques.drop(columns="geometry").to_csv(f"{OUT}/ranking_parques.csv", index=False)
print(parques.drop(columns="geometry").to_string())
print("CG:", cg.to_crs(WGS).geometry.iloc[0])
print(polys.drop(columns="geometry").to_string())
print("Delaunay aristas:", len(edges), "long media", edges.long_km.mean().round(1))

# ---------- 7. Mapas estáticos ----------
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rasterio.plot import show
R = rasterio.open(f"{RAW}/parques.tif")
pw, polw, vw, ew, dw, cgw = (parques.to_crs(WGS), polys, voronoi.to_crs(WGS), edges.to_crs(WGS),
                             demanda, cg.to_crs(WGS))
def base(title, fade=0.55):
    fig, ax = plt.subplots(figsize=(10, 7.4), dpi=170)
    show(R, ax=ax, alpha=fade)
    ax.set_xlim(R.bounds.left, R.bounds.right); ax.set_ylim(R.bounds.bottom, R.bounds.top)
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
    ax.tick_params(labelsize=7); ax.set_xlabel("Longitud", fontsize=8); ax.set_ylabel("Latitud", fontsize=8)
    return fig, ax
def done(fig, ax, name):
    ax.legend(loc="lower left", fontsize=7.5, framealpha=0.9)
    fig.tight_layout(); fig.savefig(f"{OUT}/{name}.png"); plt.close(fig)

fig, ax = base("Mapa 1 – Parques y zonas industriales (capas de la cátedra)")
polw.plot(ax=ax, color="#c0392b", alpha=0.55, edgecolor="#7b241c", linewidth=0.6, label="Polígonos industriales")
pw.plot(ax=ax, color="#1f4e79", markersize=28, edgecolor="white", linewidth=0.6, zorder=5, label="Parques (puntos)")
for _, r in pw.iterrows():
    ax.annotate(str(r.id), (r.geometry.x, r.geometry.y), xytext=(4, 3), textcoords="offset points", fontsize=7, fontweight="bold", color="#1f4e79")
ax.plot([], [], " ", label="Números = id de parque (ver tabla)")
done(fig, ax, "mapa1_parques")

fig, ax = base("Mapa 2 – Polígonos de Voronoi y triangulación de Delaunay", 0.35)
vw.boundary.plot(ax=ax, color="#d9682b", linewidth=1.2, label="Voronoi (área de influencia)")
ew.plot(ax=ax, color="#555", linewidth=0.7, linestyle="--", label="Delaunay (vecindad)")
pw.plot(ax=ax, color="#1f4e79", markersize=26, edgecolor="white", zorder=5, label="Parques")
done(fig, ax, "mapa2_voronoi_delaunay")

fig, ax = base("Mapa 3 – Demanda, centro de gravedad y parques mejor ubicados", 0.4)
vw.boundary.plot(ax=ax, color="#d9682b", linewidth=0.6, alpha=0.6)
dw.plot(ax=ax, markersize=dw.pob_2022 / 1500, color="#2e86c1", alpha=0.45, edgecolor="#1b4f72", label="Demanda (población 2022)")
for _, r in dw.iterrows():
    ax.annotate(r.departamento, (r.geometry.x, r.geometry.y), xytext=(5, -9), textcoords="offset points", fontsize=6.5, color="#1b4f72")
top = pw[pw.ranking <= 3]
pw.plot(ax=ax, color="#999", markersize=14, zorder=4, label="Otros parques")
top.plot(ax=ax, color="#c0392b", markersize=60, marker="*", zorder=6, label="Top 3 (menor distancia ponderada)")
cgw.plot(ax=ax, color="black", marker="X", markersize=90, zorder=7, label="Centro de gravedad de la demanda")
done(fig, ax, "mapa3_localizacion")

# zoom Gran Mendoza
fig, ax = base("Mapa 4 – Detalle Gran Mendoza", 0.6)
ax.set_xlim(-68.95, -68.65); ax.set_ylim(-33.08, -32.85)
polw.plot(ax=ax, color="#c0392b", alpha=0.45, edgecolor="#7b241c", linewidth=0.6, label="Polígonos industriales")
vw.boundary.plot(ax=ax, color="#d9682b", linewidth=1.0, label="Voronoi")
pw.plot(ax=ax, color="#1f4e79", markersize=30, edgecolor="white", zorder=5, label="Parques")
for _, r in pw[pw.geometry.x.between(-68.95, -68.65) & pw.geometry.y.between(-33.08, -32.85)].iterrows():
    ax.annotate(r.nombre.replace("Zona Industrial ", "Z.I. ").replace("Parque Industrial ", "P.I. "), (r.geometry.x, r.geometry.y), xytext=(5, 4), textcoords="offset points", fontsize=6.5, fontweight="bold", color="#1f4e79")
dw.plot(ax=ax, markersize=dw.pob_2022 / 1500, color="#2e86c1", alpha=0.4, label="Demanda")
cgw.plot(ax=ax, color="black", marker="X", markersize=90, zorder=7, label="Centro de gravedad")
done(fig, ax, "mapa4_gran_mendoza")
