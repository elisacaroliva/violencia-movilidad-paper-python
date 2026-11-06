# -*- coding: utf-8 -*-
"""
movilidad_absoluta.py — el desenlace de Sharkey y Torrats-Espinosa
==================================================================
Sharkey y Torrats-Espinosa (2017, J Urban Econ 102:22-33) hacen esta misma
pregunta para Estados Unidos. Su desenlace PRINCIPAL no es la pendiente sino
la movilidad absoluta ascendente: el rango esperado de destino de quien nace
en el percentil 25 de origen. La pendiente la usan sólo como desenlace
secundario.

Nuestra especificación ya contiene esa cantidad. Como

    rango_des = b1*p + b2*D + b3*(p*D) + ...

el efecto de la dosis sobre el rango esperado en el percentil p es

    d(rango_des)/dD |_p  =  b2 + p*b3

que es una combinación lineal de coeficientes que ya estimamos. Reportarla
vuelve el trabajo directamente comparable con el único precedente directo de
la literatura, y además puede estimarse con más precisión que b3 solo.

Se reporta en puntos de rango sobre 100, que es la escala de ellos.
"""
import json, os, sys, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
SEED = 20261102
np.random.seed(SEED)

SAL = _r.SAL
from base import construir, muestra, efectos_fijos, escala

LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


df = construir(verbose=False)
M = muestra(df).copy()
K = escala(M)
PEND = float(np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0])

# --------------------------------------------------------------- estimación
base = pd.DataFrame({"r_ori": M.r_ori.values, "dosis": M.dosis.values,
                     "b3": (M.r_ori * M.dosis).values}, index=M.index)
X = sm.add_constant(pd.concat([base] + efectos_fijos(M), axis=1))
m = sm.WLS(M.r_des, X, weights=M.factor).fit(cov_type="cluster",
                                             cov_kwds={"groups": M.p19})

nombres = list(X.columns)
i_d, i_3 = nombres.index("dosis"), nombres.index("b3")

di("=" * 74)
di("EFECTO SOBRE EL RANGO ESPERADO DE DESTINO, POR PERCENTIL DE ORIGEN")
di("=" * 74)
di("Escala: puntos de rango sobre 100, por desviación estándar de intensidad")
di("(la misma de Sharkey y Torrats-Espinosa 2017)")
di("")
di(f"  {'Percentil de origen':24s} {'efecto':>9} {'ee':>8} {'t':>7} {'IC 95 %':>20}")

filas = []
for p in [0.10, 0.25, 0.50, 0.75, 0.90]:
    r = np.zeros(len(nombres))
    r[i_d] = 1.0
    r[i_3] = p
    t = m.t_test(r)
    b = float(np.squeeze(t.effect)) * K * 100
    se = float(np.squeeze(t.sd)) * K * 100
    filas.append({"percentil": p, "efecto": b, "se": se, "t": float(b / se),
                  "ic_bajo": b - 1.96 * se, "ic_alto": b + 1.96 * se,
                  "emd": 2.8 * se})
    di(f"  p{int(p*100):<23d} {b:+9.3f} {se:8.3f} {b/se:+7.2f} "
       f"  [{b-1.96*se:+6.3f}, {b+1.96*se:+6.3f}]")

di("")
di(f"  Para referencia, b3 (cambio de la pendiente) = "
   f"{m.params['b3']*K:+.4f} ({m.bse['b3']*K:.4f})")

# ------------------------------------------------------- comparación directa
di("")
di("=" * 74)
di("COMPARACIÓN CON EL PRECEDENTE")
di("=" * 74)
p25 = [f for f in filas if f["percentil"] == 0.25][0]
di(f"  Sharkey y Torrats-Espinosa 2017, EE. UU., variable instrumental:")
di(f"    una d.e. de homicidio baja el rango esperado en p25 en 1.57 puntos")
di(f"    (una d.e. de delito violento lo baja 1.79 puntos)")
di(f"  Nuestro estimado para México, p25:")
di(f"    {p25['efecto']:+.3f} puntos, ee {p25['se']:.3f}, "
   f"IC95 [{p25['ic_bajo']:+.3f}, {p25['ic_alto']:+.3f}]")
di(f"  Efecto mínimo detectable al 80 % de potencia: {p25['emd']:.3f} puntos")
di("")
if p25["emd"] < 1.57:
    di(f"  -> Nuestro diseño SÍ habría detectado un efecto del tamaño del suyo:")
    di(f"     {p25['emd']:.2f} < 1.57. La cota es informativa frente al precedente.")
else:
    di(f"  -> Nuestro diseño NO habría detectado un efecto del tamaño del suyo:")
    di(f"     {p25['emd']:.2f} > 1.57. La cota no descarta ese orden de magnitud.")
di(f"  Su intervalo de 95 % para p25 y el nuestro "
   f"{'SE TRASLAPAN' if p25['ic_bajo'] < -1.57 < p25['ic_alto'] else 'NO se traslapan'}"
   f" en el valor -1.57.")

# ------------------------------------------- misma ventana de exposición
di("")
di("=" * 74)
di("ROBUSTEZ: SU VENTANA DE EXPOSICIÓN (14-17) EN LUGAR DE LA NUESTRA (10-18)")
di("=" * 74)
from base import panel_violencia

panel, intens = panel_violencia()
M2 = M.copy()
M2["nac"] = M2.nac.astype(int)
M2["frac"] = [len([y for y in range(n + 14, n + 18) if y >= 2007]) / 4.0
              for n in M2.nac]
M2["dosis"] = M2.intens * M2.frac
K2 = escala(M2)
base2 = pd.DataFrame({"r_ori": M2.r_ori.values, "dosis": M2.dosis.values,
                      "b3": (M2.r_ori * M2.dosis).values}, index=M2.index)
X2 = sm.add_constant(pd.concat([base2] + efectos_fijos(M2), axis=1))
m2 = sm.WLS(M2.r_des, X2, weights=M2.factor).fit(
    cov_type="cluster", cov_kwds={"groups": M2.p19})
n2 = list(X2.columns)
r = np.zeros(len(n2)); r[n2.index("dosis")] = 1.0; r[n2.index("b3")] = 0.25
t2 = m2.t_test(r)
b2_ = float(np.squeeze(t2.effect)) * K2 * 100
se2_ = float(np.squeeze(t2.sd)) * K2 * 100
di(f"  Ventana 14-17, efecto en p25: {b2_:+.3f} puntos (ee {se2_:.3f})")
di(f"  Cambio en la pendiente b3   : {m2.params['b3']*K2:+.4f} "
   f"({m2.bse['b3']*K2:.4f})")
di(f"  Con exposición positiva     : {100*(M2.frac>0).mean():.1f} %")

# ------------------------------------------------------------------ salida
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
R["movilidad_absoluta"] = {
    "por_percentil": filas,
    "escala": "puntos de rango sobre 100, por d.e. de intensidad",
    "referencia_sharkey": {"p25_iv_homicidio": -1.57,
                           "p25_iv_delito_violento": -1.79,
                           "cita": "Sharkey y Torrats-Espinosa 2017, J Urban Econ 102:22-33"},
    "ventana_14_17": {"efecto_p25": b2_, "se_p25": se2_,
                      "b3": float(m2.params["b3"] * K2),
                      "se_b3": float(m2.bse["b3"] * K2),
                      "share_expuesto": float((M2.frac > 0).mean())},
}
tmp = f"{SAL}/resultados.json.tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2, ensure_ascii=False, default=str)
os.replace(tmp, f"{SAL}/resultados.json")
with open(f"{SAL}/log_movilidad_absoluta.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
di(f"\nEscrito en resultados.json")
