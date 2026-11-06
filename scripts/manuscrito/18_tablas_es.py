# -*- coding: utf-8 -*-
"""
tablas_es.py — los nueve cuadros del manuscrito, en español
============================================================
Lee los mismos resultados congelados que tablas.py, de modo que ningún número
puede diferir entre la versión en inglés y la versión en español. Sólo cambian
los encabezados y las notas.
"""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import json
import pandas as pd

SAL = _r.SAL
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
T = {}

n = lambda x, d=4: f"{x:+.{d}f}"
par = lambda x, d=4: f"({x:.{d}f})"

ES = {  # las etiquetas de fila se traducen una sola vez
    "Origin rank (household assets at 14)": "Rango de origen (activos a los 14)",
    "Destination rank (household assets at survey)": "Rango de destino (activos hoy)",
    "Destination rank (years of schooling)": "Rango de destino (años de escolaridad)",
    "Years of schooling, respondent": "Años de escolaridad del encuestado",
    "Years of schooling, most educated parent": "Años de escolaridad del padre más educado",
    "Violence intensity of state (2007-2017 index)": "Intensidad de violencia de la entidad",
    "Share of formative window after 2007": "Fracción de la ventana posterior a 2007",
    "Dose (intensity x window share)": "Dosis (intensidad × fracción)",
    "Female": "Mujer",
    "Rural origin (locality < 2,500)": "Origen rural (localidad < 2 500)",
    "Co-resides with parents": "Correside con sus padres",
    "(1) Baseline": "(1) Especificación principal",
    "(2) Excluding co-residents": "(2) Excluyendo corresidentes",
    "(3) Including inter-state migrants": "(3) Incluyendo migrantes entre entidades",
    "(4) Dose from intentional homicide only": "(4) Dosis sólo con homicidio doloso",
    "(5) Clustering by birth year instead of state": "(5) Agrupando por año de nacimiento",
    "(1) No controls": "(1) Sin ningún control",
    "(2) + state and birth-year fixed effects": "(2) + efectos fijos de entidad y nacimiento",
    "(3) + state x origin rank": "(3) + entidad × rango de origen",
    "(4) + birth-year x origin rank (full model)": "(4) + nacimiento × rango (modelo final)",
    "(1) Within-state dose from counts": "(1) Dosis intraestatal con conteos",
    "(2) Within-state dose from rate": "(2) Dosis intraestatal con tasa por 100 000",
    "(3) Rate + locality size x rank": "(3) Tasa + tamaño de localidad × rango",
    "(4) Rate, clustered by state": "(4) Tasa, errores agrupados por entidad",
    "Women": "Mujeres", "Men": "Hombres",
    "Rural origin": "Origen rural", "Urban origin": "Origen urbano",
    "Origin in Q1-Q2": "Origen en Q1 y Q2", "Origin in Q4-Q5": "Origen en Q4 y Q5",
    "Years of schooling": "Años de escolaridad",
    "Destination asset index (level)": "Índice de activos de destino (nivel)",
    "Inter-state migration": "Migración entre entidades",
    "Calendario común 2007 (original)": "Calendario común de 2007 (original)",
    "Refechada por conglomerado": "Refechada por conglomerado",
    "Refechada por entidad": "Refechada por entidad",
}
tr = lambda s: ES.get(s, s)

# ------------------------------------------------------------------ Cuadro 1
d1 = pd.read_csv(f"{SAL}/t1_descriptivas.csv")
T["t1"] = {"num": 1, "titulo": "Estadísticas descriptivas",
    "cols": ["Variable", "Media", "D.E.", "Expuestos", "No expuestos", "Dif.", "n"],
    "anchos": [36, 10, 10, 11, 12, 11, 10],
    "filas": [[tr(r.Variable), f"{r.Mean:.3f}", f"{r.SD:.3f}", f"{r.Mean_exposed:.3f}",
               f"{r.Mean_unexposed:.3f}", f"{r.Diff:+.3f}", f"{int(r.N):,}".replace(",", " ")]
              for r in d1.itertuples()],
    "nota": ("Medias y desviaciones estándar ponderadas por los factores de expansión. "
             "Se clasifica como expuesto a quien tuvo alguna parte de su ventana formativa, "
             f"de los 10 a los 18 años, después de 2007: {R['descriptivas']['n_expuestos']:,}".replace(",", " ")
             + f" encuestados ({R['descriptivas']['share_expuestos']:.1%} de la muestra). La columna "
             "de diferencia es descriptiva; las estimaciones del cuadro 2 no dependen de ella.")}

# ------------------------------------------------------------------ Cuadro 2
T["t2"] = {"num": 2,
    "titulo": "Estimaciones de triple diferencia del cambio en la pendiente rango-rango",
    "cols": ["Especificación", "β₃", "ee", "t", "IC 95 %", "n"],
    "anchos": [36, 11, 11, 8, 23, 11],
    "filas": [[tr(f["nombre"]), n(f["b3"]), par(f["se"]), f"{f['t']:+.2f}",
               f"[{f['ic_bajo']:+.3f}, {f['ic_alto']:+.3f}]", f"{f['n']:,}".replace(",", " ")]
              for f in R["principal"]],
    "nota": ("Los coeficientes son el cambio en la pendiente rango-rango por desviación estándar "
             f"de intensidad de violencia estatal, que es {R['muestra']['de_intensidad']:.3f}. "
             f"La pendiente base es {R['muestra']['pendiente_base']:.3f}. Todas incluyen efectos "
             "fijos de entidad y de año de nacimiento y ambos interactuados con el rango de origen, "
             "y van ponderadas por los factores de expansión. Errores agrupados por entidad, salvo "
             "el renglón (5) que agrupa por año de nacimiento. Para el renglón (1) la prueba de "
             f"permutación sobre 2 000 reasignaciones da p = {R['permutacion']['p']:.2f}, con el "
             f"95 % central del nulo entre {R['permutacion']['nulo_bajo']:+.3f} y "
             f"{R['permutacion']['nulo_alto']:+.3f}.")}

# ------------------------------------------------------------------ Cuadro 3
T["t3"] = {"num": 3,
    "titulo": "El camino de especificación: qué quita cada bloque de controles",
    "cols": ["Controles incluidos", "β₃", "ee", "t"],
    "anchos": [54, 16, 16, 14],
    "filas": [[tr(c["nombre"]), n(c["b3"]), par(c["se"]), f"{c['t']:+.2f}"]
              for c in R["capas"]],
    "nota": ("Cada renglón agrega un bloque al anterior; el (4) es la especificación del cuadro 2, "
             "columna (1). Coeficientes por desviación estándar de intensidad; errores agrupados "
             "por entidad entre paréntesis. El camino no es monótono, que es por qué la "
             "especificación se fija con el argumento de identificación de la sección 4.2 y no se "
             "elige de entre estos renglones.")}

# ------------------------------------------------------------------ Cuadro 6
mu = R["municipal"]
T["t4"] = {"num": 6, "titulo": "Estimaciones con variación municipal dentro del estado",
    "cols": ["Especificación", "β₃", "ee", "t", "n"],
    "anchos": [46, 13, 13, 10, 18],
    "filas": [[tr(e["nombre"]), n(e["b3"]), par(e["se"]), f"{e['t']:+.2f}",
               f"{e['n']:,}".replace(",", " ")] for e in mu["especificaciones"]],
    "nota": ("El tratamiento es la desviación del municipio respecto a la media de su entidad, "
             "interactuada con la fracción de la ventana posterior a 2007. Coeficientes por "
             f"desviación estándar de esa desviación. La muestra es {mu['n']:,}".replace(",", " ")
             + f" encuestados en {mu['municipios']:,}".replace(",", " ")
             + " municipios de origen. Errores agrupados por municipio salvo el renglón (4). "
             "La correlación intraestatal con el origen rural es "
             f"{mu['corr_conteo_rural']:+.2f} con conteos y {mu['corr_tasa_rural']:+.2f} con tasa "
             f"({mu['corr_conteo_rural_nivel']:+.2f} y {mu['corr_tasa_rural_nivel']:+.2f} en "
             "niveles). La prueba conjunta de tendencias previas con tasa da p = "
             f"{mu['p_evento_con_controles']:.2f} con controles de tamaño y "
             f"p = {mu['p_evento_sin_controles']:.2f} sin ellos.")}

# ------------------------------------------------------------------ Cuadro 4
cg = R["conglomerados"]
met = {m["k"]: m for m in cg["metricas_vs_referencia"]}
f5 = [["Panel A. Selección del número de conglomerados", "", "", "", "", ""]]
for k in range(2, 9):
    f5.append([f"k = {k}", f"{cg['silueta_ward'][str(k)]:.3f}",
               f"{cg['silueta_kmedias'][str(k)]:.3f}", f"{met[k]['r2']:.3f}",
               f"{met[k]['calinski_harabasz']:.2f}", f"{met[k]['davies_bouldin']:.3f}"])
f5.append(["Panel B. Acuerdo y estabilidad", "", "", "", "", ""])
f5 += [["Correlación cofenética (Ward)", f"{cg['cofenetica']:.3f}", "", "", "", ""],
       ["Rand ajustado, Ward contra k-medias en k = 3", f"{cg['ari_ward_kmedias']:.3f}", "", "", "", ""],
       ["Rand ajustado medio, 500 sorteos del 80 %", f"{cg['estabilidad_ari_media']:.3f}", "", "", "", ""],
       ["  percentil 5 de esa distribución", f"{cg['estabilidad_ari_p5']:.3f}", "", "", "", ""],
       ["Amplitud de los años de pico (años)", f"{cg['amplitud_picos']}", "", "", "", ""]]
f5.append(["Panel C. El modelo dentro de cada conglomerado", "", "", "", "", ""])
pico = {p["cg"]: p for p in cg["perfiles"]}
for f in cg["por_conglomerado"]:
    c = f["cg"]
    f5.append([f"Conglomerado {c}: {pico[c]['n_entidades']} entidades, pico {pico[c]['pico']}",
               n(f["b3"]), par(f["se"]), f"{f['t']:+.2f}", f"{f['p_perm']:.3f}",
               f"{f['n']:,}".replace(",", " ")])
T["t5"] = {"num": 4, "titulo": "Validación de los conglomerados y estimaciones por conglomerado",
    "cols": ["", "Silueta Ward / β₃", "Silueta k-medias / ee", "R² contra k = 1 / t",
             "Calinski-Harabasz / p perm.", "Davies-Bouldin / n"],
    "anchos": [32, 14, 14, 13, 14, 13], "filas": f5, "paneles": [0, 8, 14],
    "nota": ("El panel A reporta criterios internos por número de conglomerados; R² es la fracción "
             "de la suma de cuadrados total en la forma de las trayectorias que explica la "
             "partición, con k = 1 como modelo de referencia, que es el que la dosis supone. La "
             "silueta se maximiza en k = 3 en los dos algoritmos, Calinski-Harabasz en k = 2 y "
             "Davies-Bouldin sigue mejorando; el conglomerado de primera ola de 15 entidades y el "
             "grupo de 11 de pico tardío son idénticos en k = 2, 3 y 4, así que la conclusión no "
             "depende de cuál criterio se siga. El panel C reporta la estimación dentro de cada "
             "conglomerado, con errores agrupados entre paréntesis y valores p de permutación de "
             "2 000 reasignaciones dentro del conglomerado. Con 6 a 15 entidades por grupo el "
             "estadístico agrupado no es fiable y el valor p de permutación es el que hay que leer; "
             "se muestran los dos para que la brecha se vea.")}

# ------------------------------------------------------------------ Cuadro 7
f6 = [["Panel A. Heterogeneidad", "", "", "", ""]]
for f in R["heterogeneidad"]:
    if f["nombre"].startswith("Outcome"):
        continue
    f6.append([tr(f["nombre"]), n(f["b3"]), par(f["se"]), f"{f['t']:+.2f}",
               f"{f['n']:,}".replace(",", " ")])
f6.append(["Panel B. Medidas de destino alternativas", "", "", "", ""])
for f in R["heterogeneidad"]:
    if f["nombre"].startswith("Outcome"):
        f6.append(["Rango de años de escolaridad", n(f["b3"]), par(f["se"]),
                   f"{f['t']:+.2f}", f"{f['n']:,}".replace(",", " ")])
for m in R["transiciones"]["modelos"][:2]:
    f6.append([m["etiq"].replace("Origin Q1 -> stays in Q1", "Origen Q1 → sigue en Q1")
               .replace("Origin Q1 -> reaches Q4 or Q5", "Origen Q1 → llega a Q4 o Q5"),
               n(m["b"]), par(m["se"]), f"{m['t']:+.2f}", f"{m['n']:,}".replace(",", " ")])
f6.append(["Panel C. ¿Hay primera etapa siquiera?", "", "", "", ""])
for f in R["primera_etapa"]:
    f6.append([tr(f["desenlace"]), n(f["b"]), par(f["se"]), f"{f['t']:+.2f}",
               f"{f['cota_sup']:+.3f}"])
T["t6"] = {"num": 7,
    "titulo": "Heterogeneidad, desenlaces alternativos y comprobaciones de forma reducida",
    "cols": ["", "Coeficiente", "ee", "t", "n / cota superior"],
    "anchos": [40, 14, 14, 10, 22], "filas": f6, "paneles": [0, 7, 11],
    "nota": ("Los paneles A y B reportan el coeficiente de triple diferencia por desviación "
             "estándar de intensidad, con el conjunto completo de efectos fijos y errores "
             "agrupados por entidad. Los últimos dos renglones del panel B condicionan al quintil "
             "de origen, así que el coeficiente es el cambio en la probabilidad de esa transición "
             "y no entra término de interacción. El panel C regresa desenlaces en nivel sobre la "
             "dosis con efectos fijos de entidad y de nacimiento; la última columna es el límite "
             "superior del intervalo de 95 %, es decir el mayor efecto que los datos descartan, en "
             "años para escolaridad, puntos de índice para activos y probabilidad para migración.")}

# ------------------------------------------------------------------ Cuadro 5
rd = R["redatado"]
q = rd["quiebre_por_conglomerado"]
T["t7"] = {"num": 5, "titulo": "Estimaciones bajo tres fechados de la dosis de exposición",
    "cols": ["Fechado del repunte", "β₃", "ee", "t", "Efecto mínimo detectable"],
    "anchos": [34, 14, 14, 10, 28],
    "filas": [[tr(e["dosis"]), n(e["b3"]), par(e["se"]), f"{e['t']:+.2f}",
               f"{e['emd_pct']:.1%} de la pendiente base"] for e in rd["estimaciones"]],
    "nota": ("El renglón (1) impone un inicio común en 2007 para toda entidad. Los renglones (2) "
             "y (3) estiman el inicio ajustando un cambio de nivel a la trayectoria estandarizada "
             "de violencia y eligiendo el año de quiebre que minimiza la suma de cuadrados "
             "residual sobre una rejilla de 2001 a 2015, a nivel de conglomerado y de entidad "
             "respectivamente. Los quiebres estimados por conglomerado son "
             + ", ".join(f"{v['tau']} para el conglomerado {k} (salto {float(v['delta']):+.2f})"
                         for k, v in sorted(q.items()))
             + ". La intensidad se recalcula sobre la ventana posterior al quiebre de cada unidad, "
             "así que los coeficientes son por desviación estándar de la medida correspondiente y "
             "no son comparables en nivel entre renglones, sólo en significancia y en la cota "
             "implícita. La proporción de la muestra con alguna exposición cae de 32.4 % en el "
             "renglón (1) a 26.7 % en el (2), que es por qué la precisión se deteriora.")}

# ------------------------------------------------------------------ Cuadro 8
ma = R["movilidad_absoluta"]
est = {x["percentil"]: x for x in ma["por_percentil"]}
mun = {x["percentil"]: x for x in ma["municipal"]}
T["t8"] = {"num": 8,
    "titulo": "Efecto sobre el rango esperado de destino, por percentil de origen",
    "cols": ["Percentil de origen", "Diseño estatal", "ee", "Diseño municipal", "ee",
             "¿Contiene −1.57?"],
    "anchos": [20, 16, 12, 18, 12, 22],
    "filas": [[f"p{int(p*100)}", f"{est[p]['efecto']:+.2f}", par(est[p]["se"], 2),
               f"{mun[p]['efecto']:+.2f}", par(mun[p]["se"], 2),
               ("estatal sí, municipal no" if p == 0.25 else "")]
              for p in [0.10, 0.25, 0.50, 0.75, 0.90]],
    "nota": ("Las entradas son puntos de rango sobre 100 por desviación estándar de intensidad de "
             "violencia, calculadas como la combinación lineal β₂ + p·β₃ de las especificaciones "
             "del cuadro 2 columna (1) y del cuadro 6 columna (3), con errores de la misma matriz "
             "de covarianzas agrupada. Es el desenlace que Sharkey y Torrats-Espinosa (2017) "
             "reportan como movilidad absoluta ascendente. Su estimación instrumentada para "
             "Estados Unidos en el percentil 25 es −1.57 puntos de rango por desviación estándar "
             "de la tasa de homicidio del condado. La última columna registra si nuestro intervalo "
             "de 95 % en ese percentil contiene su valor: el del diseño estatal, "
             f"[{est[0.25]['ic_bajo']:+.2f}, {est[0.25]['ic_alto']:+.2f}], sí; el del municipal, "
             f"[{mun[0.25]['ic_bajo']:+.2f}, {mun[0.25]['ic_alto']:+.2f}], no. Una desviación "
             "estándar no es el mismo objeto en las dos literaturas, y los desenlaces son un rango "
             "de ingreso allá y uno de activos aquí, así que la comparación es indicativa y no una "
             "prueba formal.")}

# ------------------------------------------------------------------ Cuadro 9
med = R["inegi"]["medidas"]
T["t9"] = {"num": 9, "titulo": "Tres definiciones del tratamiento de violencia",
    "cols": ["Índice de exposición", "β₃", "ee", "Efecto en p25", "ee", "F previas", "p"],
    "anchos": [28, 10, 10, 14, 10, 13, 15],
    "filas": [
        ["(1) SESNSP, cuatro delitos (principal)",
         f"{med['SESNSP cuatro delitos']['b3']:+.4f}",
         f"({med['SESNSP cuatro delitos']['se']:.4f})",
         f"{med['SESNSP cuatro delitos']['p25']:+.2f}".replace("-", "−"),
         f"({med['SESNSP cuatro delitos']['se_p25']:.2f})",
         f"{med['SESNSP cuatro delitos']['F']:.2f}",
         f"{med['SESNSP cuatro delitos']['p']:.2f}  pasa"],
        ["(2) INEGI, nivel 2007-17", f"{med['INEGI nivel 2007-17']['b3']:+.4f}",
         f"({med['INEGI nivel 2007-17']['se']:.4f})",
         f"{med['INEGI nivel 2007-17']['p25']:+.2f}".replace("-", "−"),
         f"({med['INEGI nivel 2007-17']['se_p25']:.2f})",
         f"{med['INEGI nivel 2007-17']['F']:.2f}",
         f"{med['INEGI nivel 2007-17']['p']:.3f}  pasa"],
        ["(3) INEGI, aumento sobre 1990-97", f"{med['INEGI aumento vs 1990-97']['b3']:+.4f}",
         f"({med['INEGI aumento vs 1990-97']['se']:.4f})",
         f"{med['INEGI aumento vs 1990-97']['p25']:+.2f}".replace("-", "−"),
         f"({med['INEGI aumento vs 1990-97']['se_p25']:.2f})",
         f"{med['INEGI aumento vs 1990-97']['F']:.2f}",
         f"{med['INEGI aumento vs 1990-97']['p']:.3f}  REPRUEBA"]],
    "nota": ("Cada renglón reestima la especificación del cuadro 2 columna (1) con un índice de "
             "exposición distinto, dejando todo lo demás fijo. β₃ es el cambio en la pendiente "
             "rango-rango por desviación estándar de ese índice; el efecto en p25 está en puntos "
             "de rango sobre 100, comparable con el −1.57 de Sharkey y Torrats-Espinosa. Las dos "
             "últimas columnas reportan la prueba conjunta de que los grupos de nacimiento previos "
             "al repunte no muestran pendiente diferencial, que es el supuesto de identificación "
             "del diseño. El renglón (3) define el tratamiento como el aumento de la tasa de "
             "homicidio entre 1990-97 y 2007-17 en lugar de su nivel, que es el objeto mejor "
             "identificado en principio; da la estimación mayor del artículo y una p de "
             "permutación de "
             f"{med['INEGI aumento vs 1990-97']['p_perm_p25']:.3f}, y es el único renglón que viola el supuesto de "
             "identificación. Las cifras del INEGI son defunciones por entidad y año de ocurrencia "
             "de los microdatos de estadísticas vitales, con población de CONAPO a mitad de año "
             "como denominador.")}

with open(_r.MAN_ES + "/tables.json", "w", encoding="utf-8") as f:
    json.dump(T, f, indent=1, ensure_ascii=False)
for k, t in T.items():
    print(f"{k}: Cuadro {t['num']} — {t['titulo'][:52]}")
    assert 95 <= sum(t["anchos"]) <= 106, (k, sum(t["anchos"]))
print("\nEscrito: " + _r.MAN_ES + "/tables.json")
