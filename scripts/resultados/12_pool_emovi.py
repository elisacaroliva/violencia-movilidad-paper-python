# -*- coding: utf-8 -*-
"""
Armonización de ESRU-EMOVI 2017 y 2023.

Los nombres de variable cambian entre rondas, pero los reactivos de activos
son en su mayoría los mismos. Este módulo define el mapeo reactivo por
reactivo y construye índices de origen y destino comparables entre rondas.

Decisiones:
  - Sólo se usan reactivos presentes en AMBAS rondas. Se pierden los de
    espacios de la vivienda (sala, jardín, patio...) y los productos
    financieros finos que 2023 agregó, pero queda un núcleo de 26 reactivos
    de origen y 23 de destino.
  - Cuando 2023 tiene un reactivo que 2017 parte en dos (terreno; animales de
    trabajo y ganado), se toma el máximo de los dos de 2017.
  - El número de automóviles (2023: p30 y p99) se binariza, porque 2017 lo
    registra como sí/no en el origen.
  - El componente principal se estima sobre las DOS rondas juntas, de modo
    que las cargas son idénticas y los índices viven en la misma escala.
  - Los rangos percentiles se calculan dentro de ronda x año de nacimiento.
"""
import sys, numpy as np, pandas as pd
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from base import EMO, rango_ponderado
import pyreadstat

E17 = _r.EMO17

# ---------------------------------------------------------------- mapeo
# nombre común -> (variable 2023, variable(es) 2017)
ORI = {
    "agua":        ("p26a", ["p30_a"]),
    "luz":         ("p26b", ["p30_b"]),
    "banio":       ("p26c", ["p30_c"]),
    "boiler":      ("p26d", ["p30_d"]),
    "domestico":   ("p26e", ["p30_e"]),
    "estufa":      ("p31a", ["p33_a"]),
    "lavadora":    ("p31b", ["p33_b"]),
    "refri":       ("p31c", ["p33_c"]),
    "telfijo":     ("p31d", ["p33_d"]),
    "tv":          ("p31e", ["p33_e"]),
    "tostador":    ("p31f", ["p33_f"]),
    "aspiradora":  ("p31g", ["p33_g"]),
    "tvcable":     ("p31h", ["p33_h"]),
    "microondas":  ("p31i", ["p33_i"]),
    "celular":     ("p31j", ["p33_j"]),
    "computadora": ("p31k", ["p33_k"]),
    "internet":    ("p31l", ["p33_l"]),
    "dvd":         ("p31m", ["p33_n"]),
    "otracasa":    ("p32a", ["p34_a"]),
    "local":       ("p32b", ["p34_b"]),
    "terreno":     ("p32c", ["p34_c", "p34_d"]),
    "animales":    ("p32d", ["p34_g", "p34_h"]),
    "ahorro":      ("p32e", ["p32_a"]),
    "tdc":         ("p32f", ["p32_c"]),
    "tdepto":      ("p32g", ["p32_d"]),
    "auto":        ("p30",  ["p34_e"]),        # 2023 es conteo, se binariza
}
DES = {
    "estufa":      ("p96a", ["p126a"]),
    "lavadora":    ("p96b", ["p126b"]),
    "refri":       ("p96c", ["p126c"]),
    "microondas":  ("p96d", ["p126d"]),
    "tv":          ("p96e", ["p126e"]),
    "tostador":    ("p96f", ["p126f"]),
    "consola":     ("p96g", ["p126i"]),
    "aspiradora":  ("p96h", ["p126g"]),
    "tvpaga":      ("p96i", ["p126j"]),
    "telfijo":     ("p96j", ["p126k"]),
    "celular":     ("p96k", ["p126l"]),
    "internet":    ("p96l", ["p126m"]),
    "tableta":     ("p96m", ["p126n"]),
    "computadora": ("p96n", ["p126o"]),
    "agricola":    ("p96o", ["p126r"]),
    "animales":    ("p96p", ["p126p", "p126q"]),
    "otracasa":    ("p97a", ["p129a"]),
    "local":       ("p97b", ["p129b"]),
    "terreno":     ("p97c", ["p129d", "p129e"]),
    "bancaria":    ("p97d", ["p128b", "p128c"]),
    "tdc":         ("p97e", ["p128d"]),
    "tdepto":      ("p97f", ["p128e"]),
    "auto":        ("p99",  ["p131"]),         # ambos son conteo, se binarizan
}
CONTEO = {"p30", "p99", "p131"}                # se binarizan en >0


def _binaria(s, nombre):
    """1 = sí, 0 = no, NaN = no sabe / no responde."""
    v = pd.to_numeric(s, errors="coerce")
    if nombre in CONTEO:
        return v.where(v <= 90).gt(0).astype(float).where(v.notna() & (v <= 90))
    return v.replace({1: 1.0, 2: 0.0}).where(v.isin([1, 2]))


def _bloque(df, mapeo, ronda):
    """Devuelve el bloque armonizado de reactivos para una ronda."""
    out = {}
    for comun, (v23, v17) in mapeo.items():
        if ronda == 2023:
            out[comun] = _binaria(df[v23], v23)
        else:
            partes = [_binaria(df[v], v) for v in v17]
            x = pd.concat(partes, axis=1)
            out[comun] = x.max(axis=1).where(x.notna().any(axis=1))
    return pd.DataFrame(out, index=df.index)


def _pca(X):
    """Primer componente sobre la matriz estandarizada, con signo orientado."""
    Z = X.copy()
    for c in Z.columns:
        Z[c] = Z[c].fillna(Z[c].mean())
        s = Z[c].std()
        Z[c] = (Z[c] - Z[c].mean()) / (s if s > 0 else 1)
    A = Z.to_numpy()
    U, S, Vt = np.linalg.svd(A - A.mean(0), full_matrices=False)
    pc, carga = U[:, 0] * S[0], Vt[0]
    if carga.sum() < 0:
        pc, carga = -pc, -carga
    var = S[0] ** 2 / (S ** 2).sum()
    return pd.Series(pc, index=X.index), var, pd.Series(carga, index=X.columns)


def cargar(verbose=True):
    """Devuelve el panel conjunto 2017 + 2023 con índices y rangos comunes."""
    cols17 = (["p23", "p23_1", "p05", "p06", "factor", "est_dis", "Estado", "p13"]
              + sorted({v for _, vs in ORI.items() for v in vs[1]})
              + sorted({v for _, vs in DES.items() for v in vs[1]}))
    d17, _ = pyreadstat.read_dta(f"{E17}/entrevistado_2017.dta",
                                 apply_value_formats=False, usecols=cols17)
    d23, _ = pyreadstat.read_dta(f"{EMO}/entrevistado_2023.dta",
                                 apply_value_formats=False)

    a = pd.DataFrame({
        "ronda": 2017, "edad": d17.p05, "nac": 2017 - d17.p05,
        "sexo": d17.p06, "factor": d17.factor,
        "ent14": d17.p23, "mun14": d17.p23_1, "ent_hoy": d17.Estado,
    }, index=d17.index)
    b = pd.DataFrame({
        "ronda": 2023, "edad": d23.edad, "nac": 2023 - d23.edad,
        "sexo": d23.sexo, "factor": d23.factor,
        "ent14": d23.p19, "mun14": pd.to_numeric(d23.p20_COD, errors="coerce"),
        "ent_hoy": d23.entidad,
    }, index=d23.index)

    O = pd.concat([_bloque(d17, ORI, 2017), _bloque(d23, ORI, 2023)], ignore_index=True)
    D = pd.concat([_bloque(d17, DES, 2017), _bloque(d23, DES, 2023)], ignore_index=True)
    P = pd.concat([a, b], ignore_index=True)

    P["idx_ori"], v1, c1 = _pca(O)
    P["idx_des"], v2, c2 = _pca(D)
    P["migro"] = (P.ent14 != P.ent_hoy).astype(int)
    P["r_ori"] = rango_ponderado(P.idx_ori, P.factor, P.ronda.astype(str) + "_" + P.nac.astype(str))
    P["r_des"] = rango_ponderado(P.idx_des, P.factor, P.ronda.astype(str) + "_" + P.nac.astype(str))
    P["q_ori"] = np.ceil(P.r_ori * 5).clip(1, 5).astype("Int64")
    P["q_des"] = np.ceil(P.r_des * 5).clip(1, 5).astype("Int64")

    if verbose:
        print(f"Índices armonizados: origen {len(ORI)} reactivos ({v1:.1%} de varianza), "
              f"destino {len(DES)} reactivos ({v2:.1%})")
    return P[P.ent14 <= 32].dropna(subset=["r_ori", "r_des"]).copy(), (c1, c2)
