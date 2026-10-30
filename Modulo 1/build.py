import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image, KeepTogether)

OUT = "/tmp/m1/Modulo1_Toma_de_Decisiones_Marsonet.pdf"

# ---------------- Datos de la decisión ----------------
alts = [
    ("A", "Viviendas modulares industrializadas (Square Housing)"),
    ("B", "Planta de valorización de orujo vitivinícola y olivícola"),
    ("C", "Segunda vida de baterías de litio para almacenamiento en fincas"),
    ("D", "Servicio de mantenimiento predictivo con IoT e IA para la agroindustria"),
]
crit = [
    ("C1", "Relevancia e impacto socioeconómico regional", 0.20),
    ("C2", "Factibilidad de completarlo en el plazo del PFE", 0.20),
    ("C3", "Acceso a información, asesores y referentes", 0.15),
    ("C4", "Integración de contenidos de la carrera", 0.15),
    ("C5", "Potencial de mercado e innovación", 0.15),
    ("C6", "Nivel de riesgo e incertidumbre (5 = bajo riesgo)", 0.10),
    ("C7", "Motivación y afinidad del equipo", 0.05),
]
scores = {
    "A": [5, 5, 4, 5, 4, 2, 5],
    "B": [4, 3, 3, 4, 3, 3, 3],
    "C": [4, 2, 2, 4, 5, 2, 4],
    "D": [3, 3, 3, 3, 4, 4, 4],
}
w = [c[2] for c in crit]
assert abs(sum(w) - 1) < 1e-9

def total(weights):
    return {k: sum(a * b for a, b in zip(v, weights)) for k, v in scores.items()}

base = total(w)

# Escenarios de sensibilidad
def norm(x):
    s = sum(x); return [i / s for i in x]
escenarios = [
    ("Base (pesos propuestos)", w),
    ("Pesos iguales", [1/7]*7),
    ("Aversión al riesgo (C6 = 30 %)", norm([0.15, 0.15, 0.10, 0.10, 0.10, 0.30, 0.10])),
    ("Foco en innovación (C5 = 35 %)", norm([0.15, 0.15, 0.10, 0.10, 0.35, 0.10, 0.05])),
    ("Sin ventaja de avance previo (C2 = 5 %)", norm([0.25, 0.05, 0.15, 0.20, 0.20, 0.10, 0.05])),
]
sens = [(n, total(x)) for n, x in escenarios]

# Umbral de peso del riesgo para que A deje de ser la mejor
def ranking_with_risk(p):
    rest = [wi for i, wi in enumerate(w) if i != 5]
    s = sum(rest)
    ww = [wi / s * (1 - p) for wi in rest]
    ww.insert(5, p)
    return total(ww)
umbral = None
for i in range(0, 101):
    p = i / 100
    t = ranking_with_risk(p)
    best = max(t, key=t.get)
    if best != "A":
        umbral = (p, best); break

# ---------------- Gráficos ----------------
pal = {"A": "#1f4e79", "B": "#8faadc", "C": "#a9a9a9", "D": "#c9c9c9"}
fig, ax = plt.subplots(figsize=(7, 3.0), dpi=200)
ks = list(base.keys())
vals = [base[k] for k in ks]
short={"A":"A. Viviendas modulares","B":"B. Valorización de orujo","C":"C. Baterías de segunda vida","D":"D. Mantenimiento predictivo IA"}
bars = ax.barh([short[k] for k in ks][::-1],
               vals[::-1], color=[pal[k] for k in ks][::-1])
for b, v in zip(bars, vals[::-1]):
    ax.text(v + 0.04, b.get_y() + b.get_height()/2, f"{v:.2f}", va="center", fontsize=8)
ax.set_xlim(0, 5); ax.set_xlabel("Puntaje ponderado (escala 1 a 5)", fontsize=8)
ax.tick_params(labelsize=7.5)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("/tmp/m1/g_total.png"); plt.close()

fig, ax = plt.subplots(figsize=(7, 3.4), dpi=200)
ps = [i/100 for i in range(0, 101, 2)]
for k in ks:
    ax.plot([p*100 for p in ps], [ranking_with_risk(p)[k] for p in ps], color=pal[k],
            lw=2.2 if k == "A" else 1.4, label=f"Alternativa {k}")
ax.axvline(10, ls="--", color="#666", lw=0.8); ax.text(11, 4.75, "peso base", fontsize=7, color="#444")
if umbral:
    ax.axvline(umbral[0]*100, ls=":", color="#b00", lw=0.9)
    ax.text(umbral[0]*100 + 1, 2.2, f"A pierde el 1.º lugar\n(riesgo ≥ {umbral[0]*100:.0f} %)", fontsize=7, color="#b00")
ax.set_xlabel("Peso asignado al criterio C6 – Riesgo (%)", fontsize=8)
ax.set_ylabel("Puntaje ponderado", fontsize=8)
ax.tick_params(labelsize=7.5); ax.legend(fontsize=7, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.28))
for s in ["top", "right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("/tmp/m1/g_sens.png"); plt.close()

# ---------------- PDF ----------------
ss = getSampleStyleSheet()
AZ = colors.HexColor("#1f4e79")
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, textColor=AZ, spaceBefore=10, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12, textColor=AZ, spaceBefore=8, spaceAfter=4)
bul = ParagraphStyle("bul", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=3)
cell = ParagraphStyle("c", parent=body, fontSize=8.8, leading=11, alignment=0, spaceAfter=0)
cellc = ParagraphStyle("cc", parent=cell, alignment=TA_CENTER)
cap = ParagraphStyle("cap", parent=body, fontSize=8.5, textColor=colors.HexColor("#555"), alignment=TA_CENTER)

def P(t): return Paragraph(t, body)
def B(items): return [Paragraph(i, bul, bulletText="•") for i in items]
def tbl(data, widths, header=True, zebra=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#b0b0b0")),
          ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]
    if header:
        st += [("BACKGROUND", (0,0), (-1,0), AZ), ("TEXTCOLOR", (0,0), (-1,0), colors.white)]
    if zebra:
        for r in range(1, len(data)):
            if r % 2 == 0: st.append(("BACKGROUND", (0,r), (-1,r), colors.HexColor("#eef3f9")))
    t.setStyle(TableStyle(st)); return t
def H(t): return Paragraph(f"<font color='white'><b>{t}</b></font>", cellc)

story = []
# Portada
story += [Spacer(1, 3*cm),
          Paragraph("Universidad Nacional de Cuyo – Facultad de Ingeniería", ParagraphStyle("p", parent=body, alignment=TA_CENTER)),
          Paragraph("Ingeniería Industrial", ParagraphStyle("p", parent=body, alignment=TA_CENTER)),
          Spacer(1, 1.2*cm),
          Paragraph("Técnicas y Herramientas Modernas II", ParagraphStyle("t0", parent=h2, alignment=TA_CENTER, fontSize=14)),
          Spacer(1, 0.4*cm),
          Paragraph("Módulo 1 – Toma de Decisiones", ParagraphStyle("t1", parent=h1, alignment=TA_CENTER, fontSize=22, leading=28)),
          Spacer(1, 0.3*cm),
          Paragraph("Elección del tema del Proyecto Final de Estudios mediante una matriz de decisión multicriterio",
                    ParagraphStyle("t2", parent=body, alignment=TA_CENTER, fontSize=13, leading=18)),
          Spacer(1, 2.2*cm),
          Paragraph("<b>Integrantes – Grupo 11</b>", ParagraphStyle("p", parent=body, alignment=TA_CENTER)),
          Spacer(1, 0.2*cm),
          tbl([[H("Apellido y nombre"), H("Legajo")],
               [Paragraph("Marsonet, Santiago", cell), Paragraph("14131", cellc)],
               [Paragraph("Royo, Santiago", cell), Paragraph("14141", cellc)],
               [Paragraph("Gimenez, Lisandro", cell), Paragraph("14122", cellc)],
               [Paragraph("Bordon, Joaquín", cell), Paragraph("14104", cellc)]],
              [6*cm, 3*cm]),
          Spacer(1, 1.2*cm),
          Paragraph("Segundo semestre 2026 – Mendoza, Argentina", ParagraphStyle("p", parent=body, alignment=TA_CENTER)),
          PageBreak()]

# 1
story += [Paragraph("1. Introducción", h1),
  P("Elegir el tema del Proyecto Final de Estudios (PFE) es una de las decisiones más importantes del último año de la carrera. "
    "Condiciona el trabajo de todo un año, los contactos que se construyen, la información a la que se tiene acceso y, en buena medida, "
    "el perfil profesional con el que el alumno egresa. Por eso conviene tomarla de forma estructurada y no solo por intuición."),
  P("En este trabajo se aplica un proceso formal de toma de decisiones para elegir el tema del PFE del Grupo 11. Se plantean cuatro "
    "alternativas: el tema finalmente elegido (viviendas modulares industrializadas) y tres alternativas de temas actuales de la "
    "Ingeniería Industrial con anclaje en Mendoza. Las alternativas se comparan mediante una matriz de decisión ponderada (método de "
    "suma ponderada) y luego se verifica la robustez del resultado con un análisis de sensibilidad sobre los pesos de los criterios."),
  Paragraph("1.1 Proceso de decisión aplicado", h2),
  P("Se siguieron las etapas clásicas del proceso racional de decisión:"),
  *B(["<b>Definición del problema:</b> qué se decide, quién decide y con qué restricciones.",
      "<b>Generación de alternativas:</b> temas viables para un estudio de prefactibilidad.",
      "<b>Definición de criterios y ponderación:</b> qué importa y cuánto.",
      "<b>Evaluación:</b> puntuación de cada alternativa en cada criterio (escala 1 a 5).",
      "<b>Elección y análisis de sensibilidad:</b> se verifica si la decisión cambia al variar los pesos.",
      "<b>Justificación:</b> argumentos cualitativos que respaldan la elección y riesgos que se asumen."]),
]

# 2
story += [Paragraph("2. Definición del problema de decisión", h1),
  tbl([[H("Elemento"), H("Descripción")],
       [Paragraph("<b>Decisión</b>", cell), Paragraph("Qué tema desarrollar como Proyecto Final de Estudios de Ingeniería Industrial.", cell)],
       [Paragraph("<b>Decisor</b>", cell), Paragraph("Grupo 11, con validación de la cátedra de Proyecto Final.", cell)],
       [Paragraph("<b>Objetivo</b>", cell), Paragraph("Elegir un tema que resuelva una necesidad regional real, que pueda completarse con calidad en el plazo disponible y que integre los contenidos de la carrera.", cell)],
       [Paragraph("<b>Formato exigido</b>", cell), Paragraph("Estudio de prefactibilidad según la guía de la cátedra: comercialización, ingeniería del proyecto, tamaño y localización, organización, estudio económico-financiero (VAN, TIR) y análisis de sensibilidad.", cell)],
       [Paragraph("<b>Restricciones</b>", cell), Paragraph("Un ciclo lectivo de plazo; información accesible para estudiantes; problema definido sobre necesidades sociales regionales; ámbito Mendoza.", cell)],
       [Paragraph("<b>Tipo de decisión</b>", cell), Paragraph("No programada, estratégica para el grupo, multicriterio y bajo incertidumbre (normativa, mercado, datos).", cell)],
      ], [4*cm, 12.5*cm]),
]

# 3 Alternativas
story += [PageBreak(), Paragraph("3. Alternativas consideradas", h1),
  P("Además del tema elegido, se plantean tres alternativas que representan líneas de trabajo actuales para la Ingeniería Industrial: "
    "economía circular, transición energética y digitalización (Industria 4.0). Las tres tienen un anclaje concreto en la economía mendocina, "
    "para que la comparación sea justa."),

  Paragraph("Alternativa A – Viviendas modulares industrializadas (Square Housing)", h2),
  P("Estudio de prefactibilidad de una planta de fabricación de viviendas modulares en Mendoza, con sistema constructivo en seco "
    "(steel frame, evaluando un híbrido con paneles SIP). El producto es una vivienda básica (cocina-estar, dormitorio y baño) ampliable por "
    "módulos y con un sistema de <i>upgrades</i> habitacionales: eficiencia térmica, preparación para paneles solares, domótica, home office. "
    "Apunta a jóvenes adultos de 25 a 40 años que no logran acceder a su primera vivienda por el costo inicial, la falta de previsibilidad "
    "de la obra tradicional (18 a 30 meses, presupuestos abiertos) y el desgaste de autogestionar la construcción."),

  Paragraph("Alternativa B – Planta de valorización de orujo vitivinícola y olivícola", h2),
  P("Mendoza genera cada vendimia grandes volúmenes de orujo (hollejos, semillas y escobajo), y la industria olivícola genera alperujo. Hoy gran parte "
    "se destina a destilerías o se dispone con bajo valor agregado. La propuesta es una planta que separe la semilla de uva para extraer aceite "
    "de pepita, aproveche hollejos para harinas o extractos ricos en polifenoles, y convierta el remanente en pellets de biomasa para calderas "
    "industriales. Es un proyecto típico de <b>economía circular</b>: transforma un residuo en varios productos y reduce el impacto ambiental de bodegas y almazaras."),

  Paragraph("Alternativa C – Segunda vida de baterías de litio para almacenamiento en fincas", h2),
  P("Con el crecimiento de la electromovilidad empiezan a salir de servicio baterías de vehículos eléctricos que todavía conservan buena parte de "
    "su capacidad. La propuesta es una planta que reciba, diagnostique, reacondicione y reensamble esos módulos en bancos de almacenamiento "
    "para fincas y agroindustrias con paneles solares, que hoy sufren cortes de energía y altos costos de bombeo para riego. Conecta con la "
    "<b>transición energética</b>, la cadena de valor del litio en Argentina y la generación distribuida."),

  Paragraph("Alternativa D – Mantenimiento predictivo con IoT e IA para la agroindustria", h2),
  P("Empresa de servicios que instala sensores de bajo costo (vibración, temperatura, consumo eléctrico) en equipos críticos de bodegas, "
    "almazaras y empacadoras (bombas, prensas, centrífugas, cámaras de frío) y usa modelos de inteligencia artificial para anticipar fallas. Se "
    "comercializa como suscripción mensual para PyMEs que no tienen un área de mantenimiento propia. Es un tema de <b>Industria 4.0</b> con "
    "inversión inicial baja, que aprovecha la estacionalidad crítica de la cosecha, cuando una parada no programada es más costosa."),
]

# 4 Criterios
story += [PageBreak(), Paragraph("4. Criterios de decisión y ponderación", h1),
  P("Los criterios surgen de lo que pide la guía de la cátedra (necesidad regional, integración de la carrera, evaluación económica) y de lo "
    "que el grupo considera determinante para terminar un buen trabajo en el plazo disponible. Los pesos se asignaron por consenso, "
    "priorizando la relevancia regional y la factibilidad de concluir el proyecto."),
  tbl([[H("Cód."), H("Criterio"), H("Qué mide"), H("Peso")]] + [
      [Paragraph(c, cellc), Paragraph(f"<b>{n}</b>", cell), Paragraph(d, cell), Paragraph(f"{p*100:.0f} %", cellc)]
      for (c, n, p), d in zip(crit, [
        "Magnitud de la necesidad que resuelve en Mendoza y su aporte a la economía local.",
        "Posibilidad de llegar a un estudio de prefactibilidad completo en un ciclo lectivo (avance previo, alcance acotable).",
        "Disponibilidad de datos públicos, expertos, empresas y organismos dispuestos a colaborar.",
        "Cuántas áreas de la carrera permite aplicar: comercialización, procesos, layout, calidad, localización, organización, finanzas.",
        "Tamaño del mercado, diferenciación frente a la competencia y grado de innovación de la propuesta.",
        "Exposición a factores externos que pueden frenar el proyecto: normativa, tecnología, financiamiento.",
        "Interés del grupo en el tema y vínculo con sus valores: innovación, emprendedurismo, compromiso social."])
  ] + [[Paragraph("", cell), Paragraph("<b>Total</b>", cell), Paragraph("", cell), Paragraph("<b>100 %</b>", cellc)]],
      [1.2*cm, 5*cm, 8.6*cm, 1.7*cm]),
  Spacer(1, 6),
  P("Escala de puntuación: 1 = muy desfavorable, 2 = desfavorable, 3 = neutro, 4 = favorable, 5 = muy favorable. En el criterio C6 la "
    "escala está invertida respecto del riesgo: 5 significa riesgo bajo."),
]

# 5 Matriz
hdr = [H("Criterio"), H("Peso")] + [H(k) for k in ks]
rows = []
for i, (c, n, p) in enumerate(crit):
    rows.append([Paragraph(f"{c} – {n}", cell), Paragraph(f"{p:.2f}", cellc)] +
                [Paragraph(f"{scores[k][i]}  <font size=7 color='#555'>({scores[k][i]*p:.2f})</font>", cellc) for k in ks])
rows.append([Paragraph("<b>Puntaje ponderado total</b>", cell), Paragraph("<b>1.00</b>", cellc)] +
            [Paragraph(f"<b>{base[k]:.2f}</b>", cellc) for k in ks])
rank = sorted(ks, key=lambda k: -base[k])
rows.append([Paragraph("<b>Ranking</b>", cell), Paragraph("", cellc)] + [Paragraph(f"<b>{rank.index(k)+1}.º</b>", cellc) for k in ks])
mt = tbl([hdr] + rows, [6.6*cm, 1.4*cm, 2.15*cm, 2.15*cm, 2.15*cm, 2.15*cm])
mt.setStyle(TableStyle([("BACKGROUND", (2, len(rows)-1), (2, len(rows)), colors.HexColor("#d6e4f2"))]))

story += [Paragraph("5. Matriz de decisión ponderada", h1),
  P("Cada celda muestra el puntaje asignado (1 a 5) y, entre paréntesis, su valor ponderado (puntaje × peso). El total de cada alternativa "
    "es la suma de sus valores ponderados."),
  mt, Spacer(1, 10),
  Image("/tmp/m1/g_total.png", width=16*cm, height=16*3.0/7*cm),
  Paragraph("Figura 1 – Puntaje ponderado total por alternativa.", cap),
  Paragraph("5.1 Fundamento de los puntajes", h2),
  *B([
    "<b>A – Viviendas modulares:</b> obtiene el máximo en relevancia (déficit habitacional de más de 100.000 personas en Mendoza y vuelta del crédito hipotecario), en factibilidad (la etapa de comercialización ya fue desarrollada en la materia Comercialización y sirve de base) y en integración de la carrera. Su punto débil es el riesgo (2): la aprobación municipal de módulos armados en planta, la homologación para crédito y una normativa provincial todavía en trámite.",
    "<b>B – Orujo:</b> buen impacto ambiental y regional, con una ingeniería de procesos rica. Pierde puntos por factibilidad e información: requiere ensayos de laboratorio sobre rendimientos y caracterización del residuo, y el grupo no tiene contacto previo con bodegas o destilerías.",
    "<b>C – Baterías de segunda vida:</b> es la más innovadora (5 en C5), pero también la más difícil de completar. Todavía hay poco volumen de baterías en desuso en el país, falta normativa específica y el diagnóstico de celdas exige conocimientos de ingeniería eléctrica que exceden el perfil del grupo.",
    "<b>D – Mantenimiento predictivo:</b> es la de menor riesgo (inversión baja, tecnología disponible), pero su componente central es de software y ciencia de datos. Integra menos áreas de la Ingeniería Industrial (no hay planta, layout ni localización relevantes) y su impacto social es más acotado.",
  ]),
]

# 6 Sensibilidad
sh = [H("Escenario de pesos")] + [H(k) for k in ks] + [H("Mejor")]
sr = []
for n, t in sens:
    best = max(t, key=t.get)
    sr.append([Paragraph(n, cell)] + [Paragraph(("<b>%.2f</b>" if k == best else "%.2f") % t[k], cellc) for k in ks] + [Paragraph(f"<b>{best}</b>", cellc)])
story += [PageBreak(), Paragraph("6. Análisis de sensibilidad", h1),
  P("Los pesos de los criterios son la parte más subjetiva del método. Para verificar que la elección no depende de una ponderación "
    "particular, se recalculó el ranking con escenarios alternativos:"),
  tbl([sh] + sr, [6.9*cm, 1.9*cm, 1.9*cm, 1.9*cm, 1.9*cm, 2.0*cm]), Spacer(1, 8),
  P("La alternativa A se mantiene en primer lugar en todos los escenarios, incluso cuando se elimina casi toda su ventaja por avance previo "
    "(C2 al 5 %) o cuando se privilegia la innovación, que es el punto fuerte de las alternativas C y D."),
  P("Como el riesgo es el único criterio en el que A puntúa mal, se analizó en detalle cuánto peso debería tener para cambiar la decisión. "
    "El peso de C6 se varió de 0 % a 100 %, repartiendo el resto en forma proporcional a los pesos base:"),
  Image("/tmp/m1/g_sens.png", width=16*cm, height=16*3.4/7*cm),
  Paragraph("Figura 2 – Sensibilidad del puntaje al peso del criterio de riesgo.", cap),
  P(f"La alternativa A deja de ser la preferida recién cuando el riesgo pesa {umbral[0]*100:.0f} % o más de la decisión, y en ese caso la "
    f"elegida pasaría a ser la alternativa {umbral[1]}. Ese escenario implicaría valorar la seguridad del proyecto por encima de su relevancia, "
    "factibilidad e integración de la carrera juntas, lo que no se corresponde con el objetivo de un PFE. Se concluye que <b>la decisión es robusta</b>."
    if umbral else "La alternativa A se mantiene primera para cualquier peso del riesgo."),
]

# 7 Justificación
story += [Paragraph("7. Justificación de la elección", h1),
  P("El grupo eligió desarrollar el <b>estudio de prefactibilidad de una planta de viviendas modulares industrializadas en Mendoza</b>. "
    "Además del resultado cuantitativo, la decisión se apoya en los siguientes argumentos:"),
  Paragraph("7.1 Responde a una necesidad social concreta y regional", h2),
  P("El acceso a la primera vivienda es uno de los problemas más sentidos por los jóvenes adultos. En la encuesta realizada por el grupo, todos "
    "los encuestados de 25 a 40 años sin vivienda propia manifestaron que comprarían o construirían si pudieran, y señalaron como limitantes "
    "el precio, la falta de financiamiento y la inestabilidad económica. La guía de la cátedra pide justamente definir el problema sobre "
    "necesidades sociales regionales para que el proyecto pueda ser motor de la economía local."),
  Paragraph("7.2 El contexto actual abre una ventana de oportunidad", h2),
  *B(["La inflación anual bajó de 117,8 % (2024) a 31,5 % (2025) y el crédito al sector privado se duplicó entre 2023 y 2025; en 2025 se sumaron unos 43.700 nuevos deudores hipotecarios.",
      "La construcción en seco e industrializada está en crecimiento, y el IPV Mendoza ya ejecuta parte de sus viviendas con sistemas industrializados.",
      "El Código Unificado de Edificación de Mendoza, enviado a la Legislatura en mayo de 2026, puede ordenar y facilitar este tipo de construcción.",
      "Las obras sin permiso equivalen a cerca del 30 % de la superficie autorizada en la provincia (DEIE), lo que en zona sísmica 4 es un problema de seguridad. Una vivienda fabricada y controlada en planta es una alternativa a la informalidad."]),
  Paragraph("7.3 Existe un hueco de mercado", h2),
  P("Los competidores locales relevados ofrecen viviendas terminadas y estáticas o apuntan al turismo de alta gama. No se identificó una oferta "
    "orientada a la vivienda familiar de clase media con un modelo <b>ampliable por módulos</b>, que permita entrar con una inversión baja y "
    "crecer junto con la familia. Esto también genera ingresos posteriores a la venta para la empresa (ampliaciones y upgrades)."),
  Paragraph("7.4 Parte de una base de trabajo avanzada", h2),
  P("La idea nació en la materia Comercialización del semestre anterior, donde ya se desarrollaron la definición del negocio, el diagnóstico "
    "(Círculo Dorado, PESTEL), el Canvas, el análisis de competidores y la validación con encuestas y entrevistas. Esa etapa es la base del "
    "PFE, lo que permite dedicar más tiempo a la ingeniería del proyecto y al estudio económico-financiero."),
  Paragraph("7.5 Integra la Ingeniería Industrial de punta a punta", h2),
  P("El tema exige aplicar casi todas las áreas de la carrera: estudio de mercado y proyección de demanda, selección del sistema constructivo "
    "por matriz multicriterio, diseño del proceso productivo y del layout de planta, control de calidad y protocolo de inspección en fábrica, "
    "localización, logística de transporte (límite de 2,60 m de ancho sin permiso), organización y evaluación económico-financiera con VAN, TIR "
    "y sensibilidad. Las otras alternativas cubren estas áreas solo en forma parcial."),
  Paragraph("7.6 Hay acceso a referentes del sector", h2),
  P("El grupo cuenta con el asesoramiento técnico de un ingeniero civil (estructuras, fundaciones y transporte), entrevistó a un desarrollador "
    "inmobiliario, mantuvo reuniones con la Municipalidad de Guaymallén y con un proveedor de paneles, y dispone de abundante información "
    "pública sobre normativa y crédito. Ninguna de las otras alternativas tenía un nivel de acceso comparable."),
  Paragraph("7.7 Aporta valor ambiental y cultural", h2),
  P("La fabricación en ambiente controlado reduce residuos de obra, mejora la aislación térmica y permite reutilizar la estructura al final de "
    "su vida útil. Además, el proyecto cuestiona el modelo de la casa de ladrillo \"para toda la vida\" y propone un hogar flexible, en línea "
    "con cómo las nuevas generaciones toman sus decisiones de largo plazo."),
]

# 8 Riesgos
rk = [
 ("Aprobación municipal de módulos armados en planta", "Alta", "Evaluar entrega desarmada o híbrida (núcleo húmedo armado + paneles en el lote); proponer un protocolo de fabricación e inspección en planta."),
 ("Acceso del cliente al crédito hipotecario", "Alta", "Usar steel frame, considerado sistema tradicional (Res. 5-E/2018), calculado con CIRSOC 303 e INPRES-CIRSOC 103: no requiere CAT."),
 ("Resistencia cultural a la construcción en seco", "Media", "Casas de exhibición, garantías y comunicación de prestaciones térmicas y sísmicas."),
 ("Costos fijos de planta y precio del acero", "Media", "Análisis de sensibilidad en la etapa financiera; tamaño de planta escalonado."),
 ("Datos de demanda débiles", "Media", "Rehacer la proyección con entrevistas por perfil de cliente y benchmark de empresas de CACMI."),
]
story += [Paragraph("8. Riesgos asumidos y cómo se abordan", h1),
  P("La matriz muestra que el tema elegido es el de mayor riesgo relativo. El grupo lo asume de forma consciente, porque los riesgos son "
    "conocidos y forman parte del propio análisis de prefactibilidad:"),
  tbl([[H("Riesgo"), H("Nivel"), H("Respuesta prevista")]] +
      [[Paragraph(a, cell), Paragraph(b, cellc), Paragraph(c, cell)] for a, b, c in rk],
      [5.2*cm, 1.6*cm, 9.7*cm]),
  Spacer(1, 6),
  P("Si la vía habitacional resultara inviable, el proyecto conserva una salida: los módulos para el sector minero (por ejemplo, campamentos "
    "del proyecto PSJ Cobre Mendocino), donde no se requiere crédito hipotecario ni aprobación municipal de vivienda."),
]

# 9 Conclusión
story += [Paragraph("9. Conclusión", h1),
  P(f"Con la matriz de decisión ponderada, la alternativa A – Viviendas modulares industrializadas obtuvo {base['A']:.2f} puntos sobre 5, "
    f"con una ventaja de {base['A'] - sorted(base.values())[-2]:.2f} puntos sobre la segunda opción. El análisis de sensibilidad mostró que el "
    "resultado se mantiene ante cambios razonables en los pesos, y que solo cambiaría si el riesgo dominara la decisión."),
  P("La elección combina un problema social real y vigente, una oportunidad de mercado concreta, una base de trabajo ya validada y un tema que "
    "integra la Ingeniería Industrial de punta a punta. El principal riesgo, el marco normativo y de financiamiento, se incorpora como parte "
    "del estudio en lugar de ignorarse."),
  Paragraph("Herramientas utilizadas", h2),
  P("Matriz de decisión ponderada (método de suma ponderada), análisis de sensibilidad de pesos, Python (matplotlib y reportlab) para los "
    "cálculos y gráficos, e inteligencia artificial (Claude) como asistente para generar alternativas y redactar el documento, con revisión del alumno."),
]

def footer(c, d):
    if d.page == 1: return
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#777"))
    c.drawString(2*cm, 1.2*cm, "TyHM II – Módulo 1: Toma de Decisiones – Grupo 11")
    c.drawRightString(A4[0]-2*cm, 1.2*cm, f"Página {d.page}")
    c.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2*cm, bottomMargin=2*cm,
                        title="Módulo 1 – Toma de Decisiones", author="Marsonet, Royo, Gimenez, Bordon – Grupo 11")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(base, umbral)
for n, t in sens: print(n, {k: round(v, 2) for k, v in t.items()})
