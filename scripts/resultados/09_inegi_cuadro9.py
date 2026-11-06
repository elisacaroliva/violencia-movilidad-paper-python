# -*- coding: utf-8 -*-
"""
inegi_cuadro9.py — las tres definiciones del tratamiento de violencia
======================================================================
Es el cuadro 9 y es el resultado más instructivo del artículo, porque el
único renglón que da una estimación grande es también el único que viola el
supuesto de identificación del diseño.

Se reestima la especificación principal con tres índices de exposición,
dejando todo lo demás fijo:

  (1) SESNSP, índice de cuatro delitos, 2007-17  -> la medida principal
  (2) INEGI, NIVEL de la tasa de homicidio 2007-17
  (3) INEGI, AUMENTO de la tasa entre 1990-97 y 2007-17

El renglón (3) es el objeto mejor identificado en principio: si lo que daña a
una cohorte es el repunte y no el nivel crónico de violencia de su entidad,
entonces el tratamiento es el incremento. Da la estimación mayor del artículo
y una p de permutación de 0.08, y REPRUEBA la prueba conjunta de tendencias
previas. Se reporta con la falla a la vista, porque ocultarla sería reportar
el resultado más vistoso del trabajo sin su advertencia.

Para cada índice se calcula b3, el efecto sobre el rango esperado en el
percentil 25 —la escala de Sharkey y Torrats-Espinosa— y la prueba conjunta
de que los grupos de nacimiento previos al repunte no muestran pendiente
diferencial. La inferencia por permutación replica el procedimiento de
`congelar.py`: Frisch-Waugh-Lovell con una sola descomposición QR y 2 000
reasignaciones del vector de intensidad entre entidades.

Uso:  python -I codigo/inegi_cuadro9.py
"""
import json
import sys
import warnings

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
N_PERM = 2000
CORTES = [1958, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998]
ETIQ = ["<=1970", "1971-74", "1975-78", "1979-82", "1983-86", "1987-90",
        "1991-94", "1995-98"]
REF = "1979-82"

from base import construir, muestra, escala
from guardar import guardar

LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def zscore(s):
    return (s - s.mean()) / s.std()


# --------------------------------------------------------- tasas del INEGI
pob = pd.read_csv(CON, encoding="latin-1", low_memory=False,
                  usecols=["CLAVE_ENT", "ANO", "POB_MIT_MUN"])
pob_ent = (pob.groupby(["CLAVE_ENT", "ANO"]).POB_MIT_MUN.sum().rename("pob")
           .reset_index().rename(columns={"CLAVE_ENT": "cve", "ANO": "anio"}))
ho = pd.read_csv(f"{INE}/hom_entidad_ocurrencia.csv")
E = (pob_ent.merge(ho, on=["cve", "anio"], how="left")
     .assign(homicidios=lambda d: d.homicidios.fillna(0)))
E["tasa"] = E.homicidios / E.pob * 1e5

pre = E[E.anio.between(1990, 1997)].groupby("cve").tasa.mean()
post = E[E.anio.between(2007, 2017)].groupby("cve").tasa.mean()

INDICES = {
    "INEGI nivel 2007-17": zscore(np.log1p(post)),
    "INEGI aumento vs 1990-97": zscore(np.log1p(post) - np.log1p(pre)),
}

# -------------------------------------------------------------- la muestra
df = construir(verbose=False)
M = muestra(df).copy()
M["nac"] = M.nac.astype(int)
M["frac"] = [len([y for y in range(n + 10, n + 19) if y >= 2007]) / 9.0
             for n in M.nac]
M["grp"] = pd.cut(M.nac, CORTES, labels=ETIQ)
PEND = float(np.polyfit(M.r_ori, M.r_des, 1, w=np.sqrt(M.factor))[0])

C = pd.get_dummies(M.nac, prefix="c", drop_first=True).astype(float)
Ed = pd.get_dummies(M.p19.astype(int), prefix="e", drop_first=True).astype(float)
FIJOS = [Ed, C, Ed.mul(M.r_ori, axis=0).add_prefix("ri_"),
         C.mul(M.r_ori, axis=0).add_prefix("rc_")]


def ddd(dosis):
    """Triple diferencia completa. Devuelve el ajuste y los nombres."""
    X = sm.add_constant(pd.concat(
        [pd.DataFrame({"r_ori": M.r_ori.values, "dosis": dosis.values,
                       "b3": (M.r_ori * dosis).values}, index=M.index)]
        + FIJOS, axis=1))
    m = sm.WLS(M.r_des, X, weights=M.factor).fit(
        cov_type="cluster", cov_kwds={"groups": M.p19})
    return m, list(X.columns)


def efecto_p25(m, nombres, p=0.25):
    """b2 + p*b3, en puntos de rango sobre 100."""
    r = np.zeros(len(nombres))
    r[nombres.index("dosis")] = 1.0
    r[nombres.index("b3")] = p
    t = m.t_test(r)
    return (float(np.squeeze(t.effect)) * 100,
            float(np.squeeze(t.sd)) * 100)


def tendencias_previas(intens, dosis):
    """Prueba conjunta: los grupos previos al repunte no tienen pendiente."""
    G = pd.get_dummies(M.grp, prefix="g", dtype=float).drop(columns=[f"g_{REF}"])
    X = sm.add_constant(pd.concat([
        pd.DataFrame({"r_ori": M.r_ori.values}, index=M.index),
        G.mul(intens, axis=0).add_prefix("d_"),
        G.mul(M.r_ori * intens, axis=0).add_prefix("ev_")] + FIJOS, axis=1))
    me = sm.WLS(M.r_des, X, weights=M.factor).fit(
        cov_type="cluster", cov_kwds={"groups": M.p19})
    previos = [g for g in ETIQ if g != REF and (dosis[M.grp == g] == 0).all()]
    ft = me.f_test([f"ev_g_{g}=0" for g in previos])
    return float(ft.fvalue), float(ft.pvalue), previos


def permutacion(intens, p=0.25):
    """p de permutación para b3 Y para el efecto en el percentil p.

    Las dos hacen falta y no son la misma cosa. b3 es el cambio de pendiente;
    el efecto en p25 es b2 + p*b3, que es la cantidad comparable con Sharkey y
    Torrats-Espinosa y la que de hecho resulta marginalmente significativa en
    el renglón del aumento. Reportar sólo una de las dos daría una impresión
    equivocada de la fuerza del resultado, en cualquiera de los dos sentidos.
    """
    rng = np.random.default_rng(SEED)
    ents = sorted(M.p19.unique())
    FE = sm.add_constant(pd.concat(
        [pd.DataFrame({"r_ori": M.r_ori.values}, index=M.index)] + FIJOS,
        axis=1)).to_numpy()
    sw = np.sqrt(M.factor.to_numpy())
    Q, _ = np.linalg.qr(FE * sw[:, None])
    res = lambda v: (v * sw) - Q @ (Q.T @ (v * sw))
    ry, ro, fr = res(M.r_des.to_numpy()), M.r_ori.to_numpy(), M.frac.to_numpy()
    idx = {e: (M.p19 == e).to_numpy() for e in ents}
    iv = np.array([intens[M.p19 == e].iloc[0] for e in ents])

    def coefs(vec):
        d = np.empty(len(M))
        for e, v in zip(ents, vec):
            d[idx[e]] = v
        d = d * fr
        A = np.column_stack([res(d), res(ro * d)])
        b2, b3 = np.linalg.lstsq(A, ry, rcond=None)[0]
        return b3, b2 + p * b3

    r_b3, r_p25 = coefs(iv)
    nulo = np.array([coefs(rng.permutation(iv)) for _ in range(N_PERM)])
    return (float((np.abs(nulo[:, 0]) >= abs(r_b3)).mean()),
            float((np.abs(nulo[:, 1]) >= abs(r_p25)).mean()))


# ------------------------------------------------- renglón (1): el principal
di("=" * 78)
di("CUADRO 9 — TRES DEFINICIONES DEL TRATAMIENTO DE VIOLENCIA")
di("=" * 78)
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
K_ses = escala(M)
ses = {"b3": R["principal"][0]["b3"], "se": R["principal"][0]["se"],
       "p25": [x for x in R["movilidad_absoluta"]["por_percentil"]
               if x["percentil"] == 0.25][0]["efecto"],
       "se_p25": [x for x in R["movilidad_absoluta"]["por_percentil"]
                  if x["percentil"] == 0.25][0]["se"],
       "F": R["evento_estatal"]["F"], "p": R["evento_estatal"]["p"],
       "p_perm": R["permutacion"]["p"], "escala_de": float(K_ses)}
di(f"\n{'Índice':34s} {'b3':>9} {'ee':>8} {'p25':>8} {'ee':>7} "
   f"{'F':>7} {'p':>7}")
di(f"{'(1) SESNSP, cuatro delitos':34s} {ses['b3']:+9.4f} {ses['se']:8.4f} "
   f"{ses['p25']:+8.2f} {ses['se_p25']:7.2f} {ses['F']:7.2f} {ses['p']:7.3f}"
   f"   {'pasa' if ses['p'] > 0.10 else 'REPRUEBA'}")

medidas = {"SESNSP cuatro delitos": ses}

# --------------------------------------------- renglones (2) y (3): el INEGI
for nombre, I in INDICES.items():
    M["I"] = M.p19.map(I)
    sub = M.dropna(subset=["I"])
    if len(sub) != len(M):
        di(f"  aviso: {len(M) - len(sub)} observaciones sin índice, se omiten")
    dosis = M.I * M.frac
    m, nombres = ddd(dosis)
    b3, se = float(m.params["b3"]), float(m.bse["b3"])
    p25, se_p25 = efecto_p25(m, nombres)
    F, p, previos = tendencias_previas(M.I, dosis)
    pp, pp25 = permutacion(M.I)
    medidas[nombre] = {"b3": b3, "se": se, "t": b3 / se, "p25": p25,
                       "se_p25": se_p25, "F": F, "p": p, "p_perm": pp,
                       "p_perm_p25": pp25,
                       "emd_pct": float(2.8 * se / PEND),
                       "grupos_previos": previos}
    etq = ("(2) INEGI, nivel 2007-17" if "nivel" in nombre
           else "(3) INEGI, aumento sobre 1990-97")
    di(f"{etq:34s} {b3:+9.4f} {se:8.4f} {p25:+8.2f} {se_p25:7.2f} "
       f"{F:7.2f} {p:7.3f}   {'pasa' if p > 0.10 else 'REPRUEBA'}"
       f"   (p perm. b3 {pp:.3f}, p25 {pp25:.3f})")

di("")
di("Lectura: el renglón (3) define el tratamiento como el AUMENTO de la tasa")
di("de homicidio y no su nivel, que es el objeto mejor identificado en")
di("principio. Da la estimación mayor del artículo y es el único renglón que")
di("viola el supuesto de identificación del propio diseño.")

R.setdefault("inegi", {})["medidas"] = medidas
guardar(R, f"{SAL}/resultados.json")
with open(f"{SAL}/log_cuadro9.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
print("\nEscrito en resultados.json")
