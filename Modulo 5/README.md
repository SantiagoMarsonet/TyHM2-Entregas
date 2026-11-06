# Módulo 5 – Dinámica de Sistemas: *The Beer Game*

## Simulación del Juego de la Cerveza en Vensim y análisis del efecto látigo en la cadena de suministro

Se trabajó con el modelo `Beer_Game.mdl` de Vensim. Reproduce el *Beer Distribution Game* desarrollado en el MIT por el grupo de Jay W. Forrester y popularizado por John Sterman. El informe se armó en **R Markdown** y explica de qué se trata el juego, cómo se juega y la teoría básica de la gestión de la cadena de suministro. También analiza los resultados de la simulación.

### El juego
Es una cadena de suministro de cerveza con **cuatro eslabones**: minorista, mayorista, distribuidor y fábrica. Cada jugador ve solo su inventario y los pedidos de su cliente inmediato, y cada semana decide **cuánto pedirle a su proveedor**.

- Los pedidos tardan 1 semana en llegar al proveedor y los envíos tardan 2 semanas.
- Cada caja en stock cuesta $0,50 por semana y cada caja pendiente (backlog) cuesta $1,00 por semana.
- La demanda del consumidor pasa una sola vez de **4 a 8 cajas/semana** en la semana 5.

### El modelo
Cada eslabón tiene tres stocks: inventario, backlog y línea de suministro (pedidos en tránsito). La decisión de pedido sigue la regla de **anclaje y ajuste** de Sterman (1989):

> pedido = demanda esperada + A · (12 − inventario efectivo − B · línea de suministro)

Los parámetros son `A = 0,25` (velocidad de corrección) y `B = 0,33` (peso que se le da a lo ya pedido). El horizonte es de 36 semanas.

### Resultados principales
- **Efecto látigo:** la demanda solo se duplica (de 4 a 8), pero los pedidos máximos crecen al subir por la cadena: minorista 10,6 → mayorista 16 → distribuidor 24 → **fábrica 30 cajas/semana**.
- Primero todos los eslabones se quedan sin stock y después terminan con mucho sobrestock: la fábrica llega a unas **70 cajas** cuando el objetivo es 12.
- El **costo total** de la cadena en 36 semanas es de **$2.250**, y el distribuidor y la fábrica generan la mayor parte.
- **Análisis de sensibilidad:** si los jugadores tienen en cuenta todo lo que ya pidieron (`B = 1`), las oscilaciones casi desaparecen y el costo baja a unos **$580**. La causa del problema es la regla de decisión, no la demanda.

### Contenido de la carpeta
| Archivo | Descripción |
|---|---|
| `Modulo5_Beer_Game.zip` | Entrega completa (contiene los archivos de abajo) |
| ↳ `Informe_Beer_Game.html` | Informe final. Se abre con cualquier navegador |
| ↳ `Informe_Beer_Game.Rmd` | Código fuente del informe en R Markdown |
| ↳ `Beer_Game.mdl` | Modelo de Vensim |
| ↳ `resultados_vensim_mdl.csv` | Resultados de la corrida del modelo, usados en la validación del informe |

**Para regenerar el informe:** abrir `Informe_Beer_Game.Rmd` en RStudio o Posit Cloud, con el `.csv` en la misma carpeta, y apretar **Knit**. Requiere los paquetes `rmarkdown`, `knitr` y `ggplot2`.

## Integrantes – Grupo 11
| Apellido y nombre | Legajo |
|---|---|
| Marsonet, Santiago | 14131 |
| Royo, Santiago | 14141 |
| Gimenez, Lisandro | 14122 |
| Bordon, Joaquín | 14104 |
