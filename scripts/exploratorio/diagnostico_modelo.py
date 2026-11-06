# -*- coding: utf-8 -*-
"""Diagnósticos para decidir la especificación del Entregable 2."""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graficas_entregable1 import (poblacion_anual, cargar_sesnsp, indice_pca,
                                  ORIGEN, ABREV)
import pyreadstat
import statsmodels.api as sm

SES = _r.SES
EMO = _r.EMO

pob = poblacion_anual(range(1997, 2025))
panel, _ = cargar_sesnsp(SES, pob)
clave = panel.set_index(["cve", "year"]).indice

df, _ = pyreadstat.read_dta(os.path.join(EMO, "entrevistado_2023.dta"),
                            apply_value_formats=False)
h, _ = pyreadstat.read_dta(os.path.join(EMO, "hogar_2023.dta"),
                           apply_value_formats=False)
df["nac"] = 2023 - df.edad
df["idx_ori"], _ = indice_pca(df, ORIGEN, numericas=["p30"])
DEST = ([f"p94{c}" for c in "abcdefg"] + [f"p96{c}" for c in "abcdefghijklmnopqr"]
        + [f"p97{c}" for c in "abcdefghijklmn"])
df["idx_des"], _ = indice_pca(df, DEST, numericas=["p99"])
cor = h[h.p5 == 4].groupby("index").size().rename("npad")
df = df.merge(cor, left_on="index", right_index=True, how="left")
df["corresid"] = df.npad.fillna(0).gt(0).astype(int)
df["coh"] = pd.cut(df.nac, [1958, 1984, 1988, 1992, 1998], labels=["D","C","B","A"])
df["migro"] = (df.p19 != df.entidad).astype(int)

def rank_p(x, w, by):
    out = pd.Series(np.nan, index=x.index)
    for _, i in x.groupby(by).groups.items():
        xi, wi = x.loc[i], w.loc[i]
        o = np.argsort(xi.values); ws = wi.values[o]
        out.loc[xi.index[o]] = (np.cumsum(ws) - .5*ws)/ws.sum()
    return out
df["r_ori"] = rank_p(df.idx_ori, df.factor, df.cohorte)
df["r_des"] = rank_p(df.idx_des, df.factor, df.cohorte)

# ---- exposición: años de la ventana 10-18 posteriores a 2007, y el índice
df["ven_post07"] = df.nac.apply(lambda n: len([y for y in range(n+10, n+19) if y >= 2007]))
def expo(r):
    yy = [y for y in range(r.nac+10, r.nac+19) if 1997 <= y <= 2017]
    v = [clave[(r.p19, y)] for y in yy if (r.p19, y) in clave.index]
    return (np.mean(v) if v else np.nan), len(yy)
df[["exp_idx","cub"]] = df.apply(lambda r: pd.Series(expo(r)), axis=1)

print("="*70)
print("1. COBERTURA DE LA VENTANA FORMATIVA POR AÑO DE NACIMIENTO")
c = df.groupby("nac").agg(n=("cub","size"), cub=("cub","mean")).round(1)
print("  primer año con 9/9 años cubiertos:", c[c.cub>=9].index.min())
print("  primer año con ventana que toca 2007:", df[df.ven_post07>0].nac.min())
print(c.loc[[1979,1984,1986,1987,1990,1995,1998]].to_string())

print("\n2. TAMAÑO DE CELDA entidad x cohorte")
cc = df[df.p19<=32].groupby(["p19","coh"], observed=True).size()
print(f"  celdas: {len(cc)} | mediana {cc.median():.0f} | <30 obs: {(cc<30).sum()}")
ca = df[(df.p19<=32)&(df.coh=='A')].groupby("p19").size()
print(f"  cohorte A: {len(ca)} entidades, mediana {ca.median():.0f}, mínimo {ca.min()}")

print("\n3. VARIACIÓN DE LA EXPOSICIÓN: descomposición")
m = df[(df.p19<=32)&df.exp_idx.notna()]
vt = m.exp_idx.var()
ve = m.groupby("p19").exp_idx.transform("mean").var()
vc = m.groupby("nac").exp_idx.transform("mean").var()
print(f"  varianza total {vt:.4f} | entre entidades {ve:.4f} ({ve/vt:.0%})"
      f" | entre cohortes {vc:.4f} ({vc/vt:.0%})")
resid = m.exp_idx - m.groupby("p19").exp_idx.transform("mean") \
            - m.groupby("nac").exp_idx.transform("mean") + m.exp_idx.mean()
print(f"  residual tras absorber entidad y año de nacimiento: {resid.var():.4f}"
      f" ({resid.var()/vt:.0%})  <-- la que identifica el efecto")

# ---------------------------------------------------------------- 4. DDD
def ddd(d, etiqueta, excl_corresid=False, solo_no_migro=True):
    d = d[d.p19 <= 32].copy()
    if solo_no_migro: d = d[d.migro == 0]
    if excl_corresid: d = d[d.corresid == 0]
    d = d.dropna(subset=["exp_idx","r_ori","r_des"])
    E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    X = pd.concat([
        pd.DataFrame({"r_ori": d.r_ori.values,
                      "exp": d.exp_idx.values,
                      "r_ori_x_exp": (d.r_ori*d.exp_idx).values}, index=d.index),
        E, C,
        E.mul(d.r_ori, axis=0).add_prefix("ri_"),     # pendiente propia por entidad
        C.mul(d.r_ori, axis=0).add_prefix("ri_"),     # pendiente propia por cohorte
    ], axis=1)
    X = sm.add_constant(X)
    mod = sm.WLS(d.r_des, X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d.p19})
    b, se = mod.params["r_ori_x_exp"], mod.bse["r_ori_x_exp"]
    print(f"  {etiqueta:38s} n={len(d):5d}  beta3={b:+.4f}  ee={se:.4f}  "
          f"t={b/se:+.2f}  p={mod.pvalues['r_ori_x_exp']:.3f}")
    return b, se

print("\n4. TRIPLE DIFERENCIA: coeficiente de r_origen x exposicion")
print("   (efectos fijos de entidad y de año de nacimiento, mas pendiente propia de cada uno)")
ddd(df, "muestra completa")
ddd(df, "excluyendo corresidentes", excl_corresid=True)
ddd(df[df.nac>=1987], "solo cohortes con ventana completa")

# ------------------------------------------- 5. tendencias previas diferenciales
print("\n5. PRUEBA DE TENDENCIAS PREVIAS DIFERENCIALES")
print("   Nacidos <=1986: su ventana formativa termina antes o apenas en 2007.")
print("   Se les asigna la intensidad FUTURA de su entidad (promedio 2007-2017)")
print("   y se prueba si la pendiente ya subia mas rapido donde despues hubo mas violencia.")
fut = panel[(panel.year>=2007)&(panel.year<=2017)].groupby("cve").indice.mean()
pre = df[(df.nac<=1986)&(df.p19<=32)&(df.migro==0)].copy()
pre["fut"] = pre.p19.map(fut)
pre["t"] = (pre.nac - pre.nac.mean())/10          # decadas de nacimiento
pre = pre.dropna(subset=["fut","r_ori","r_des"])
E = pd.get_dummies(pre.p19.astype(int), prefix="e", drop_first=True).astype(float)
X = pd.concat([
    pd.DataFrame({"r_ori":pre.r_ori.values,"t":pre.t.values,
                  "r_ori_x_t":(pre.r_ori*pre.t).values,
                  "r_ori_x_fut":(pre.r_ori*pre.fut).values,
                  "r_ori_x_t_x_fut":(pre.r_ori*pre.t*pre.fut).values,
                  "t_x_fut":(pre.t*pre.fut).values}, index=pre.index),
    E, E.mul(pre.r_ori,axis=0).add_prefix("ri_")], axis=1)
X = sm.add_constant(X)
mp = sm.WLS(pre.r_des, X, weights=pre.factor).fit(
    cov_type="cluster", cov_kwds={"groups": pre.p19})
b, se = mp.params["r_ori_x_t_x_fut"], mp.bse["r_ori_x_t_x_fut"]
print(f"  n={len(pre)}  triple interaccion placebo = {b:+.4f}  ee={se:.4f}  "
      f"t={b/se:+.2f}  p={mp.pvalues['r_ori_x_t_x_fut']:.3f}")
print(f"  tendencia comun (r_ori x t) = {mp.params['r_ori_x_t']:+.4f}"
      f"  ee={mp.bse['r_ori_x_t']:.4f}")
print("\n  Lectura: la tendencia comun capta el ciclo de vida; lo que debe ser")
print("  indistinguible de cero es la TRIPLE interaccion con la intensidad futura.")
