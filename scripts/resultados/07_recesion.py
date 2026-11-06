# -*- coding: utf-8 -*-
"""
recesion.py — el confusor con el calendario correcto
====================================================
La pandemia y el fin de PROSPERA no alcanzan ninguna ventana formativa de la
muestra, que cierran todas en 2016 o antes. La recesión de 2008-2009 sí, y
golpeó más fuerte a los estados manufactureros del norte, que son los mismos
donde la violencia repuntó. Ese es el confusor que hay que atacar.

Se construye un control exactamente paralelo a la dosis de violencia:

    choque(e)   = caída del PIB real de la entidad entre 2007 y 2009
    psi(c)      = fracción de la ventana 10-18 que cae en 2008 o 2009
    dosis_rec   = choque(e) x psi(c)

y se mete al modelo junto con su interacción con el rango de origen, que es
la forma en que la recesión podría imitar el efecto que buscamos. Si b3
sobrevive, el confusor queda atendido; si no, hay que decirlo.

Insumo: INEGI, PIB por entidad federativa, millones de pesos a precios de 2018.
"""
import json, os, re, sys, unicodedata, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
SEED = 20261102
np.random.seed(SEED)

SAL = _r.SAL
PIBE = _r.PIBE

from base import construir, muestra, efectos_fijos, escala
from graficas_entregable1 import ABREV

LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


NOMBRES = {
    1: "Aguascalientes", 2: "Baja California", 3: "Baja California Sur",
    4: "Campeche", 5: "Coahuila de Zaragoza", 6: "Colima", 7: "Chiapas",
    8: "Chihuahua", 9: "Ciudad de Mexico", 10: "Durango", 11: "Guanajuato",
    12: "Guerrero", 13: "Hidalgo", 14: "Jalisco", 15: "Mexico",
    16: "Michoacan de Ocampo", 17: "Morelos", 18: "Nayarit",
    19: "Nuevo Leon", 20: "Oaxaca", 21: "Puebla", 22: "Queretaro",
    23: "Quintana Roo", 24: "San Luis Potosi", 25: "Sinaloa", 26: "Sonora",
    27: "Tabasco", 28: "Tamaulipas", 29: "Tlaxcala", 30: "Veracruz de Ignacio de la Llave",
    31: "Yucatan", 32: "Zacatecas",
}
CLAVE = {norm(v): k for k, v in NOMBRES.items()}

# ------------------------------------------------------------- panel de PIB
raw = pd.read_csv(PIBE, encoding="utf-8")
raw = raw[raw.Descriptores.str.contains("PIBPM", na=False)]
anios = [c for c in raw.columns if re.match(r"^\d{4}", str(c))]
ren = {c: int(str(c)[:4]) for c in anios}

filas = []
for _, r in raw.iterrows():
    etiq = str(r.Descriptores).split("|")[-1]
    etiq = re.sub(r"<[^>]*>", "", etiq).strip()
    cve = CLAVE.get(norm(etiq))
    if cve is None:
        continue
    for c in anios:
        v = pd.to_numeric(r[c], errors="coerce")
        if pd.notna(v):
            filas.append({"cve": cve, "year": ren[c], "pib": float(v)})
P = pd.DataFrame(filas).drop_duplicates(["cve", "year"])
di(f"Panel de PIB estatal: {P.cve.nunique()} entidades, "
   f"{P.year.min()}-{P.year.max()}, {len(P)} celdas")
if P.cve.nunique() != 32:
    faltan = set(range(1, 33)) - set(P.cve)
    di(f"  AVISO: faltan entidades {sorted(faltan)}")

W = P.pivot(index="cve", columns="year", values="pib").sort_index()
g = np.log(W)

# ---------------------------------------------------- el choque de 2008-09
choque = -(g[2009] - g[2007])          # positivo = contracción mayor
di("")
di("=" * 74)
di("LA CAÍDA DEL PIB ESTATAL ENTRE 2007 Y 2009")
di("=" * 74)
orden = choque.sort_values(ascending=False)
di(f"  Mayor contracción: " + ", ".join(
    f"{ABREV[int(e)]} {100*v:.1f}%" for e, v in orden.head(6).items()))
di(f"  Menor contracción: " + ", ".join(
    f"{ABREV[int(e)]} {100*v:+.1f}%" for e, v in orden.tail(5).items()))
di(f"  Media {100*choque.mean():.1f} %, d.e. {100*choque.std():.1f} puntos")

# ¿es cierto que la recesión golpeó donde la violencia subió?
from base import panel_violencia

panel, intens = panel_violencia()
comp = pd.DataFrame({"choque": choque, "intens": intens}).dropna()
r = float(np.corrcoef(comp.choque, comp.intens)[0, 1])
di("")
di(f"  Correlación entre la contracción de 2007-09 y la intensidad de")
di(f"  violencia 2007-2017, entre las {len(comp)} entidades: {r:+.3f}")
if abs(r) < 0.2:
    di("  -> La premisa del confusor es débil: la recesión y la violencia")
    di("     no coinciden geográficamente tanto como se temía.")
else:
    di("  -> La premisa del confusor se sostiene: hay que controlarlo.")

# ------------------------------------------------------------ el control
df = construir(verbose=False)
M = muestra(df).copy()
M["nac"] = M.nac.astype(int)
M["choque"] = M.p19.map(choque)
M["psi"] = [len([y for y in range(n + 10, n + 19) if y in (2008, 2009)]) / 9.0
            for n in M.nac]
M["dosis_rec"] = M.choque * M.psi
M = M.dropna(subset=["dosis_rec"])
K = escala(M)
PEND = float(np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0])
di("")
di(f"  Con exposición positiva a la recesión: {100*(M.psi>0).mean():.1f} % "
   f"de la muestra")
di(f"  Correlación entre la dosis de violencia y la de recesión: "
   f"{np.corrcoef(M.dosis, M.dosis_rec)[0,1]:+.3f}")


def estimar(d, extra=None, etiq=""):
    base = pd.DataFrame({"r_ori": d.r_ori.values, "dosis": d.dosis.values,
                         "b3": (d.r_ori * d.dosis).values}, index=d.index)
    piezas = [base] + efectos_fijos(d)
    if extra is not None:
        piezas.append(extra)
    X = sm.add_constant(pd.concat(piezas, axis=1))
    m = sm.WLS(d.r_des, X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d.p19})
    b, se = m.params["b3"] * K, m.bse["b3"] * K
    di(f"  {etiq:52s} {b:+9.4f} {se:8.4f} {b/se:+7.2f} {2.8*se/PEND:7.1%}")
    return {"etiq": etiq, "b3": float(b), "se": float(se), "t": float(b / se),
            "emd_pct": float(2.8 * se / PEND)}


di("")
di("=" * 74)
di("EL MODELO CON Y SIN EL CONTROL DE RECESIÓN")
di("=" * 74)
di(f"  {'Especificación':50s} {'b3':>9} {'ee':>8} {'t':>7} {'EMD':>7}")
res = [estimar(M, None, "Sin control de recesión")]
rec1 = pd.DataFrame({"rec": M.dosis_rec.values}, index=M.index)
res.append(estimar(M, rec1, "+ dosis de recesión"))
rec2 = pd.DataFrame({"rec": M.dosis_rec.values,
                     "rec_r": (M.dosis_rec * M.r_ori).values}, index=M.index)
res.append(estimar(M, rec2, "+ dosis de recesión x rango de origen"))
# control más exigente: la caída del PIB interactuada con cada cohorte
C = pd.get_dummies(M.nac.astype(int), prefix="c", drop_first=True).astype(float)
rec3 = pd.concat([C.mul(M.choque, axis=0).add_prefix("gc_"),
                  C.mul(M.choque * M.r_ori, axis=0).add_prefix("gcr_")], axis=1)
res.append(estimar(M, rec3, "+ caída del PIB x cohorte x rango (saturado)"))

R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
R["recesion"] = {
    "choque_por_entidad": {str(int(k)): float(v) for k, v in choque.items()},
    "corr_choque_violencia": r,
    "share_expuesto": float((M.psi > 0).mean()),
    "corr_dosis": float(np.corrcoef(M.dosis, M.dosis_rec)[0, 1]),
    "estimaciones": res,
}
tmp = f"{SAL}/resultados.json.tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2, ensure_ascii=False, default=str)
os.replace(tmp, f"{SAL}/resultados.json")
with open(f"{SAL}/log_recesion.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
di(f"\nEscrito en resultados.json")
