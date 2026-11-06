# -*- coding: utf-8 -*-
"""
Dos pruebas de robustez pedidas tras la auditoría.

Prueba 1. Destino educativo
  La escolaridad está terminada hacia los 25 años, así que no depende de la
  etapa de vida ni de vivir con los padres. Si el nulo del modelo principal
  viniera de medir el destino demasiado pronto, aquí deberíamos ver algo.

Prueba 2. Variación municipal dentro del estado
  El 70 % de la variación del homicidio municipal está dentro de los estados.
  Si nuestro nulo fuera un artefacto de medir el tratamiento al nivel
  equivocado, al comparar municipios del mismo estado deberíamos ver algo.
  La serie municipal del SESNSP no trae población, así que la intensidad
  relativa se construye como participación en homicidios del estado dividida
  entre participación en población del estado (esta última aproximada con los
  factores de expansión de la propia encuesta).
"""
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
MES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO",
       "SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]

# ------------------------------------------------------------------ insumos
pob = poblacion_anual(range(1997, 2025))
panel, _ = cargar_sesnsp(SES, pob)
intens = panel[(panel.year >= 2007) & (panel.year <= 2017)].groupby("cve").indice.mean()

df, meta = pyreadstat.read_dta(E + "entrevistado_2023.dta", apply_value_formats=False)
hg, _ = pyreadstat.read_dta(E + "hogar_2023.dta", apply_value_formats=False)
df["nac"] = 2023 - df.edad
df["idx_ori"], _ = indice_pca(df, ORIGEN, numericas=["p30"])
df["idx_des"], _ = indice_pca(df, DEST, numericas=["p99"])
df["corresid"] = df["index"].isin(hg[hg.p5 == 4]["index"]).astype(int)
df["migro"] = (df.p19 != df.entidad).astype(int)
df["rural"] = (df.p21 == 5).astype(int)          # INEGI: menos de 2 500 hab.
df["frac"] = df.nac.apply(lambda n: len([y for y in range(n+10, n+19) if y >= 2007]) / 9)
df["intens"] = df.p19.map(intens)
df["dosis"] = df.intens * df.frac
df["coh"] = pd.cut(df.nac, [1958, 1984, 1988, 1992, 1998], labels=["D","C","B","A"])

print("Etiquetas de nivel educativo (p9):")
for k, v in sorted(meta.variable_value_labels.get("p9", {}).items()):
    print(f"   {k}: {v}")

# ---------------------------------------------------- escolaridad en niveles
# Se usa el nivel declarado como escala ordinal; los códigos de no respuesta
# (8, 9, 98, 99) quedan como faltantes.
def nivel(s):
    v = pd.to_numeric(s, errors="coerce")
    return v.where(v <= 9)

df["ed_yo"]  = nivel(df.p9)
df["ed_pa"]  = nivel(df.p42a)
df["ed_ma"]  = nivel(df.p42b)
df["ed_pad"] = df[["ed_pa", "ed_ma"]].max(axis=1)     # el mayor de los dos
print(f"\nCobertura: propia {df.ed_yo.notna().mean():.0%} | "
      f"de al menos un padre {df.ed_pad.notna().mean():.0%}")

def rank_p(x, w, by):
    o = pd.Series(np.nan, index=x.index)
    ok = x.notna()
    for _, i in x[ok].groupby(by[ok]).groups.items():
        xi, wi = x.loc[i], w.loc[i]
        s = np.argsort(xi.values); ws = wi.values[s]
        o.loc[xi.index[s]] = (np.cumsum(ws) - .5 * ws) / ws.sum()
    return o

df["r_ori"]    = rank_p(df.idx_ori, df.factor, df.cohorte)
df["r_des"]    = rank_p(df.idx_des, df.factor, df.cohorte)
df["r_des_ed"] = rank_p(df.ed_yo,  df.factor, df.cohorte)
df["r_ori_ed"] = rank_p(df.ed_pad, df.factor, df.cohorte)

M = df[(df.p19 <= 32) & (df.migro == 0)].dropna(subset=["intens"]).copy()
K = M.groupby("p19").intens.first().std()          # para reescalar a d.e.

def ddd(d, ro, rd, dos="dosis", etiq="", clust="p19"):
    d = d.dropna(subset=[ro, rd, dos])
    Ed = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    Cd = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    X = sm.add_constant(pd.concat([
        pd.DataFrame({"r_ori": d[ro].values, "dosis": d[dos].values,
                      "b3": (d[ro]*d[dos]).values}, index=d.index),
        Ed, Cd, Ed.mul(d[ro], axis=0).add_prefix("ri_"),
        Cd.mul(d[ro], axis=0).add_prefix("rc_")], axis=1))
    m = sm.WLS(d[rd], X, weights=d.factor).fit(cov_type="cluster",
                                               cov_kwds={"groups": d[clust]})
    b, se = m.params["b3"]*K, m.bse["b3"]*K
    pend = np.polyfit(d[ro], d[rd], 1, w=np.sqrt(d.factor))[0]
    print(f"  {etiq:44s} n={len(d):5d} b3={b:+.4f} ({se:.4f}) t={b/se:+.2f} "
          f"| pendiente base {pend:.3f} | EMD {2.8*se/pend:.0%}")
    return b, se

print("\n" + "="*92)
print("PRUEBA 1 — DESTINO EDUCATIVO")
print("="*92)
ddd(M, "r_ori", "r_des", etiq="Referencia: activos -> activos")
ddd(M, "r_ori", "r_des_ed", etiq="Activos -> escolaridad propia")
ddd(M, "r_ori_ed", "r_des_ed", etiq="Escolaridad de los padres -> propia")
print("  Solo la cohorte expuesta y sus vecinas (nacidos desde 1985):")
ddd(M[M.nac >= 1985], "r_ori", "r_des_ed", etiq="  Activos -> escolaridad, 1985 en adelante")

print("\n" + "="*92)
print("PRUEBA 2 — VARIACION MUNICIPAL DENTRO DEL ESTADO")
print("="*92)
mu = pd.read_csv(MUN, encoding="latin-1", low_memory=False)
mu["tot"] = mu[MES].apply(pd.to_numeric, errors="coerce").sum(axis=1)
h = mu[(mu.MODALIDAD == "HOMICIDIOS") & (mu.TIPO == "DOLOSOS")]
hm = h[h["AÑO"].between(2011, 2017)].groupby("INEGI").tot.sum().rename("hom")
hm = hm.reset_index(); hm["edo"] = (hm.INEGI // 1000).astype(int)
hm["sh_hom"] = hm.hom / hm.groupby("edo").hom.transform("sum")

# participación poblacional aproximada con los factores de la encuesta
A = M[M.coh == "A"].copy()
popm = A.groupby("p20_COD").agg(w=("factor","sum"), n=("factor","size")).reset_index()
popm["INEGI"] = pd.to_numeric(popm.p20_COD, errors="coerce")
popm["edo"] = (popm.INEGI // 1000).astype("Int64")
popm["sh_pob"] = popm.w / popm.groupby("edo").w.transform("sum")

mm = popm.merge(hm[["INEGI","sh_hom","hom"]], on="INEGI", how="inner")
mm = mm[(mm.n >= 15) & (mm.sh_pob > 0) & (mm.sh_hom > 0)].copy()
mm["rel"] = np.log(mm.sh_hom / mm.sh_pob)         # intensidad relativa al estado
mm["rel"] = (mm.rel - mm.rel.mean()) / mm.rel.std()
print(f"  Municipios usables: {len(mm)} en {mm.edo.nunique()} estados "
      f"(al menos 15 entrevistados de la cohorte A)")
print(f"  Cubren {mm.n.sum()} de {len(A)} personas de la cohorte A")
print(f"  Intensidad relativa: d.e. 1 por construccion, rango "
      f"[{mm.rel.min():.2f}, {mm.rel.max():.2f}]")

A2 = A.merge(mm[["p20_COD","rel"]], on="p20_COD", how="inner").dropna(subset=["r_ori","r_des"])
est = A2.groupby("p19").size()
A2 = A2[A2.p19.isin(est[est >= 40].index)]
print(f"  Muestra de la prueba: {len(A2)} personas, {A2.p19.nunique()} estados, "
      f"{A2.p20_COD.nunique()} municipios")

Ed = pd.get_dummies(A2.p19.astype(int), prefix="e", drop_first=True).astype(float)
X = sm.add_constant(pd.concat([
    pd.DataFrame({"r_ori": A2.r_ori.values, "rel": A2.rel.values,
                  "b3": (A2.r_ori*A2.rel).values}, index=A2.index),
    Ed, Ed.mul(A2.r_ori, axis=0).add_prefix("ri_")], axis=1))
m = sm.WLS(A2.r_des, X, weights=A2.factor).fit(cov_type="cluster",
                                               cov_kwds={"groups": A2.p20_COD})
b, se = m.params["b3"], m.bse["b3"]
pend = np.polyfit(A2.r_ori, A2.r_des, 1, w=np.sqrt(A2.factor))[0]
print(f"\n  Destino = activos:     b3={b:+.4f} ({se:.4f}) t={b/se:+.2f} "
      f"| pendiente base {pend:.3f}")
A3 = A2.dropna(subset=["r_des_ed"])
Ed = pd.get_dummies(A3.p19.astype(int), prefix="e", drop_first=True).astype(float)
X = sm.add_constant(pd.concat([
    pd.DataFrame({"r_ori": A3.r_ori.values, "rel": A3.rel.values,
                  "b3": (A3.r_ori*A3.rel).values}, index=A3.index),
    Ed, Ed.mul(A3.r_ori, axis=0).add_prefix("ri_")], axis=1))
m2 = sm.WLS(A3.r_des_ed, X, weights=A3.factor).fit(cov_type="cluster",
                                                   cov_kwds={"groups": A3.p20_COD})
b2, se2 = m2.params["b3"], m2.bse["b3"]
print(f"  Destino = escolaridad: b3={b2:+.4f} ({se2:.4f}) t={b2/se2:+.2f}")
print("\n  Advertencia: sin cohortes de contraste esto es una comparacion")
print("  transversal entre municipios, no un diseno causal. Sirve como")
print("  diagnostico de medicion, no como estimacion del efecto.")
