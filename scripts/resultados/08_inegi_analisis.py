# -*- coding: utf-8 -*-
"""
inegi_analisis.py — la exposición reconstruida sobre defunciones
=================================================================
Sustituye el índice del SESNSP por tasas de homicidio de las estadísticas
vitales del INEGI, con población de CONAPO como denominador. Tres cosas que
la serie anterior no permitía:

  1. Empieza en 1990 y no en 1997, así que las cohortes que tratábamos como
     no expuestas se pueden verificar en lugar de suponer. Es el comentario 7
     del profesor: Sinaloa, Chihuahua y Michoacán ya tenían violencia ligada
     al narcotráfico antes de 1997.
  2. Cuenta víctimas y no expedientes, que es el comentario 3.
  3. A nivel municipal empieza en 1990 y no en 2011, que es la debilidad
     principal del diseño municipal.

Uso:  python -I inegi_analisis.py
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
INE = _r.INE
CON = _r.CON

from base import construir, muestra, efectos_fijos, panel_violencia
from graficas_entregable1 import ABREV

LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def titulo(t):
    di("\n" + "=" * 74)
    di(t)
    di("=" * 74)


# ------------------------------------------------------------------ insumos
pob = pd.read_csv(CON, encoding="latin-1", low_memory=False,
                  usecols=["CLAVE", "CLAVE_ENT", "ANO", "POB_MIT_MUN"])
pob_ent = (pob.groupby(["CLAVE_ENT", "ANO"]).POB_MIT_MUN.sum()
           .rename("pob").reset_index()
           .rename(columns={"CLAVE_ENT": "cve", "ANO": "anio"}))
pob_mun = (pob.rename(columns={"CLAVE": "cvemun", "ANO": "anio",
                               "POB_MIT_MUN": "pob"})[["cvemun", "anio", "pob"]])

ho = pd.read_csv(f"{INE}/hom_entidad_ocurrencia.csv")
hr = pd.read_csv(f"{INE}/hom_entidad_residencia.csv")
hm = pd.read_csv(f"{INE}/hom_municipio_ocurrencia.csv")

E = (pob_ent.merge(ho, on=["cve", "anio"], how="left")
     .assign(homicidios=lambda d: d.homicidios.fillna(0)))
E["tasa"] = E.homicidios / E.pob * 1e5
E = E[E.anio.between(1990, 2020)]

titulo("A. LA SERIE DE DEFUNCIONES POR HOMICIDIO, 1990-2020")
nac = E.groupby("anio").agg(hom=("homicidios", "sum"), pob=("pob", "sum"))
nac["tasa"] = nac.hom / nac.pob * 1e5
di(f"  {'año':>6} {'homicidios':>11} {'tasa':>7}")
for a in [1990, 1995, 1997, 2000, 2004, 2007, 2011, 2017, 2019, 2020]:
    if a in nac.index:
        di(f"  {a:>6} {int(nac.loc[a,'hom']):>11,} {nac.loc[a,'tasa']:>7.1f}")
di("\n  El mínimo histórico y el pico:")
di(f"    mínimo {int(nac.tasa.idxmin())} con {nac.tasa.min():.1f} por 100 000")
di(f"    máximo {int(nac.tasa.idxmax())} con {nac.tasa.max():.1f} por 100 000")

# ------------------------------------------------- comparación con el SESNSP
titulo("B. INEGI CONTRA SESNSP, 1997-2017")
panel, _ = panel_violencia()
ses = panel[["cve", "year", "homicidio_t"]].rename(
    columns={"year": "anio", "homicidio_t": "tasa_ses"})
cmp = E.merge(ses, on=["cve", "anio"]).dropna()
r_niv = float(np.corrcoef(cmp.tasa, cmp.tasa_ses)[0, 1])
brecha = float((cmp.tasa.sum() - cmp.tasa_ses.sum()) / cmp.tasa_ses.sum())
di(f"  Correlación entre las dos tasas, {len(cmp)} celdas entidad-año: {r_niv:+.3f}")
di(f"  INEGI es {100*brecha:+.1f} % respecto al SESNSP en el agregado")
por_ent = cmp.groupby("cve").apply(
    lambda d: (d.tasa.mean() - d.tasa_ses.mean()) / d.tasa_ses.mean())
di(f"  La brecha por entidad va de {100*por_ent.min():+.0f} % "
   f"({ABREV[int(por_ent.idxmin())]}) a {100*por_ent.max():+.0f} % "
   f"({ABREV[int(por_ent.idxmax())]})")
di("  -> No es un factor constante: es error de medición no clásico, como")
di("     decía la sección 3.3 del manuscrito.")

# ------------------------------------- COMENTARIO 7: la violencia previa
titulo("C. ¿YA HABÍA VIOLENCIA ANTES DE 1997? (comentario 7)")
pre = E[E.anio.between(1990, 1997)].groupby("cve").tasa.mean()
post = E[E.anio.between(2007, 2017)].groupby("cve").tasa.mean()
comp = pd.DataFrame({"pre_90_97": pre, "post_07_17": post})
comp["ent"] = [ABREV[int(e)] for e in comp.index]
di(f"  Tasa media nacional 1990-1997: {pre.mean():.1f}   "
   f"2007-2017: {post.mean():.1f}")
di("")
di("  Las entidades que el profesor señaló:")
for e in [25, 8, 16]:
    di(f"    {ABREV[e]:5s} 1990-97 {comp.loc[e,'pre_90_97']:6.1f}   "
       f"2007-17 {comp.loc[e,'post_07_17']:6.1f}   "
       f"(nacional {pre.mean():.1f} y {post.mean():.1f})")
di("")
di("  Las cinco más violentas en 1990-1997:")
for e, r in comp.sort_values("pre_90_97", ascending=False).head(5).iterrows():
    di(f"    {r['ent']:5s} {r['pre_90_97']:6.1f}")
r_pp = float(np.corrcoef(comp.pre_90_97, comp.post_07_17)[0, 1])
di(f"\n  Correlación entre la violencia de 1990-97 y la de 2007-17: {r_pp:+.3f}")

# ------------------------------------------------------ dosis reconstruida
def zscore(s):
    return (s - s.mean()) / s.std()


I_ine = zscore(np.log1p(post))          # intensidad del repunte, INEGI
I_pre = zscore(np.log1p(pre))           # intensidad previa al repunte

df = construir(verbose=False)
M = muestra(df).copy()
M["nac"] = M.nac.astype(int)
M["I_ine"] = M.p19.map(I_ine)
M["I_pre"] = M.p19.map(I_pre)
M["frac"] = [len([y for y in range(n + 10, n + 19) if y >= 2007]) / 9.0
             for n in M.nac]
M["frac_pre"] = [len([y for y in range(n + 10, n + 19) if 1990 <= y <= 1997]) / 9.0
                 for n in M.nac]
M["dosis_ine"] = M.I_ine * M.frac
M["dosis_pre"] = M.I_pre * M.frac_pre
M = M.dropna(subset=["dosis_ine", "dosis_pre"])
PEND = float(np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0])
di(f"\n  Encuestados con ventana en 1990-1997: "
   f"{100*(M.frac_pre>0).mean():.1f} % de la muestra")


def estimar(d, dosis, extra=None, etiq="", esc=None):
    base = pd.DataFrame({"r_ori": d.r_ori.values, "dosis": d[dosis].values,
                         "b3": (d.r_ori * d[dosis]).values}, index=d.index)
    piezas = [base] + efectos_fijos(d)
    if extra is not None:
        piezas.append(extra)
    X = sm.add_constant(pd.concat(piezas, axis=1))
    m = sm.WLS(d.r_des, X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d.p19})
    k = 1.0 if esc is None else esc
    b, se = m.params["b3"] * k, m.bse["b3"] * k
    di(f"  {etiq:50s} {b:+9.4f} {se:8.4f} {b/se:+7.2f} {2.8*se/PEND:7.1%}")
    return {"etiq": etiq, "b3": float(b), "se": float(se),
            "t": float(b / se), "emd_pct": float(2.8 * se / PEND)}


titulo("D. EL MODELO CON LA DOSIS DE DEFUNCIONES")
di(f"  {'Especificación':48s} {'b3':>9} {'ee':>8} {'t':>7} {'EMD':>7}")
res = []
res.append(estimar(M, "dosis_ine", None, "Dosis INEGI (defunciones)"))
res.append(estimar(M, "dosis_pre", None,
                   "PLACEBO: dosis de violencia previa 1990-97"))
pre_ctrl = pd.DataFrame({"dpre": M.dosis_pre.values,
                         "dpre_r": (M.dosis_pre * M.r_ori).values},
                        index=M.index)
res.append(estimar(M, "dosis_ine", pre_ctrl,
                   "Dosis INEGI + control de violencia previa"))

R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
R["inegi"] = {
    "serie_nacional": {str(int(a)): float(v) for a, v in nac.tasa.items()},
    "corr_con_sesnsp": r_niv, "brecha_agregada": brecha,
    "brecha_min": float(por_ent.min()), "brecha_max": float(por_ent.max()),
    "pre_90_97": {str(int(k)): float(v) for k, v in pre.items()},
    "post_07_17": {str(int(k)): float(v) for k, v in post.items()},
    "corr_pre_post": r_pp,
    "share_ventana_pre": float((M.frac_pre > 0).mean()),
    "estimaciones": res,
}
tmp = f"{SAL}/resultados.json.tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2, ensure_ascii=False, default=str)
os.replace(tmp, f"{SAL}/resultados.json")
E.to_csv(f"{SAL}/panel_homicidios_inegi.csv", index=False)
with open(f"{SAL}/log_inegi.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
di(f"\nEscrito en resultados.json y {SAL}/panel_homicidios_inegi.csv")
