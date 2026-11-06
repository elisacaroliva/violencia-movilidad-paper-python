# -*- coding: utf-8 -*-
"""
Construcción del panel y estimador de triple diferencia.

Este módulo lo comparten modelo.py, transiciones.py y conglomerados.py, de
modo que los tres trabajan sobre exactamente la misma muestra y las mismas
variables. Cualquier cambio aquí se propaga a los tres.
"""
import sys, numpy as np, pandas as pd
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from graficas_entregable1 import (poblacion_anual, cargar_sesnsp, indice_pca,
                                  ORIGEN, ABREV)
import pyreadstat, statsmodels.api as sm

SES = _r.SES
EMO = _r.EMO
OUT = _r.OUT
DEST = ([f"p94{c}" for c in "abcdefg"] + [f"p96{c}" for c in "abcdefghijklmnopqr"]
        + [f"p97{c}" for c in "abcdefghijklmn"])

# Escala de escolaridad: p9 llega a 13 y el 97 es "ninguno". Filtrar por <=9
# truncaba la variable por arriba y por abajo, así que se traduce a años.
ANIOS_ESC = {97: 0, 1: 0, 2: 6, 3: 9, 4: 9, 5: 12, 6: 12, 7: 8, 8: 11, 9: 14,
             10: 11, 11: 16, 12: 16, 13: 18}


def rango_ponderado(x, w, by):
    """Percentil dentro de cada grupo, respetando los factores de expansión."""
    o = pd.Series(np.nan, index=x.index)
    ok = x.notna()
    for _, i in x[ok].groupby(by[ok]).groups.items():
        xi, wi = x.loc[i], w.loc[i]
        s = np.argsort(xi.values); ws = wi.values[s]
        o.loc[xi.index[s]] = (np.cumsum(ws) - .5 * ws) / ws.sum()
    return o


def panel_violencia():
    """Índice de violencia por entidad y año, y la intensidad 2007-2017."""
    pob = poblacion_anual(range(1997, 2025))
    panel, _ = cargar_sesnsp(SES, pob)
    intens = (panel[(panel.year >= 2007) & (panel.year <= 2017)]
              .groupby("cve").indice.mean())
    return panel, intens


def construir(verbose=True):
    panel, intens = panel_violencia()

    df, _ = pyreadstat.read_dta(f"{EMO}/entrevistado_2023.dta",
                                apply_value_formats=False)
    hg, _ = pyreadstat.read_dta(f"{EMO}/hogar_2023.dta",
                                apply_value_formats=False)
    df["nac"] = 2023 - df.edad
    df["idx_ori"], v1 = indice_pca(df, ORIGEN, numericas=["p30"])
    df["idx_des"], v2 = indice_pca(df, DEST, numericas=["p99"])
    df["corresid"] = df["index"].isin(hg[hg.p5 == 4]["index"]).astype(int)
    df["migro"] = (df.p19 != df.entidad).astype(int)
    df["mujer"] = (df.sexo == 2).astype(int)
    # INEGI define rural como localidad de menos de 2 500 habitantes, que en
    # p21 es únicamente el código 5.
    df["rural"] = (df.p21 == 5).astype(int)

    esc = lambda s: pd.to_numeric(s, errors="coerce").map(ANIOS_ESC)
    df["ed_yo"] = esc(df.p9)
    df["ed_pad"] = pd.concat([esc(df.p42a), esc(df.p42b)], axis=1).max(axis=1)

    df["r_ori"] = rango_ponderado(df.idx_ori, df.factor, df.cohorte)
    df["r_des"] = rango_ponderado(df.idx_des, df.factor, df.cohorte)
    df["r_des_ed"] = rango_ponderado(df.ed_yo, df.factor, df.cohorte)
    df["q_ori"] = np.ceil(df.r_ori * 5).clip(1, 5).astype("Int64")
    df["q_des"] = np.ceil(df.r_des * 5).clip(1, 5).astype("Int64")

    df["frac"] = df.nac.apply(
        lambda n: len([y for y in range(n + 10, n + 19) if y >= 2007]) / 9)
    df["intens"] = df.p19.map(intens)
    df["dosis"] = df.intens * df.frac
    if verbose:
        print(f"Índices: origen {v1:.1%} de varianza, destino {v2:.1%}")
    return df.dropna(subset=["intens", "r_ori", "r_des"])


def muestra(df):
    """Muestra analítica: no migraron de entidad desde los 14 años."""
    return df[(df.p19 <= 32) & (df.migro == 0)].copy()


def efectos_fijos(d, rango=True):
    E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    piezas = [E, C]
    if rango:
        piezas += [E.mul(d.r_ori, axis=0).add_prefix("ri_"),
                   C.mul(d.r_ori, axis=0).add_prefix("rc_")]
    return piezas


def ddd(d, extra=None, cl="p19", y="r_des"):
    """Triple diferencia. b3 = coeficiente de rango de origen x dosis."""
    base = pd.DataFrame({"r_ori": d.r_ori.values, "dosis": d.dosis.values,
                         "b3": (d.r_ori * d.dosis).values}, index=d.index)
    piezas = [base] + efectos_fijos(d)
    if extra is not None:
        piezas.append(extra)
    X = sm.add_constant(pd.concat(piezas, axis=1))
    return sm.WLS(d[y], X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d[cl]})


def escala(d):
    """Desviación estándar de la intensidad entre entidades."""
    return d.groupby("p19").intens.first().std()


def linea(nombre, m, n):
    b, se = m.params["b3"], m.bse["b3"]
    print(f"  {nombre:42s} n={n:5d}  b3={b:+.4f} ({se:.4f})  "
          f"t={b/se:+.2f}  IC95=[{b-1.96*se:+.3f},{b+1.96*se:+.3f}]")
    return b, se
