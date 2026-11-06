# Módulo 3 – Sistemas de Información Geográfica (SIG)

## Análisis espacial de los parques industriales de Mendoza y localización preliminar de la planta Square Housing

Se trabajó sobre las capas de la cátedra (carpeta GIS: `parques_3_modificado_modificado.tif`, `COGAR`, `Uso Suelo` y `Capas_shp`) para analizar cómo se distribuyen los 18 parques y zonas industriales del oasis norte y este de Mendoza. El resultado sirve como insumo para la **etapa de localización** de nuestro Proyecto Final: una planta de viviendas modulares industrializadas.

### Mapa web interactivo
👉 **[Ver el mapa interactivo](https://santiagomarsonet.github.io/TyHM2-Entregas/Modulo%203/mapa_web/index.html)**

El mapa permite activar y desactivar capas (parques, polígonos industriales, Voronoi, Delaunay, demanda y raster de la cátedra), medir distancias y ver los indicadores de cada parque al hacer clic sobre él.

### Procedimiento
1. **Sistema de referencia:** las capas originales están en EPSG:4326 y se reproyectaron a **EPSG:32719 (WGS 84 / UTM 19S)** para medir en metros.
2. **Capa de puntos desde texto:** se cargó `locaciones2.csv` (17 parques) y se digitalizó el Parque Industrial Santa Rosa sobre el raster georreferenciado.
3. **Polígonos desde WKT:** zonas Rodríguez Peña, refinería de Luján, San Martín, Rivadavia y PASIP. La superficie se calculó en hectáreas (`$area / 10000`).
4. **Polígonos de Voronoi:** área de influencia de cada parque, recortada al área de estudio.
5. **Triangulación de Delaunay:** red de vecindad entre parques (46 conexiones).
6. **Centro de gravedad de la demanda:** ponderado por la población 2022 (INDEC) de 11 departamentos.
7. **Indicadores y ranking:** distancia media a la demanda ponderada por población, distancia al centro de gravedad y población a 15 km o menos.
8. **Exportación web:** mapa en HTML con Leaflet, equivalente a qgis2web.

### Resultado principal
El centro de gravedad de la demanda cae en el límite entre Guaymallén y Maipú. Los parques mejor ubicados para la planta son:

| # | Parque / zona | Distancia media ponderada a la demanda |
|---|---|---|
| 1 | Zona Industrial Carril Rodríguez Peña | 13,4 km |
| 2 | Zona Alcoholera | 14,1 km |
| 3 | Parque Industrial General Ortega / Zona Carril Gómez | 15,8 km |

Se propone el **corredor Rodríguez Peña – General Ortega** para la macrolocalización. La microlocalización queda pendiente de evaluar con la red vial, los lotes disponibles y los servicios.

### Contenido de la carpeta
| Archivo | Descripción |
|---|---|
| `Modulo3_SIG_Parques_Industriales_Square_Housing.pdf` | Informe completo (7 páginas) con mapas, tablas y conclusiones |
| `mapa_web/index.html` | Mapa web interactivo |
| `datos/Modulo3_SIG_SquareHousing.gpkg` | GeoPackage con todas las capas generadas, para abrir en QGIS |
| `datos/ranking_parques.csv` | Indicadores y ranking de los 18 parques |
| `mapas/` | Mapas en PNG |
| `scripts/` | Código Python del análisis (GeoPandas, Shapely, Rasterio, Folium) |
| `Analisis_artistico_Patio_de_los_Arrayanes_La_Alhambra.pdf` | Complemento: análisis artístico de una fotografía (ver abajo) |

**Para abrir en QGIS:** arrastrar el `.gpkg` a QGIS. Aparecen las capas `parques_industriales`, `poligonos_industriales`, `voronoi`, `delaunay`, `demanda_cabeceras`, `centro_gravedad` y `area_estudio`.

### Complemento: análisis artístico de una fotografía
📄 **[Análisis artístico – Patio de los Arrayanes, La Alhambra](Analisis_artistico_Patio_de_los_Arrayanes_La_Alhambra.pdf)**

Análisis de una fotografía del Patio de los Arrayanes, en el Palacio de Comares de la Alhambra (Granada). Incluye:
- **Descripción de la imagen:** estanque, fuente, cercos de arrayanes, galería de siete arcos y Torre de Comares.
- **Análisis formal:** simetría, composición centrada, perspectiva, planos de profundidad, luz, color, formas y texturas.
- **La cultura musulmana en el patio:** el patio como centro, el agua como imagen del paraíso, la naturaleza ordenada, la decoración geométrica sin figuras, la liviandad de arcos y columnas, y la torre como símbolo de poder.
- **Interpretación y conclusión:** la sensación de calma, orden y permanencia, y por qué se eligió esta foto como ejemplo de la arquitectura nazarí.

## Integrantes – Grupo 11
| Apellido y nombre | Legajo |
|---|---|
| Marsonet, Santiago | 14131 |
| Royo, Santiago | 14141 |
| Gimenez, Lisandro | 14122 |
| Bordon, Joaquín | 14104 |
