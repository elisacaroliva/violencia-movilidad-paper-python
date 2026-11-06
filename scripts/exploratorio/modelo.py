# -*- coding: utf-8 -*-
"""
Modelo del Entregable 2
=======================
Triple diferencia sobre la pendiente rango-rango.

Dosis_ec = Intensidad_e x (años de la ventana 10-18 posteriores a 2007)/9
  Intensidad_e : índice promedio 2007-2017 de la entidad de residencia a los 14
  El componente de cohorte es mecánico: depende sólo del año de nacimiento.

rango_des = b1*rango_ori + b2*Dosis + b3*(rango_ori x Dosis)
            + EF_ent + EF_nac + EF_ent*rango_ori + EF_nac*rango_ori + e

b3 es el parámetro: cambio en la pendiente origen-destino por unidad de dosis.
"""
import os, sys, numpy as np, pandas as pd
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from graficas_entregable1 import (poblacion_anual, cargar_sesnsp, indice_pca,
                                  ORIGEN, ABREV)
import pyreadstat, statsmodels.api as sm
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

SES = _r.SES
EMO = _r.EMO
OUT = _r.OUT
DEST = ([f"p94{c}" for c in "abcdefg"] + [f"p96{c}" for c in "abcdefghijklmnopqr"]
        + [f"p97{c}" for c in "abcdefghijklmn"])

# ----------------------------------------------------------------- datos
def construir():
    pob = poblacion_anual(range(1997, 2025))
    panel, _ = cargar_sesnsp(SES, pob)
    intens = panel[(panel.year >= 2007) & (panel.year <= 2017)].groupby("cve").indice.mean()

    df, _ = pyreadstat.read_dta(f"{EMO}/entrevistado_2023.dta", apply_value_formats=False)
    hg, _ = pyreadstat.read_dta(f"{EMO}/hogar_2023.dta", apply_value_formats=False)
    df["nac"] = 2023 - df.edad
    df["idx_ori"], v1 = indice_pca(df, ORIGEN, numericas=["p30"])
    df["idx_des"], v2 = indice_pca(df, DEST, numericas=["p99"])
    df["corresid"] = df["index"].isin(hg[hg.p5 == 4]["index"]).astype(int)
    df["migro"] = (df.p19 != df.entidad).astype(int)
    df["mujer"] = (df.sexo == 2).astype(int)
    # INEGI define rural como localidad de menos de 2 500 habitantes, que en
    # p21 es únicamente el código 5. Incluir 3 y 4 metía localidades de hasta
    # 99 999 habitantes y clasificaba como rural al 68 % de la muestra.
    df["rural"] = (df.p21 == 5).astype(int)

    def rk(x, w, by):
        o = pd.Series(np.nan, index=x.index)
        for _, i in x.groupby(by).groups.items():
            xi, wi = x.loc[i], w.loc[i]
            s = np.argsort(xi.values); ws = wi.values[s]
            o.loc[xi.index[s]] = (np.cumsum(ws) - .5 * ws) / ws.sum()
        return o
    df["r_ori"] = rk(df.idx_ori, df.factor, df.cohorte)
    df["r_des"] = rk(df.idx_des, df.factor, df.cohorte)
    df["q_ori"] = np.ceil(df.r_ori * 5).clip(1, 5).astype(int)
    df["q_des"] = np.ceil(df.r_des * 5).clip(1, 5).astype(int)

    # dosis
    df["frac"] = df.nac.apply(lambda n: len([y for y in range(n+10, n+19) if y >= 2007]) / 9)
    df["intens"] = df.p19.map(intens)
    df["dosis"] = df.intens * df.frac
    print(f"Índices: origen {v1:.1%} de varianza, destino {v2:.1%}")
    return df.dropna(subset=["intens", "r_ori", "r_des"])

# ------------------------------------------------------- estimación DDD
def ddd(d, extra=None, cl="p19"):
    """Devuelve el modelo con b3 = coeficiente de r_ori x dosis."""
    E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    base = pd.DataFrame({"r_ori": d.r_ori.values, "dosis": d.dosis.values,
                         "b3": (d.r_ori * d.dosis).values}, index=d.index)
    piezas = [base, E, C, E.mul(d.r_ori, axis=0).add_prefix("ri_"),
              C.mul(d.r_ori, axis=0).add_prefix("rc_")]
    if extra is not None: piezas.append(extra)
    X = sm.add_constant(pd.concat(piezas, axis=1))
    return sm.WLS(d.r_des, X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d[cl]})

def linea(nombre, m, n):
    b, se = m.params["b3"], m.bse["b3"]
    print(f"  {nombre:42s} n={n:5d}  b3={b:+.4f} ({se:.4f})  "
          f"t={b/se:+.2f}  IC95=[{b-1.96*se:+.3f},{b+1.96*se:+.3f}]")
    return b, se

# ------------------------------------------------------------------ main
df = construir()
M = df[(df.p19 <= 32) & (df.migro == 0)].copy()
print(f"\nMuestra analítica: {len(M)} (no migraron de entidad desde los 14 años)")

print("\n" + "="*78)
print("RESULTADO PRINCIPAL — b3 = cambio en la pendiente por unidad de dosis")
print("="*78)
m0 = ddd(M); b0, se0 = linea("Especificación principal", m0, len(M))
m1 = ddd(M[M.corresid == 0]); linea("Excluyendo corresidentes", m1, (M.corresid==0).sum())
m2 = ddd(df[df.p19 <= 32]); linea("Incluyendo a quienes migraron", m2, (df.p19<=32).sum())

# robustez: dosis sólo con homicidio del INEGI (proxy: homicidio del SESNSP)
pob = poblacion_anual(range(1997, 2025)); panel, _ = cargar_sesnsp(SES, pob)
ih = panel[(panel.year>=2007)&(panel.year<=2017)].groupby("cve").homicidio_t.mean()
ih = (ih - ih.mean())/ih.std()
Mh = M.copy(); Mh["dosis"] = Mh.p19.map(ih) * Mh.frac
linea("Dosis sólo con homicidio doloso", ddd(Mh.dropna(subset=["dosis"])),
      len(Mh.dropna(subset=["dosis"])))

# ---------------------------------------------------------- potencia
# Dos escalas distintas, y conviene no confundirlas. "Por unidad de dosis" es
# el coeficiente crudo: una unidad de dosis es pasar de nunca expuesto a la
# entidad más violenta durante toda la adolescencia, un cambio enorme. La
# escala interpretable es por desviación estándar de intensidad entre
# entidades, que es K veces menor. Lo que se reporta afuera es la segunda.
K = M.groupby("p19").intens.first().std()
mde = 2.8 * se0
pend = np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0]
print(f"\nPotencia (pendiente base {pend:.3f}; d.e. de intensidad {K:.3f})")
print(f"  por unidad de dosis:        ee={se0:.4f} -> EMD {mde:.3f} "
      f"({mde/pend:.0%} de la pendiente)")
print(f"  por d.e. de intensidad:     ee={se0*K:.4f} -> EMD {mde*K:.3f} "
      f"({mde*K/pend:.0%} de la pendiente)   <- la que se reporta")

# ------------------------------------------- inferencia por permutación
rng = np.random.default_rng(11); ents = sorted(M.p19.unique())
print("\nInferencia por permutación (reasigna la intensidad entre entidades)")
# Frisch-Waugh: se proyecta una sola vez el bloque de efectos fijos y luego
# cada permutación sólo requiere residualizar las dos columnas que cambian.
E = pd.get_dummies(M.p19.astype(int), prefix="e", drop_first=True).astype(float)
C = pd.get_dummies(M.nac.astype(int), prefix="c", drop_first=True).astype(float)
FE = sm.add_constant(pd.concat([pd.DataFrame({"r_ori": M.r_ori.values}, index=M.index),
     E, C, E.mul(M.r_ori,axis=0).add_prefix("ri_"),
     C.mul(M.r_ori,axis=0).add_prefix("rc_")], axis=1)).to_numpy()
sw = np.sqrt(M.factor.to_numpy())
FEw = FE * sw[:, None]
Q, _ = np.linalg.qr(FEw)
def resid(v):            # residual de v respecto del bloque de efectos fijos
    vw = v * sw
    return vw - Q @ (Q.T @ vw)
ry = resid(M.r_des.to_numpy()); ro = M.r_ori.to_numpy()
def b3_rapido(dos):
    A = np.column_stack([resid(dos), resid(ro * dos)])
    return np.linalg.lstsq(A, ry, rcond=None)[0][1]
intens_vec = np.array([M[M.p19 == e].intens.iloc[0] for e in ents])
idx = {e: (M.p19 == e).to_numpy() for e in ents}
frac = M.frac.to_numpy()
nulos = []
for _ in range(2000):
    perm = rng.permutation(intens_vec)
    dos = np.empty(len(M))
    for e, v in zip(ents, perm): dos[idx[e]] = v
    nulos.append(b3_rapido(dos * frac))
nulos = np.array(nulos); p_ri = (np.abs(nulos) >= abs(b0)).mean()
print(f"  {len(nulos)} permutaciones | p = {p_ri:.3f} | "
      f"nulo en [{np.percentile(nulos,2.5):+.3f}, {np.percentile(nulos,97.5):+.3f}]")

# --------------------------------------------------------- heterogeneidad
print("\nHeterogeneidad (b3 por submuestra)")
for nom, sub in [("Mujeres", M[M.mujer==1]), ("Hombres", M[M.mujer==0]),
                 ("Origen rural", M[M.rural==1]), ("Origen urbano", M[M.rural==0]),
                 ("Origen en Q1 y Q2", M[M.q_ori<=2]), ("Origen en Q4 y Q5", M[M.q_ori>=4])]:
    try: linea(nom, ddd(sub), len(sub))
    except Exception as e: print(f"  {nom}: no estimable ({e})")

# ------------------------------------------------------------ evento
print("\nEstudio de eventos por grupo de nacimiento")
cortes = [1958, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998]
etiq = ["≤1970","1971-74","1975-78","1979-82","1983-86","1987-90","1991-94","1995-98"]
M["grp"] = pd.cut(M.nac, cortes, labels=etiq)
REF = "1979-82"
G = pd.get_dummies(M.grp, prefix="g", dtype=float).drop(columns=[f"g_{REF}"])
E = pd.get_dummies(M.p19.astype(int), prefix="e", drop_first=True).astype(float)
C = pd.get_dummies(M.nac.astype(int), prefix="c", drop_first=True).astype(float)
# Dos correcciones respecto a la primera versión. Los efectos principales de
# grupo los absorben los efectos fijos de año de nacimiento, así que incluirlos
# sólo volvía singular la matriz. Y el término cohorte x rango tiene que estar
# aquí igual que en el modelo principal: sin él, la tendencia de ciclo de vida
# (la pendiente sube con la edad) se filtra a los coeficientes del evento y
# fabrica una tendencia previa que no existe.
X = sm.add_constant(pd.concat([
    pd.DataFrame({"r_ori": M.r_ori.values}, index=M.index),
    G.mul(M.intens, axis=0).add_prefix("d_"),
    G.mul(M.r_ori * M.intens, axis=0).add_prefix("ev_"),
    E, C, E.mul(M.r_ori, axis=0).add_prefix("ri_"),
    C.mul(M.r_ori, axis=0).add_prefix("rc_")], axis=1))
me = sm.WLS(M.r_des, X, weights=M.factor).fit(cov_type="cluster", cov_kwds={"groups": M.p19})
ev = []
for e_ in etiq:                      # reescalado a desviaciones estándar
    k = f"ev_g_{e_}"
    ev.append((e_, 0.0, 0.0) if e_ == REF else (e_, me.params[k]*K, me.bse[k]*K))
ev = pd.DataFrame(ev, columns=["grp","b","se"])
ev["t"] = (ev.b / ev.se.replace(0, np.nan)).round(2)
print(ev.round(3).to_string(index=False))

# Prueba conjunta: los grupos con dosis cero en todos sus años de nacimiento
PRE = [e_ for e_ in etiq if e_ != REF and (M.dosis[M.grp == e_] == 0).all()]
ft = me.f_test([f"ev_g_{e_}=0" for e_ in PRE])
print(f"  Grupos previos al repunte: {', '.join(PRE)}")
print(f"  Prueba conjunta de tendencias previas: F={float(ft.fvalue):.2f}  "
      f"p={float(ft.pvalue):.3f}")

fig, ax = plt.subplots(figsize=(8.4, 4.2))
x = np.arange(len(ev))
pre = ev.grp.isin(["≤1970","1971-74","1975-78","1979-82","1983-86"])
ax.axhline(0, color="#666", lw=.8); ax.axvspan(4.5, 7.5, color="#a63a2b", alpha=.06)
ax.errorbar(x[pre], ev.b[pre], yerr=1.96*ev.se[pre], fmt="o", ms=5, lw=1.4,
            capsize=3, color="#3f7cac", label="Ventana formativa previa al repunte")
ax.errorbar(x[~pre], ev.b[~pre], yerr=1.96*ev.se[~pre], fmt="o", ms=5, lw=1.4,
            capsize=3, color="#a63a2b", label="Ventana formativa alcanzada por el repunte")
ax.set_xticks(x); ax.set_xticklabels(ev.grp, fontsize=8.5)
ax.set_xlabel("Grupo de año de nacimiento")
ax.set_ylabel("Cambio en la pendiente origen-destino\npor desviación estándar de intensidad")
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
ax.grid(axis="y", color="#e6e6e6", lw=.8); ax.set_axisbelow(True)
for s_ in ("top","right"): ax.spines[s_].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/g3_evento.png", dpi=200, bbox_inches="tight")
print(f"\nGuardada: {OUT}/g3_evento.png")
M[["p19","nac","grp","r_ori","r_des","dosis","intens","factor"]].to_pickle(_r.OUT + "/M.pkl")
ev.to_pickle(_r.OUT + "/ev.pkl")
