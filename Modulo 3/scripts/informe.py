import pandas as pd, geopandas as gpd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import KeepTogether, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

OUT = "/tmp/gis/out"; G = f"{OUT}/Modulo3_SIG_SquareHousing.gpkg"
park = gpd.read_file(G, layer="parques_industriales").sort_values("ranking")
poly = gpd.read_file(G, layer="poligonos_industriales")
dem = gpd.read_file(G, layer="demanda_cabeceras")
cg = gpd.read_file(G, layer="centro_gravedad").geometry.iloc[0]
edges = gpd.read_file(G, layer="delaunay")

ss = getSampleStyleSheet(); AZ = colors.HexColor("#1f4e79")
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=10.3, leading=14.6, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, textColor=AZ, spaceBefore=8, spaceAfter=8, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, textColor=AZ, spaceBefore=6, spaceAfter=4, keepWithNext=1)
bul = ParagraphStyle("bul", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=3)
cell = ParagraphStyle("c", parent=body, fontSize=8.2, leading=9.8, alignment=0, spaceAfter=0)
cellc = ParagraphStyle("cc", parent=cell, alignment=TA_CENTER)
cap = ParagraphStyle("cap", parent=body, fontSize=8.5, textColor=colors.HexColor("#555"), alignment=TA_CENTER)
C = lambda s: ParagraphStyle("x", parent=body, alignment=TA_CENTER)
P = lambda t: Paragraph(t, body)
B = lambda items: [Paragraph(i, bul, bulletText="•") for i in items]
H = lambda t: Paragraph(f"<font color='white'><b>{t}</b></font>", cellc)
def tbl(data, widths, hl_rows=()):
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#b0b0b0")), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3), ("BACKGROUND", (0,0), (-1,0), AZ)]
    for r in range(1, len(data)):
        if r % 2 == 0: st.append(("BACKGROUND", (0,r), (-1,r), colors.HexColor("#eef3f9")))
    for r in hl_rows: st.append(("BACKGROUND", (0,r), (-1,r), colors.HexColor("#fde2d6")))
    t.setStyle(TableStyle(st)); return t
def img(name, w=15.5, ratio=7.4/10): return Image(f"{OUT}/{name}.png", width=w*cm, height=w*ratio*cm)
fmt = lambda n: f"{int(n):,}".replace(",", ".")

S = []
S += [Spacer(1, 3*cm),
      Paragraph("Universidad Nacional de Cuyo – Facultad de Ingeniería<br/>Ingeniería Industrial", C(0)), Spacer(1, 1.2*cm),
      Paragraph("Técnicas y Herramientas Modernas II", ParagraphStyle("t0", parent=h2, alignment=TA_CENTER, fontSize=14)), Spacer(1, .3*cm),
      Paragraph("Módulo 3 – Sistemas de Información Geográfica", ParagraphStyle("t1", parent=h1, alignment=TA_CENTER, fontSize=21, leading=27)),
      Spacer(1, .3*cm),
      Paragraph("Análisis espacial de los parques industriales de Mendoza y localización preliminar de la planta de Square Housing",
                ParagraphStyle("t2", parent=body, alignment=TA_CENTER, fontSize=12.5, leading=17)), Spacer(1, 2.2*cm),
      Paragraph("<b>Integrantes – Grupo 11</b>", C(0)), Spacer(1, .2*cm)]
S += [tbl([[H("Apellido y nombre"), H("Legajo")]] + [[Paragraph(a, cell), Paragraph(b, cellc)] for a, b in
          [("Marsonet, Santiago", "14131"), ("Royo, Santiago", "14141"), ("Gimenez, Lisandro", "14122"), ("Bordon, Joaquín", "14104")]], [6*cm, 3*cm]),
      Spacer(1, 1.2*cm), Paragraph("Segundo semestre 2026 – Mendoza, Argentina", C(0)), PageBreak()]

S += [Paragraph("1. Objetivo", h1),
  P("Aplicar herramientas de Sistemas de Información Geográfica (SIG) sobre las capas provistas por la cátedra para analizar la distribución de los "
    "parques, zonas y áreas industriales del oasis norte y este de Mendoza, y usar ese análisis como insumo para la <b>etapa de localización</b> "
    "del Proyecto Final de Estudios del grupo: una planta de fabricación de viviendas modulares industrializadas (Square Housing)."),
  P("La pregunta que guía el trabajo es: <i>¿qué parque industrial minimiza la distancia a la demanda de vivienda, y cómo se reparte el territorio entre los parques existentes?</i>"),
  Paragraph("2. Datos utilizados", h1),
  tbl([[H("Capa"), H("Tipo"), H("Origen"), H("Uso en el trabajo")]] + [[Paragraph(a, cell), Paragraph(b, cellc), Paragraph(c, cell), Paragraph(d, cell)] for a, b, c, d in [
      ("parques_3_modificado_modificado.tif", "Raster RGB", "Cátedra (carpeta GIS)", "Mapa base georreferenciado de parques, oasis y departamentos."),
      ("locaciones2.csv", "Puntos (X, Y)", "Cátedra (COGAR)", "Ubicación de 17 parques y zonas industriales."),
      ("Parque Industrial Santa Rosa", "Punto", "Digitalizado por el grupo", "Parque presente en el raster y ausente en el CSV."),
      ("Polígonos industriales (WKT)", "Polígonos", "Cátedra (COGAR / Uso Suelo)", "Rodríguez Peña, refinería, San Martín, Rivadavia y PASIP."),
      ("Argentina.shp", "Polígonos", "Cátedra (Capas_shp)", "Límite provincial para recortar el área de estudio."),
      ("Población por departamento", "Tabla", "INDEC, Censo 2022", "Peso de cada nodo de demanda."),
      ("Cabeceras departamentales", "Puntos", "Ubicación aproximada de cada ciudad cabecera", "Nodos de demanda (11 departamentos del área)."),
  ]], [4.3*cm, 2.1*cm, 3.8*cm, 6.3*cm]),
]

S += [Paragraph("3. Metodología", h1),
  P("El procesamiento replica el flujo de trabajo de QGIS visto en clase. Se realizó en Python con GeoPandas y Shapely, que usan los mismos motores "
    "(GDAL y GEOS) que QGIS. Todas las capas se entregan en un GeoPackage para abrirlas y verificarlas en QGIS."),
  *B(["<b>Sistema de referencia:</b> las capas vienen en coordenadas geográficas (EPSG:4326). Para medir distancias y áreas se reproyectaron a "
      "<b>WGS 84 / UTM zona 19S (EPSG:32719)</b>, un sistema métrico adecuado para Mendoza.",
      "<b>Capa de puntos desde texto:</b> el CSV de locaciones se cargó como capa delimitada por texto con los campos X e Y. El Parque Industrial "
      "Santa Rosa, que falta en el CSV, se digitalizó sobre el raster georreferenciado.",
      "<b>Polígonos desde WKT:</b> las zonas industriales se cargaron desde la columna WKT de los CSV. Su superficie se calculó en hectáreas, "
      "equivalente a <font face='Courier'>$area / 10000</font> en la calculadora de campos.",
      "<b>Polígonos de Voronoi:</b> dividen el territorio en celdas donde cada punto está más cerca de un parque que de cualquier otro. "
      "Representan el área de influencia de cada parque.",
      "<b>Triangulación de Delaunay:</b> une a los parques vecinos con triángulos. Es el dual de Voronoi y muestra la red de vecindad "
      "y la distancia entre parques.",
      "<b>Centro de gravedad de la demanda:</b> promedio de las coordenadas de las cabeceras ponderado por su población. Es un método clásico "
      "de localización en Ingeniería Industrial.",
      "<b>Indicadores por parque:</b> distancia media a la demanda ponderada por población, distancia al centro de gravedad, población "
      "a 15 km o menos, población más cercana según Voronoi y vecinos en Delaunay.",
      "<b>Exportación web:</b> mapa interactivo en HTML (Leaflet), equivalente a la salida del complemento qgis2web."])]

S += [Paragraph("4. Resultados", h1), Paragraph("4.1 Parques y zonas industriales", h2),
  KeepTogether([img("mapa1_parques"), Paragraph("Mapa 1 – Capas vectoriales sobre el raster de la cátedra.", cap)]), Spacer(1, 6),
  P("El área de estudio tiene 18 parques y zonas industriales. Se concentran en dos ejes: el <b>Gran Mendoza</b> (corredor Rodríguez Peña, "
    "Acceso Sur y Acceso Este) y el <b>Este</b> (Palmira, San Martín, Rivadavia). Las superficies de los polígonos de la cátedra son:"),
]
pz = poly.groupby("zona")["sup_ha"].agg(["sum", "count"]).reset_index().sort_values("sum", ascending=False)
S += [tbl([[H("Zona industrial (polígonos de la cátedra)"), H("Polígonos"), H("Superficie (ha)")]] +
          [[Paragraph(r.zona, cell), Paragraph(str(r["count"]), cellc), Paragraph(f"{r['sum']:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."), cellc)] for _, r in pz.iterrows()],
          [10*cm, 2.5*cm, 3.5*cm])]

S += [KeepTogether([Paragraph("4.2 Áreas de influencia y vecindad", h2), img("mapa2_voronoi_delaunay"), Paragraph("Mapa 2 – Polígonos de Voronoi (naranja) y triangulación de Delaunay (gris).", cap)]), Spacer(1, 6),
  P(f"La triangulación genera {len(edges)} conexiones entre parques, con una longitud media de {edges.long_km.mean():.1f} km. Las celdas de Voronoi "
    "son pequeñas en el Gran Mendoza, donde hay muchos parques próximos, y muy grandes en el Este y en Lavalle, donde un solo parque cubre "
    "un territorio extenso. En términos de demanda, la celda de la <b>Zona Industrial Carril Rodríguez Peña</b> es la más cercana para "
    f"Capital, Godoy Cruz y Guaymallén ({fmt(park[park.id==8].pob_cercana.iloc[0])} habitantes). Es la de mayor demanda potencial de toda la red.")]

top10 = park.head(10)
rows = [[H("#"), H("Parque / zona"), H("Dist. media ponderada (km)"), H("Dist. al centro de gravedad (km)"), H("Población ≤ 15 km"), H("Vecinos Delaunay")]]
for _, r in park.iterrows():
    rows.append([Paragraph(str(r.ranking), cellc), Paragraph(r.nombre, cell), Paragraph(f"{r.dist_media_pond_km:.1f}".replace(".", ","), cellc),
                 Paragraph(f"{r.dist_cg_km:.1f}".replace(".", ","), cellc), Paragraph(fmt(r.pob_15km), cellc), Paragraph(str(r.vecinos_delaunay), cellc)])
S += [KeepTogether([Paragraph("4.3 Demanda y localización", h2), img("mapa3_localizacion"), Paragraph("Mapa 3 – Demanda por departamento (círculos), centro de gravedad (X) y los tres parques mejor ubicados (estrellas).", cap)]),
  Spacer(1, 6),
  P(f"El centro de gravedad de la demanda cae en <b>{abs(cg.y):.3f}° S, {abs(cg.x):.3f}° O</b>, en el límite entre Guaymallén y Maipú, dentro "
    "del propio corredor industrial de Rodríguez Peña. La tabla ordena los 18 parques según la distancia media ponderada a la demanda:"),
  tbl(rows, [0.8*cm, 6.2*cm, 2.5*cm, 2.6*cm, 2.4*cm, 2*cm], hl_rows=(1, 2, 3)),
  KeepTogether([img("mapa4_gran_mendoza"), Paragraph("Mapa 4 – Detalle del Gran Mendoza.", cap)])]

S += [Paragraph("5. Aplicación a la localización de Square Housing", h1),
  P("Para una planta de viviendas modulares, la cercanía a la demanda pesa mucho: cada vivienda o módulo viaja por ruta con un ancho máximo "
    "de 2,60 m sin permiso especial, así que el costo logístico crece con cada kilómetro. Con ese criterio, el análisis sugiere:"),
  *B(["<b>Zona Industrial Carril Rodríguez Peña (1.°):</b> la menor distancia media a la demanda (13,4 km) y a 3,3 km del centro de gravedad. "
      "Su celda de Voronoi concentra la mayor población cercana. Es un corredor industrial consolidado, de gran superficie, entre Guaymallén y Maipú.",
      "<b>Zona Alcoholera (2.°):</b> la más próxima al centro de gravedad (1,9 km), muy cerca de la primera.",
      "<b>Parque Industrial General Ortega / Zona Carril Gómez (3.°):</b> en el mismo eje, con buena conexión hacia el Este.",
      "<b>Parques del Este y de Luján</b> (Provincial, San Martín, Rivadavia): duplican o triplican la distancia media a la demanda. Solo se justificarían "
      "por otros factores, como el precio de la tierra o los incentivos."]),
  P("Por lo tanto, para la <b>macrolocalización</b> se propone el <b>corredor industrial Rodríguez Peña – General Ortega</b> en el Gran Mendoza. "
    "La elección del lote concreto (microlocalización) debe completarse en el PFE con factores que este análisis no cubre:"),
  *B(["Distancia real por la <b>red vial</b>, no en línea recta. La cátedra ofrece la capa <i>Red Vial</i> para este paso.",
      "Disponibilidad y precio de lotes, servicios (energía trifásica: capa <i>Líneas AT</i>) y zonificación municipal.",
      "Accesos aptos para camiones con carga ancha y espacio para playa de acopio de módulos.",
      "Cercanía a proveedores de acero y a mano de obra calificada en construcción en seco."]),
  Paragraph("6. Observaciones técnicas", h1),
  *B(["El raster de la cátedra y las capas vectoriales no coinciden exactamente en el Este (Rivadavia y San Martín). Esto muestra un error de "
      "georreferenciación del raster y la importancia de verificar las capas entre sí.",
      "El Parque General Ortega y la Zona Carril Gómez figuran en el CSV a solo 30 m de distancia, por lo que comparten prácticamente el mismo nodo.",
      "Las cabeceras departamentales tienen ubicación aproximada y representan a toda la población del departamento, que en la realidad está más dispersa.",
      "Las distancias son euclidianas (en línea recta) y sirven para comparar parques entre sí, no como distancias de viaje reales."]),
  Paragraph("7. Conclusión", h1),
  P("Las herramientas SIG permitieron pasar de un mapa en imagen a capas medibles: superficies en hectáreas, áreas de influencia, red de vecindad "
    "y distancias ponderadas a la demanda. Aplicadas al proyecto Square Housing, indican que la planta conviene ubicarla en el corredor industrial "
    "del Gran Mendoza (Rodríguez Peña – General Ortega), cerca del centro de gravedad de la demanda. Esto reduce el recorrido de módulos de gran "
    "tamaño y deja una base cuantitativa para la etapa de localización del PFE."),
  Paragraph("Herramientas: Python (GeoPandas, Shapely, Rasterio, Matplotlib, Folium), GeoPackage para abrir en QGIS. Asistencia de IA (Claude) en el "
            "procesamiento y la redacción, con revisión del grupo. Fuente de población: INDEC, Censo 2022.", cap)]

def footer(c, d):
    if d.page == 1: return
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#777"))
    c.drawString(2*cm, 1.2*cm, "TyHM II – Módulo 3: Sistemas de Información Geográfica – Grupo 11")
    c.drawRightString(A4[0]-2*cm, 1.2*cm, f"Página {d.page}"); c.restoreState()
doc = SimpleDocTemplate(f"{OUT}/Modulo3_SIG_Parques_Industriales_Square_Housing.pdf", pagesize=A4, leftMargin=2.2*cm, rightMargin=2.2*cm,
                        topMargin=1.8*cm, bottomMargin=2*cm, title="Módulo 3 – SIG", author="Grupo 11")
doc.build(S, onFirstPage=footer, onLaterPages=footer); print("pdf ok")
