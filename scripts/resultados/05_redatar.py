# -*- coding: utf-8 -*-
"""
redatar.py — la dosis con el calendario propio de cada región
=============================================================
El calendario común de 2007 es una suposición. Los conglomerados muestran que
once entidades repuntaron hasta 2017, de modo que para ellas la dosis está mal
fechada y eso atenúa b3 hacia cero.

Aquí se estima el año de inicio del repunte en lugar de imponerlo, por búsqueda
de quiebre estructural sobre la trayectoria de violencia:

    y(t) = mu1 + delta * 1[t >= tau] + e(t)

sobre una rejilla de tau, eligiendo el que minimiza la suma de cuadrados. Se
hace de dos maneras:

  * por conglomerado, sobre la trayectoria media del grupo (más precisa, y es
    la que motiva el módulo de conglomerados)
  * por entidad, sobre su propia trayectoria (más flexible, más ruidosa)

Dos piezas se redefinen, y conviene no confundirlas:

  TIEMPO    phi_e(c) = fracción de la ventana 10-18 posterior a tau_e
            se estima sobre la serie ESTANDARIZADA DENTRO de la entidad,
            porque la forma es lo que fecha el repunte

  MAGNITUD  I(e) = índice medio de violencia sobre [tau_e, 2017]
            se calcula sobre la serie SIN estandarizar dentro de la entidad,
            porque el nivel es lo que mide cuánta violencia hubo

Usar la serie estandarizada para la magnitud borraría las diferencias de nivel
entre entidades, que es justo lo que la dosis necesita.
"""
import json, sys, warnings
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from guardar import guardar
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
SEED = 20261102
np.random.seed(SEED)

SAL = _r.SAL
from base import construir, muestra, panel_violencia, ddd, escala
from graficas_entregable1 import ABREV
from scipy.cluster.hierarchy import linkage, fcluster

LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def titulo(t):
    di("\n" + "=" * 74)
    di(t)
    di("=" * 74)


# ------------------------------------------------------- estimador de quiebre
def quiebre(y, anios, lo=2001, hi=2015):
    """Año que minimiza la suma de cuadrados de un cambio de nivel.

    Devuelve (tau, delta, perfil de SSR). La rejilla deja al menos cuatro años
    de cada lado para que el quiebre esté identificado.
    """
    perfil = {}
    for tau in range(lo, hi + 1):
        d = (anios >= tau).astype(float)
        X = np.column_stack([np.ones(len(y)), d])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        perfil[tau] = float(((y - X @ b) ** 2).sum())
    tau = min(perfil, key=perfil.get)
    d = (anios >= tau).astype(float)
    X = np.column_stack([np.ones(len(y)), d])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return tau, float(b[1]), perfil


# ------------------------------------------------------------------- insumos
panel, _ = panel_violencia()
W = panel.pivot(index="cve", columns="year", values="indice").sort_index()
anios = W.columns.values.astype(int)
F = W.sub(W.mean(axis=1), axis=0).div(W.std(axis=1), axis=0)   # forma
Z = linkage(F.values, method="ward")
cg = pd.Series(fcluster(Z, 3, criterion="maxclust"), index=W.index, name="cg")

titulo("A. AÑO DE QUIEBRE POR CONGLOMERADO")
di(f"{'Conglomerado':14s} {'entidades':>10} {'tau':>6} {'delta':>8} "
   f"{'2do mejor':>10} {'brecha SSR':>11}")
tau_cg, info_cg = {}, {}
for c in sorted(cg.unique()):
    ent = cg[cg == c].index
    y = F.loc[ent].mean().values
    tau, delta, perfil = quiebre(y, anios)
    orden = sorted(perfil, key=perfil.get)
    brecha = perfil[orden[1]] - perfil[orden[0]]
    tau_cg[c] = tau
    info_cg[c] = {"tau": int(tau), "delta": delta, "n": int(len(ent)),
                  "segundo": int(orden[1]), "brecha_ssr": brecha,
                  "entidades": [ABREV[int(e)] for e in ent]}
    di(f"  {c:<12d} {len(ent):>10d} {tau:>6d} {delta:>8.3f} "
       f"{orden[1]:>10d} {brecha:>11.3f}")
di("")
for c in sorted(cg.unique()):
    di(f"  Conglomerado {c} (tau={tau_cg[c]}): "
       f"{', '.join(info_cg[c]['entidades'])}")

titulo("B. AÑO DE QUIEBRE POR ENTIDAD")
tau_ent = {}
filas = []
for e in W.index:
    tau, delta, _ = quiebre(F.loc[e].values, anios)
    tau_ent[int(e)] = int(tau)
    filas.append({"cve": int(e), "ent": ABREV[int(e)], "cg": int(cg[e]),
                  "tau": int(tau), "delta": delta})
te = pd.DataFrame(filas).sort_values("tau")
di(te.to_string(index=False))
di("")
di("Distribución de los quiebres por entidad:")
for t, n in te.tau.value_counts().sort_index().items():
    di(f"  {t}: {'#' * n}  ({n})")
di(f"\nConcordancia: la mediana del quiebre por entidad dentro de cada conglomerado")
for c in sorted(cg.unique()):
    s = te[te.cg == c]
    di(f"  Conglomerado {c}: mediana {int(s.tau.median())}, "
       f"rango [{s.tau.min()}, {s.tau.max()}], quiebre del grupo {tau_cg[c]}")

# ---------------------------------------------------- construcción de dosis
titulo("C. LAS TRES DOSIS")
df = construir(verbose=False)
M = muestra(df).copy()
M["nac"] = M.nac.astype(int)
M["cg"] = M.p19.map(cg)

idx = panel.set_index(["cve", "year"]).indice     # índice SIN estandarizar


def intensidad(tau_por_ent):
    """Índice medio de violencia sobre el periodo propio de cada entidad."""
    out = {}
    for e in W.index:
        t0 = tau_por_ent[int(e)]
        out[int(e)] = float(idx.loc[int(e)].loc[t0:2017].mean())
    return pd.Series(out)


def fraccion(nac, tau):
    return len([y for y in range(nac + 10, nac + 19) if y >= tau]) / 9.0


# (0) la dosis original: calendario común de 2007
tau_comun = {int(e): 2007 for e in W.index}
# (1) refechada por conglomerado
tau_por_cg = {int(e): tau_cg[int(cg[e])] for e in W.index}
# (2) refechada por entidad
tau_por_ent = {int(e): tau_ent[int(e)] for e in W.index}

VARIANTES = [("Calendario común 2007 (original)", tau_comun),
             ("Refechada por conglomerado", tau_por_cg),
             ("Refechada por entidad", tau_por_ent)]

for nombre, taus in VARIANTES:
    I = intensidad(taus)
    col_i = "intens_" + nombre[:4].strip().lower().replace(" ", "")
    M["_I"] = M.p19.map(I)
    M["_frac"] = [fraccion(n, taus[int(e)]) for n, e in zip(M.nac, M.p19)]
    M[f"dosis__{nombre[:12]}"] = M._I * M._frac
    M[f"intens__{nombre[:12]}"] = M._I
    M[f"frac__{nombre[:12]}"] = M._frac
    di(f"\n{nombre}")
    di(f"  intensidad: media {M._I.mean():+.3f}, d.e. entre entidades "
       f"{M.groupby('p19')._I.first().std():.3f}")
    di(f"  fracción expuesta: media {M._frac.mean():.3f}, "
       f"con exposición positiva {100*(M._frac>0).mean():.1f} %")
    di(f"  dosis: media {(M._I*M._frac).mean():+.4f}, "
       f"d.e. {(M._I*M._frac).std():.4f}")

# ------------------------------------------------------------- estimación
titulo("D. EL MODELO CON CADA DOSIS")
di(f"{'Dosis':44s} {'b3':>10} {'ee':>9} {'t':>7} {'EMD %':>7}")
res = []
PEND = float(np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0])
for nombre, taus in VARIANTES:
    k = nombre[:12]
    d = M.copy()
    d["intens"] = d[f"intens__{k}"]
    d["frac"] = d[f"frac__{k}"]
    d["dosis"] = d[f"dosis__{k}"]
    K = d.groupby("p19").intens.first().std()
    m = ddd(d)
    b, se = m.params["b3"] * K, m.bse["b3"] * K
    emd = 2.8 * se / PEND
    di(f"  {nombre:42s} {b:+10.4f} {se:9.4f} {b/se:+7.2f} {emd:7.1%}")
    res.append({"dosis": nombre, "b3": float(b), "se": float(se),
                "t": float(b / se), "emd_pct": float(emd),
                "K": float(K), "n": int(len(d))})

# ------------------------------------------- estudio de eventos refechado
titulo("E. TENDENCIAS PREVIAS CON LA DOSIS REFECHADA POR CONGLOMERADO")
k = VARIANTES[1][0][:12]
d = M.copy()
d["intens"] = d[f"intens__{k}"]
d["frac"] = d[f"frac__{k}"]
d["dosis"] = d[f"dosis__{k}"]
cortes = [1958, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998]
etiq = ["<=1970", "1971-74", "1975-78", "1979-82", "1983-86", "1987-90",
        "1991-94", "1995-98"]
d["grp"] = pd.cut(d.nac, cortes, labels=etiq)
REF = "1979-82"
K = d.groupby("p19").intens.first().std()
G = pd.get_dummies(d.grp, prefix="g", dtype=float).drop(columns=[f"g_{REF}"])
E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
X = sm.add_constant(pd.concat([
    pd.DataFrame({"r_ori": d.r_ori.values}, index=d.index),
    G.mul(d.intens, axis=0).add_prefix("d_"),
    G.mul(d.r_ori * d.intens, axis=0).add_prefix("ev_"),
    E, C, E.mul(d.r_ori, axis=0).add_prefix("ri_"),
    C.mul(d.r_ori, axis=0).add_prefix("rc_")], axis=1))
me = sm.WLS(d.r_des, X, weights=d.factor).fit(
    cov_type="cluster", cov_kwds={"groups": d.p19})
di(f"  {'grupo':>9} {'b':>9} {'ee':>8} {'t':>7}")
ev = []
for e_ in etiq:
    if e_ == REF:
        di(f"  {e_:>9} {0:>9.3f} {0:>8.3f} {'—':>7}  (referencia)")
        ev.append({"grupo": e_, "b": 0.0, "se": 0.0, "previo": False})
        continue
    b, se = me.params[f"ev_g_{e_}"] * K, me.bse[f"ev_g_{e_}"] * K
    prev = bool((d.dosis[d.grp == e_] == 0).all())
    di(f"  {e_:>9} {b:>9.3f} {se:>8.3f} {b/se:>7.2f}"
       f"{'  previo' if prev else '  expuesto'}")
    ev.append({"grupo": e_, "b": float(b), "se": float(se), "previo": prev})
PRE = [e_["grupo"] for e_ in ev if e_["previo"]]
ft = me.f_test([f"ev_g_{e_}=0" for e_ in PRE])
di(f"\n  Grupos previos: {', '.join(PRE)}")
di(f"  Prueba conjunta: F = {float(ft.fvalue):.3f}   p = {float(ft.pvalue):.3f}")

# ------------------------------------------------------------------ salida
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
R["redatado"] = {
    "quiebre_por_conglomerado": info_cg,
    "quiebre_por_entidad": te.to_dict("records"),
    "estimaciones": res,
    "evento_refechado": {"coef": ev, "grupos_previos": PRE,
                         "F": float(ft.fvalue), "p": float(ft.pvalue)},
}
guardar(R, f"{SAL}/resultados.json")
with open(f"{SAL}/log_redatado.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
te.to_csv(f"{SAL}/quiebres_entidad.csv", index=False)
di(f"\nEscrito en resultados.json y {SAL}/log_redatado.txt")
