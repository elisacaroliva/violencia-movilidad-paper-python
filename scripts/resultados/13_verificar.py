# -*- coding: utf-8 -*-
"""
verificar.py — comprueba las cifras que el manuscrito hereda de documentos
previos, en lugar de confiar en ellas, y añade las métricas de desempeño del
agrupamiento frente al modelo de referencia (k = 1, calendario común).
"""
import json, sys, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
SEED = 20261102
np.random.seed(SEED)

SAL = _r.SAL
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
from base import construir, muestra, escala, panel_violencia
from graficas_entregable1 import ABREV

LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


df = construir(verbose=False)
M = muestra(df)
panel, intens = panel_violencia()

# ------------------------------------------------- 1. correlación entre entidades
di("=" * 74)
di("1. CORRELACIÓN ENTRE PERSISTENCIA E INTENSIDAD, ENTRE ENTIDADES")
di("=" * 74)
filas = []
for e, s in M.groupby("p19"):
    if len(s) < 100:
        continue
    filas.append({"e": int(e), "n": len(s),
                  "pend": float(np.polyfit(s.r_ori, s.r_des, 1,
                                           w=np.sqrt(s.factor))[0]),
                  "I": float(s.intens.iloc[0])})
ce = pd.DataFrame(filas)
r = float(np.corrcoef(ce.pend, ce.I)[0, 1])
n = len(ce)
# intervalo de Fisher
z = np.arctanh(r)
se_z = 1 / np.sqrt(n - 3)
lo, hi = np.tanh(z - 1.96 * se_z), np.tanh(z + 1.96 * se_z)
di(f"  Entidades usadas : {n}")
di(f"  Correlación      : {r:+.3f}")
di(f"  IC 95 % (Fisher) : [{lo:+.3f}, {hi:+.3f}]")
R["corr_entidades"] = {"r": r, "n": n, "ic_bajo": float(lo), "ic_alto": float(hi)}

# ------------------------------------------------------- 2. pendiente por cohorte
di("\n" + "=" * 74)
di("2. PENDIENTE RANGO-RANGO POR GRUPO DE NACIMIENTO")
di("=" * 74)
bandas = [(1959, 1966), (1967, 1974), (1975, 1984), (1985, 1991), (1992, 1998)]
pc = []
for a, b in bandas:
    s = M[(M.nac >= a) & (M.nac <= b)]
    p_ = float(np.polyfit(s.r_ori, s.r_des, 1, w=np.sqrt(s.factor))[0])
    exp_ = float((s.frac > 0).mean())
    pc.append({"banda": f"{a}-{b}", "n": int(len(s)), "pendiente": p_,
               "share_expuesto": exp_})
    di(f"  {a}-{b}: n={len(s):5d}  pendiente {p_:.3f}  "
       f"expuestos {exp_:.0%}")
R["pendiente_por_cohorte"] = pc

# ------------------------------- 3. métricas del agrupamiento contra el k = 1
di("\n" + "=" * 74)
di("3. AGRUPAMIENTO: DESEMPEÑO FRENTE AL MODELO DE REFERENCIA (k = 1)")
di("=" * 74)
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score

W = panel.pivot(index="cve", columns="year", values="indice").sort_index()
F = W.sub(W.mean(axis=1), axis=0).div(W.std(axis=1), axis=0)
X = F.values
Z = linkage(X, method="ward")

TSS = float(((X - X.mean(axis=0)) ** 2).sum())        # el modelo k = 1
di(f"  Suma de cuadrados total (modelo de referencia, k = 1): {TSS:.1f}")
di("")
di(f"  {'k':>3} {'WSS':>9} {'R2':>7} {'Calinski-H':>11} {'Davies-B':>9}")
met = []
for k in range(1, 9):
    if k == 1:
        wss, r2, ch, db = TSS, 0.0, np.nan, np.nan
    else:
        lab = fcluster(Z, k, criterion="maxclust")
        wss = float(sum(((X[lab == c] - X[lab == c].mean(axis=0)) ** 2).sum()
                        for c in np.unique(lab)))
        r2 = 1 - wss / TSS
        ch = float(calinski_harabasz_score(X, lab))
        db = float(davies_bouldin_score(X, lab))
    met.append({"k": k, "wss": wss, "r2": r2, "calinski_harabasz": ch,
                "davies_bouldin": db})
    di(f"  {k:>3} {wss:>9.1f} {r2:>7.3f} "
       f"{'—' if np.isnan(ch) else format(ch, '>11.2f')} "
       f"{'—' if np.isnan(db) else format(db, '>9.3f')}")
R["conglomerados"]["metricas_vs_referencia"] = met

# año del pico implícito en cada modelo
anios = W.columns.values
ward3 = fcluster(Z, 3, criterion="maxclust")
pico_global = int(anios[np.argmax(X.mean(axis=0))])
di(f"\n  Pico implícito del modelo de referencia (una sola trayectoria media): "
   f"{pico_global}")
picos = []
for c in np.unique(ward3):
    pk = int(anios[np.argmax(X[ward3 == c].mean(axis=0))])
    picos.append(pk)
    di(f"    Conglomerado {c}: pico {pk}")
di(f"  Amplitud del desacuerdo entre regímenes: {max(picos)-min(picos)} años")
R["conglomerados"]["pico_referencia"] = pico_global
R["conglomerados"]["amplitud_picos"] = int(max(picos) - min(picos))

with open(f"{SAL}/resultados.json", "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2, ensure_ascii=False)
with open(f"{SAL}/log_verificacion.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
di(f"\nActualizado: {SAL}/resultados.json")
