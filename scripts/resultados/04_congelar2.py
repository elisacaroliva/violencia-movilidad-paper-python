# -*- coding: utf-8 -*-
"""
congelar2.py — complementos del congelado
=========================================
Añade a resultados.json lo que congelar.py deja fuera:
  * el estudio de eventos municipal con y sin controles de tamaño de localidad,
    para saber qué especificación corresponde a cada cifra reportada antes
  * DBSCAN a nivel municipal, donde sí hay densidad suficiente
  * las rutas que no funcionaron: transiciones por quintil y agrupamiento de
    la EMOVI 2017 con la de 2023
"""
import json, os, sys, warnings
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
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


from municipal import construir_municipal, evento_municipal, dummies_tam
from base import escala, ddd

# ------------------------------------------------- evento municipal, dos versiones
di("=" * 74)
di("EVENTO MUNICIPAL: ¿CON O SIN CONTROLES DE TAMAÑO DE LOCALIDAD?")
di("=" * 74)
Mm = construir_municipal(verbose=False)
di("\nSin controles de tamaño:")
p_sin = evento_municipal(Mm)
tams = dummies_tam(Mm)
di("\nCon tamaño de localidad interactuado con el rango:")
p_con = evento_municipal(Mm, controles=tams)
R["municipal"]["p_evento_sin_controles"] = float(p_sin)
R["municipal"]["p_evento_con_controles"] = float(p_con)

# ------------------------------------------------------- DBSCAN municipal
di("\n" + "=" * 74)
di("DBSCAN A NIVEL MUNICIPAL (donde sí hay densidad)")
di("=" * 74)
from sklearn.cluster import DBSCAN

MUN = _r.MUN
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
         "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
mu = pd.read_csv(MUN, encoding="latin-1", low_memory=False)
mu["tot"] = mu[MESES].apply(pd.to_numeric, errors="coerce").sum(axis=1)
h = mu[(mu.MODALIDAD == "HOMICIDIOS") & (mu.TIPO == "DOLOSOS")]
h = h[h["AÑO"].between(2011, 2017)]
Wm = h.groupby(["INEGI", "AÑO"]).tot.sum().unstack().fillna(0)
Wm = Wm[Wm.sum(axis=1) >= 35]
Fm = np.log1p(Wm)
Fm = Fm.sub(Fm.mean(axis=1), axis=0).div(Fm.std(axis=1).replace(0, np.nan),
                                         axis=0).dropna()
Xm = Fm.values
di(f"Municipios con al menos 35 homicidios en 2011-2017: {len(Xm):,}")
dbm = []
for eps in [0.8, 1.0, 1.2]:
    lab = DBSCAN(eps=eps, min_samples=10).fit(Xm).labels_
    nc, nr = int(len(set(lab) - {-1})), float((lab == -1).mean())
    dbm.append({"eps": eps, "k": nc, "share_ruido": nr})
    di(f"  eps={eps}: {nc} conglomerado(s), {nr:.1%} como ruido")
R["conglomerados"]["dbscan_municipal"] = dbm
R["conglomerados"]["n_municipios_dbscan"] = int(len(Xm))

# ----------------------------------------------- transiciones por quintil
di("\n" + "=" * 74)
di("RUTA ALTERNATIVA: TRANSICIONES ENTRE QUINTILES")
di("=" * 74)
M = pd.read_pickle(f"{SAL}/M.pkl")
K = escala(M)
PEND = float(np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0])


def lpm(d, y, etiq):
    """Modelo lineal de probabilidad con la misma estructura de controles."""
    E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    X = sm.add_constant(pd.concat(
        [pd.DataFrame({"dosis": d.dosis.values}, index=d.index), E, C], axis=1))
    m = sm.WLS(d[y], X, weights=d.factor).fit(cov_type="cluster",
                                              cov_kwds={"groups": d.p19})
    b, se = m.params["dosis"] * K, m.bse["dosis"] * K
    di(f"  {etiq:52s} {b:+9.4f} {se:8.4f} {b/se:+7.2f}  n={len(d):,}")
    return {"etiq": etiq, "b": float(b), "se": float(se), "t": float(b / se),
            "n": int(len(d))}


di(f"{'Desenlace':54s} {'b':>9} {'ee':>8} {'t':>7}")
q1 = M[M.q_ori == 1].copy()
q1["queda"] = (q1.q_des == 1).astype(float)
q5 = M[M.q_ori == 5].copy()
q5["queda"] = (q5.q_des == 5).astype(float)
tr = [lpm(q1, "queda", "Stay in bottom quintile | origin Q1"),
      lpm(q5, "queda", "Stay in top quintile | origin Q5")]

# tipo de cambio: cuánto se mueve la tasa de permanencia cuando la pendiente
# se mueve una unidad, estimado sobre celdas de entidad x cohorte
M["gc"] = pd.cut(M.nac, [1958, 1970, 1978, 1986, 1998],
                 labels=["g1", "g2", "g3", "g4"])
cel = []
for (e, g), s in M.groupby(["p19", "gc"], observed=True):
    if len(s) < 60 or (s.q_ori == 1).sum() < 15:
        continue
    p_ = float(np.polyfit(s.r_ori, s.r_des, 1, w=np.sqrt(s.factor))[0])
    t_ = float((s.loc[s.q_ori == 1, "q_des"] == 1).mean())
    cel.append({"pend": p_, "tasa": t_})
cel = pd.DataFrame(cel)
tc = float(np.polyfit(cel.pend, cel.tasa, 1)[0])
di(f"\n  Celdas entidad x cohorte utilizables: {len(cel)}")
di(f"  Tipo de cambio: 1 unidad de pendiente = {tc:+.3f} en la tasa de permanencia")
emd_tr = 2.8 * tr[0]["se"] / abs(tc)
di(f"  EMD de la transición, traducido a unidades de pendiente: "
   f"{emd_tr:.4f} = {emd_tr/PEND:.0%} de la pendiente")
R["transiciones"] = {"modelos": tr, "tipo_de_cambio": tc,
                     "celdas": int(len(cel)), "emd_pendiente": float(emd_tr),
                     "emd_pct": float(emd_tr / PEND)}

guardar(R, f"{SAL}/resultados.json")
with open(f"{SAL}/log2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
di(f"\nActualizado: {SAL}/resultados.json")
