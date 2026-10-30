import geopandas as gpd, folium, rasterio, base64
from folium.plugins import MeasureControl, MiniMap
G = "/tmp/gis/out/Modulo3_SIG_SquareHousing.gpkg"
L = {n: gpd.read_file(G, layer=n) for n in ["parques_industriales","poligonos_industriales","demanda_cabeceras","centro_gravedad","voronoi","delaunay"]}
m = folium.Map(location=[-32.98, -68.6], zoom_start=10, tiles=None, control_scale=True)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri World Imagery", name="Satélite (Esri)").add_to(m)
b = rasterio.open("/tmp/gis/raw/parques.tif").bounds
from PIL import Image; Image.open("/tmp/gis/parques.png").save("/tmp/gis/parques_q.jpg", quality=80)
img = "data:image/jpeg;base64," + base64.b64encode(open("/tmp/gis/parques_q.jpg","rb").read()).decode()
folium.raster_layers.ImageOverlay(img, bounds=[[b.bottom, b.left], [b.top, b.right]], opacity=0.6, name="Raster cátedra: parques_3.tif", show=False).add_to(m)

fg = folium.FeatureGroup(name="Voronoi (área de influencia)")
folium.GeoJson(L["voronoi"], style_function=lambda f: {"color": "#d9682b", "weight": 1.5, "fillOpacity": 0.04},
    tooltip=folium.GeoJsonTooltip(["nombre","area_km2","pob_cercana"], aliases=["Parque","Área celda (km²)","Población más cercana"])).add_to(fg); fg.add_to(m)
fg = folium.FeatureGroup(name="Delaunay (vecindad)")
folium.GeoJson(L["delaunay"], style_function=lambda f: {"color": "#555", "weight": 1, "dashArray": "4 4"},
    tooltip=folium.GeoJsonTooltip(["long_km"], aliases=["Longitud (km)"])).add_to(fg); fg.add_to(m)
fg = folium.FeatureGroup(name="Polígonos industriales")
folium.GeoJson(L["poligonos_industriales"], style_function=lambda f: {"color": "#7b241c", "fillColor": "#c0392b", "weight": 1, "fillOpacity": 0.5},
    tooltip=folium.GeoJsonTooltip(["zona","sup_ha"], aliases=["Zona","Superficie (ha)"])).add_to(fg); fg.add_to(m)
fg = folium.FeatureGroup(name="Demanda (población 2022)")
for _, r in L["demanda_cabeceras"].iterrows():
    folium.CircleMarker([r.geometry.y, r.geometry.x], radius=(r.pob_2022/4000)**0.5*1.5, color="#1b4f72", fill=True, fill_color="#2e86c1", fill_opacity=0.45,
        tooltip=f"{r.departamento}: {r.pob_2022:,} hab.".replace(",", ".")).add_to(fg)
fg.add_to(m)
fg = folium.FeatureGroup(name="Parques industriales")
for _, r in L["parques_industriales"].iterrows():
    top = r.ranking <= 3
    html = (f"<b>{r.nombre}</b><br>Ranking: {r.ranking}°<br>Distancia media ponderada a la demanda: {r.dist_media_pond_km} km"
            f"<br>Distancia al centro de gravedad: {r.dist_cg_km} km<br>Población a ≤15 km: {r.pob_15km:,}".replace(",", ".")
            + f"<br>Vecinos Delaunay: {r.vecinos_delaunay}")
    folium.CircleMarker([r.geometry.y, r.geometry.x], radius=9 if top else 6, color="white", weight=1.5, fill=True,
        fill_color="#c0392b" if top else "#1f4e79", fill_opacity=1, popup=folium.Popup(html, max_width=280), tooltip=r.nombre).add_to(fg)
fg.add_to(m)
c = L["centro_gravedad"].geometry.iloc[0]
folium.Marker([c.y, c.x], tooltip="Centro de gravedad de la demanda", icon=folium.Icon(color="black", icon="crosshairs", prefix="fa")).add_to(m)
MeasureControl(primary_length_unit="kilometers", primary_area_unit="hectares").add_to(m)
MiniMap(toggle_display=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)
title = """<div style="position:fixed;top:10px;left:55px;z-index:9999;background:white;padding:8px 12px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.3);font-family:Arial;max-width:340px">
<b>Parques industriales de Mendoza – Localización Square Housing</b><br><span style="font-size:12px;color:#555">TyHM II · Módulo 3 SIG · Grupo 11. Rojo: top 3 por menor distancia ponderada a la demanda.</span></div>"""
m.get_root().html.add_child(folium.Element(title))
m.get_root().header.add_child(folium.Element('<title>Mapa SIG Square Housing</title>'))
m.save("/tmp/gis/out/index.html")
print("ok")
