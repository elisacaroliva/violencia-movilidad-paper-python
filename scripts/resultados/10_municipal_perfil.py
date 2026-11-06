# -*- coding: utf-8 -*-
"""
municipal_perfil.py — el desenlace de Sharkey bajo el diseño municipal
=======================================================================
`movilidad_absoluta.py` calcula el rango esperado de destino por percentil de
origen bajo el diseño ESTATAL. El cuadro 8 compara ese perfil con el del
diseño intraestatal, porque es ahí donde la comparación con Sharkey y
Torrats-Espinosa (2017) se vuelve interesante: su diseño también es
intraestatal, de condados dentro de un estado, de modo que el renglón
municipal es el verdaderamente comparable y el estatal es el que conviene
leer con cuidado.

Se replica exactamente la especificación de la columna (3) del cuadro 6 —la
dosis municipal construida con tasa por 100 000, con los indicadores de tamaño
de localidad interactuados con el rango de origen y errores agrupados por
municipio— y se evalúa la combinación lineal b2 + p*b3 en los mismos cinco
percentiles del diseño estatal.

De paso se llenan los dos valores p de la prueba conjunta de tendencias
previas municipales, con y sin los controles de tamaño, que la nota del
cuadro 6 necesita y que `congelar.py` reporta sólo en el log.

Uso:  python -I codigo/municipal_perfil.py
"""
import json
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
SEED = 20261102
np.random.seed(SEED)

SAL = _r.SAL
from guardar import guardar
from municipal import construir_municipal, dummies_tam, evento_municipal

PERCENTILES = [0.10, 0.25, 0.50, 0.75, 0.90]
SHARKEY_P25 = -1.57
LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


Mm = construir_municipal(verbose=False)
tams = dummies_tam(Mm)
K = float(Mm.Dm.std())            # una d.e. de la desviación intraestatal
PEND = float(np.polyfit(Mm.r_ori, Mm.r_des, 1, w=np.sqrt(Mm.factor))[0])

# ----------------------------------------- columna (3) del cuadro 6, completa
C = pd.get_dummies(Mm.nac.astype(int), prefix="c", drop_first=True).astype(float)
E = pd.get_dummies(Mm.p19.astype(int), prefix="e", drop_first=True).astype(float)
piezas = [pd.DataFrame({"r_ori": Mm.r_ori.values, "trat": Mm.dosis_m.values,
                        "b3": (Mm.r_ori * Mm.dosis_m).values}, index=Mm.index),
          C, C.mul(Mm.r_ori, axis=0).add_prefix("rc_"),
          E, E.mul(Mm.r_ori, axis=0).add_prefix("ri_")]
for c in tams:
    piezas.append(pd.DataFrame({f"x_{c}": Mm[c].values,
                                f"xr_{c}": (Mm[c] * Mm.r_ori).values},
                               index=Mm.index))
X = sm.add_constant(pd.concat(piezas, axis=1))
m = sm.WLS(Mm.r_des, X, weights=Mm.factor).fit(cov_type="cluster",
                                               cov_kwds={"groups": Mm.mun})
nombres = list(X.columns)
i_t, i_3 = nombres.index("trat"), nombres.index("b3")

di("=" * 74)
di("RANGO ESPERADO DE DESTINO POR PERCENTIL — DISEÑO MUNICIPAL")
di("=" * 74)
di(f"Muestra: {len(Mm):,} encuestados en {Mm.mun.nunique():,} municipios de origen")
di(f"Escala: puntos de rango sobre 100, por d.e. de la desviación intraestatal "
   f"({K:.3f})")
di("")
di(f"  {'Percentil':24s} {'efecto':>9} {'ee':>8} {'t':>7} {'IC 95 %':>22}")

filas = []
for p in PERCENTILES:
    r = np.zeros(len(nombres))
    r[i_t] = 1.0
    r[i_3] = p
    t = m.t_test(r)
    b = float(np.squeeze(t.effect)) * K * 100
    se = float(np.squeeze(t.sd)) * K * 100
    filas.append({"percentil": p, "efecto": b, "se": se, "t": float(b / se),
                  "ic_bajo": b - 1.96 * se, "ic_alto": b + 1.96 * se,
                  "emd": 2.8 * se})
    di(f"  p{int(p * 100):<23d} {b:+9.3f} {se:8.3f} {b / se:+7.2f} "
       f"  [{b - 1.96 * se:+7.3f}, {b + 1.96 * se:+7.3f}]")

p25 = [f for f in filas if f["percentil"] == 0.25][0]
contiene = p25["ic_bajo"] < SHARKEY_P25 < p25["ic_alto"]
di("")
di(f"  b3 de referencia: {m.params['b3'] * K:+.4f} ({m.bse['b3'] * K:.4f})")
di(f"  El intervalo municipal en p25 "
   f"{'CONTIENE' if contiene else 'EXCLUYE'} el {SHARKEY_P25} de Sharkey y "
   f"Torrats-Espinosa.")
di(f"  Efecto mínimo detectable en p25: {p25['emd']:.3f} puntos de rango.")

# ------------------------------- tendencias previas, con y sin control de tamaño
di("")
di("=" * 74)
di("TENDENCIAS PREVIAS MUNICIPALES")
di("=" * 74)
di("Con controles de tamaño de localidad:")
p_con = float(evento_municipal(Mm, controles=tams))
di("\nSin controles de tamaño de localidad:")
p_sin = float(evento_municipal(Mm))

# ------------------------------------------------------------------- salida
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
R.setdefault("movilidad_absoluta", {})["municipal"] = filas
R["movilidad_absoluta"]["municipal_meta"] = {
    "de_intraestatal": K, "n": int(len(Mm)),
    "municipios": int(Mm.mun.nunique()),
    "especificacion": "cuadro 6 columna (3): tasa + tamaño de localidad x rango",
    "contiene_sharkey_p25": bool(contiene)}
R.setdefault("municipal", {})["p_evento_con_controles"] = p_con
R["municipal"]["p_evento_sin_controles"] = p_sin
guardar(R, f"{SAL}/resultados.json")
with open(f"{SAL}/log_municipal_perfil.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
print("\nEscrito en resultados.json")
