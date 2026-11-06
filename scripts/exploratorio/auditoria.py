# -*- coding: utf-8 -*-
"""Auditoría adversaria del modelo: supuestos vulnerables, cuantificados."""
import sys, numpy as np, pandas as pd
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from graficas_entregable1 import poblacion_anual, cargar_sesnsp, indice_pca, ORIGEN
import pyreadstat, statsmodels.api as sm

SES = _r.SES
MUN = _r.MUN
E   = _r.EMO + "/"
DEST = ([f"p94{c}" for c in "abcdefg"] + [f"p96{c}" for c in "abcdefghijklmnopqr"]
        + [f"p97{c}" for c in "abcdefghijklmn"])

pob = poblacion_anual(range(1997, 2025))
panel, _ = cargar_sesnsp(SES, pob)
idx = panel.set_index(["cve", "year"]).indice
intens = panel[(panel.year >= 2007) & (panel.year <= 2017)].groupby("cve").indice.mean()

df, _ = pyreadstat.read_dta(E + "entrevistado_2023.dta", apply_value_formats=False)
hg, _ = pyreadstat.read_dta(E + "hogar_2023.dta", apply_value_formats=False)
df["nac"] = 2023 - df.edad
df["idx_ori"], _ = indice_pca(df, ORIGEN, numericas=["p30"])
df["idx_des"], _ = indice_pca(df, DEST, numericas=["p99"])
df["corresid"] = df["index"].isin(hg[hg.p5 == 4]["index"]).astype(int)
df["migro"] = (df.p19 != df.entidad).astype(int)
df["mujer"] = (df.sexo == 2).astype(int)
df["rural_ok"]  = (df.p21 == 5).astype(int)          # INEGI: menos de 2 500 hab.
df["rural_malo"] = df.p21.isin([3, 4, 5]).astype(int)  # lo que usamos antes

def rank_p(x, w, by):
    o = pd.Series(np.nan, index=x.index)
    for _, i in x.groupby(by).groups.items():
        xi, wi = x.loc[i], w.loc[i]
        s = np.argsort(xi.values); ws = wi.values[s]
        o.loc[xi.index[s]] = (np.cumsum(ws) - .5 * ws) / ws.sum()
    return o

# dos normalizaciones: la que usamos (bandas de 10 años) y una fina (año simple)
df["r_ori"] = rank_p(df.idx_ori, df.factor, df.cohorte)
df["r_des"] = rank_p(df.idx_des, df.factor, df.cohorte)
df["r_ori_f"] = rank_p(df.idx_ori, df.factor, df.nac)
df["r_des_f"] = rank_p(df.idx_des, df.factor, df.nac)

# dos dosis: la del modelo y una que usa la violencia realmente vivida
df["frac"] = df.nac.apply(lambda n: len([y for y in range(n+10, n+19) if y >= 2007]) / 9)
df["intens"] = df.p19.map(intens)
df["dosis"] = df.intens * df.frac
def real(r):
    yy = [y for y in range(r.nac+10, r.nac+19) if 1997 <= y <= 2017]
    v = [idx[(r.p19, y)] for y in yy if (r.p19, y) in idx.index]
    return (np.mean(v) * len(yy)/9) if v else 0.0
df["dosis_real"] = df.apply(real, axis=1)

M = df[(df.p19 <= 32) & (df.migro == 0)].dropna(subset=["intens"]).copy()

def ddd(d, ro, rd, dos, etiq):
    Ed = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    Cd = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    X = sm.add_constant(pd.concat([
        pd.DataFrame({"r_ori": d[ro].values, "dosis": d[dos].values,
                      "b3": (d[ro]*d[dos]).values}, index=d.index),
        Ed, Cd, Ed.mul(d[ro], axis=0).add_prefix("ri_"),
        Cd.mul(d[ro], axis=0).add_prefix("rc_")], axis=1))
    m = sm.WLS(d[rd], X, weights=d.factor).fit(cov_type="cluster",
                                               cov_kwds={"groups": d.p19})
    b, se = m.params["b3"], m.bse["b3"]
    k = d.groupby("p19").intens.first().std()
    print(f"  {etiq:46s} b3={b*k:+.4f} (ee {se*k:.4f})  t={b/se:+.2f}")
    return b*k, se*k

print("="*80)
print("1. SENSIBILIDAD A DECISIONES QUE TOMAMOS SIN PENSARLO MUCHO")
print("   (todo reescalado a desviaciones estandar de intensidad)")
print("="*80)
b0, s0 = ddd(M, "r_ori", "r_des", "dosis", "Especificacion publicada")
ddd(M, "r_ori_f", "r_des_f", "dosis", "Rangos normalizados por anio simple")
ddd(M, "r_ori", "r_des", "dosis_real", "Dosis = violencia realmente vivida")
ddd(M, "r_ori_f", "r_des_f", "dosis_real", "Ambos cambios a la vez")

print("\n" + "="*80)
print("2. EL ERROR DE CODIFICACION DE 'RURAL'")
print("="*80)
print(f"  Definicion INEGI (menos de 2 500 hab., p21=5):  {df.rural_ok.mean():.1%}")
print(f"  Lo que usamos en el diagnostico (p21 in 3,4,5): {df.rural_malo.mean():.1%}")
print("  Heterogeneidad con la definicion correcta:")
for nom, sub in [("Origen rural (<2 500 hab.)", M[M.rural_ok == 1]),
                 ("Origen urbano", M[M.rural_ok == 0]),
                 ("Mujeres", M[M.mujer == 1]), ("Hombres", M[M.mujer == 0])]:
    try: ddd(sub, "r_ori", "r_des", "dosis", nom)
    except Exception as ex: print(f"    {nom}: no estimable")

print("\n" + "="*80)
print("3. ATENUACION POR USAR EL ESTADO Y NO EL MUNICIPIO")
print("="*80)
mu = pd.read_csv(MUN, encoding="latin-1", low_memory=False)
MES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO",
       "SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
mu["tot"] = mu[MES].apply(pd.to_numeric, errors="coerce").sum(axis=1)
h = mu[(mu.MODALIDAD == "HOMICIDIOS") & (mu.TIPO == "DOLOSOS")]
g = h.groupby(["AÑO", "INEGI", "MUNICIPIO"]).tot.sum().reset_index()
g = g[g.AÑO.between(2011, 2017)]
# tasa aproximada no es posible sin poblacion municipal: se usa el conteo en logs
g["lv"] = np.log1p(g.tot)
ve = g.groupby("INEGI").lv.transform("mean").var()
vt = g.lv.var()
print(f"  Municipios-anio observados: {len(g):,}")
print(f"  Varianza del homicidio municipal (en logs): {vt:.3f}")
print(f"    entre estados {ve/vt:.0%}   |   dentro de estados {1-ve/vt:.0%}")
print(f"  Factor de atenuacion aproximado si el tratamiento real fuera municipal:")
print(f"    el coeficiente estimado seria ~{ve/vt:.0%} del verdadero")
print(f"    es decir, un efecto real de X se veria como {ve/vt:.2f}X")
