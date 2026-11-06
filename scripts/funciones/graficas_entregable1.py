# -*- coding: utf-8 -*-
"""
Gráficas del Entregable 1
=========================
Proyecto: exposición a la violencia del crimen organizado en la adolescencia
          y persistencia intergeneracional en México.

Produce:
  Gráfica 1  (g1_delitos.png)  Carpetas de investigación por cada 100 000 habitantes
                               de cuatro delitos asociados al crimen organizado,
                               México, 1997-2017.
  Gráfica 2  (g2_exposicion.png) Exposición a la violencia entre los 10 y los 18 años,
                               cohorte 1993-1998, por entidad de residencia a los 14 años.

Insumos
-------
  SESNSP, incidencia delictiva del fuero común, metodología anterior,
      serie estatal 1997-2017 .............. IDEFC_MAnterior_ago2024.csv
  CEEY, ESRU-EMOVI 2023 ................... Data/entrevistado_2023.dta
  INEGI, censos de población 2010 y 2020 ... población estatal (constantes, abajo)

Uso
---
  python graficas_entregable1.py --sesnsp RUTA.csv --emovi CARPETA_DATA --salida CARPETA

Requiere: pandas, numpy, matplotlib, pyreadstat
"""

import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import argparse
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------- #
# Parámetros de estilo (compartidos por las dos gráficas)
# --------------------------------------------------------------------------- #
COL = {
    "homicidio": "#a63a2b",
    "extorsion": "#c98f2e",
    "secuestro": "#3f7cac",
    "robo_carr": "#7d9b76",
    "negativo":  "#3f7cac",
    "positivo":  "#a63a2b",
}
ETIQ = {
    "homicidio": "Homicidio doloso",
    "extorsion": "Extorsión",
    "secuestro": "Secuestro",
    "robo_carr": "Robo en carreteras con violencia",
}
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
         "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

ABREV = {1:"Ags", 2:"BC", 3:"BCS", 4:"Camp", 5:"Coah", 6:"Col", 7:"Chis",
         8:"Chih", 9:"CDMX", 10:"Dgo", 11:"Gto", 12:"Gro", 13:"Hgo", 14:"Jal",
         15:"Méx", 16:"Mich", 17:"Mor", 18:"Nay", 19:"NL", 20:"Oax", 21:"Pue",
         22:"Qro", 23:"QR", 24:"SLP", 25:"Sin", 26:"Son", 27:"Tab", 28:"Tamps",
         29:"Tlax", 30:"Ver", 31:"Yuc", 32:"Zac"}

# Población estatal, censos INEGI 2010 y 2020. Se usan como anclas para
# interpolar y extrapolar la población de cada año de la serie.
POB2010 = {1:1184996, 2:3155070, 3:637026, 4:822441, 5:2748391, 6:650555,
           7:4796580, 8:3406465, 9:8851080, 10:1632934, 11:5486372, 12:3388768,
           13:2665018, 14:7350682, 15:15175862, 16:4351037, 17:1777227,
           18:1084979, 19:4653458, 20:3801962, 21:5779829, 22:1827937,
           23:1325578, 24:2585518, 25:2767761, 26:2662480, 27:2238603,
           28:3268554, 29:1169936, 30:7643194, 31:1955577, 32:1490668}
POB2020 = {1:1425607, 2:3769020, 3:798447, 4:928363, 5:3146771, 6:731391,
           7:5543828, 8:3741869, 9:9209944, 10:1832650, 11:6166934, 12:3540685,
           13:3082841, 14:8348151, 15:16992418, 16:4748846, 17:1971520,
           18:1235456, 19:5784442, 20:4132148, 21:6583278, 22:2368467,
           23:1857985, 24:2822255, 25:3026943, 26:2944840, 27:2402598,
           28:3527735, 29:1342977, 30:8062579, 31:2320898, 32:1622138}

# Reactivos de la ESRU-EMOVI 2023 que alimentan el índice de recursos del hogar
# de origen (referidos a los 14 años). Todos son dicotómicos 1=Sí / 2=No.
ORIGEN = ([f"p26{c}" for c in "abcde"]            # servicios de la vivienda
          + [f"p29{c}" for c in "abcdefg"]        # características de la vivienda
          + [f"p31{c}" for c in "abcdefghijklmno"]  # bienes duraderos
          + [f"p32{c}" for c in "abcdefghijklmno"])  # propiedades y activos


# --------------------------------------------------------------------------- #
# 1. Población estatal anual
# --------------------------------------------------------------------------- #
def poblacion_anual(anios):
    """Población estatal por año, log-lineal entre los censos de 2010 y 2020.

    Tomar un denominador fijo (por ejemplo la población de 2020 para toda la
    serie) subestima los niveles de los años iniciales y, como las entidades
    crecieron a ritmos distintos, sesga además la comparación entre ellas.
    """
    tasa = {e: (np.log(POB2020[e]) - np.log(POB2010[e])) / 10 for e in POB2010}
    return pd.DataFrame(
        {e: {a: POB2010[e] * np.exp(tasa[e] * (a - 2010)) for a in anios}
         for e in POB2010}
    )


# --------------------------------------------------------------------------- #
# 2. Serie delictiva del SESNSP
# --------------------------------------------------------------------------- #
def cargar_sesnsp(ruta_csv, pob):
    """Devuelve un panel entidad-año con los cuatro delitos, sus tasas y el índice.

    Se excluye deliberadamente el robo común: es un delito de oportunidad que no
    exige una organización capaz de sostener la amenaza sobre un territorio, de
    modo que incluirlo diluiría la atribución al crimen organizado.
    """
    s = pd.read_csv(ruta_csv, encoding="latin-1", low_memory=False)
    s["total"] = s[MESES].apply(pd.to_numeric, errors="coerce").sum(axis=1)

    filtros = {
        "homicidio": (s.TIPO == "DOLOSOS") & (s.MODALIDAD == "HOMICIDIOS"),
        "extorsion": s.TIPO == "EXTORSION",
        "secuestro": s.TIPO == "SECUESTRO",
        "robo_carr": (s.MODALIDAD == "ROBO EN CARRETERAS") & (s.TIPO == "CON VIOLENCIA"),
    }
    partes = [s[m].groupby(["AÑO", "INEGI"]).total.sum().rename(k)
              for k, m in filtros.items()]
    panel = (pd.concat(partes, axis=1)
               .reset_index()
               .rename(columns={"AÑO": "year", "INEGI": "cve"}))

    panel["pob"] = [pob.loc[a, e] for a, e in zip(panel.year, panel.cve)]
    delitos = list(filtros)
    for d in delitos:                                   # tasa por 100 000
        panel[d + "_t"] = panel[d] / panel.pob * 1e5
    for d in delitos:                                   # estandarización
        col = panel[d + "_t"]
        panel[d + "_z"] = (col - col.mean()) / col.std()
    # Índice de exposición: promedio simple de los cuatro delitos estandarizados.
    panel["indice"] = panel[[d + "_z" for d in delitos]].mean(axis=1)
    return panel, delitos


# --------------------------------------------------------------------------- #
# 3. GRÁFICA 1
# --------------------------------------------------------------------------- #
def grafica1(panel, delitos, salida):
    """Dos paneles porque las escalas no son comparables: el homicidio se mueve
    entre 9 y 21 por cada 100 000 y los demás entre 0 y 7. En un solo eje, la
    extorsión y el secuestro se verían como líneas planas."""
    nac = panel.groupby("year")[delitos].sum()
    pob = panel.groupby("year").pob.sum()
    tasa = (nac.T / pob).T * 1e5

    fig, ax = plt.subplots(1, 2, figsize=(10.6, 4.3))

    ax[0].plot(tasa.index, tasa.homicidio, lw=2.2, marker="o", ms=3,
               color=COL["homicidio"])
    ax[0].set_title("a) Homicidio doloso", fontsize=10.5)
    ax[0].set_ylabel("Carpetas por cada 100 000 habitantes")

    for d in ["extorsion", "secuestro", "robo_carr"]:
        ax[1].plot(tasa.index, tasa[d], lw=2.0, marker="o", ms=3,
                   color=COL[d], label=ETIQ[d])
    ax[1].set_title("b) Delitos de depredación económica", fontsize=10.5)
    ax[1].legend(frameon=False, fontsize=8.5)

    for a in ax:
        a.axvspan(2007, 2012, color="#000000", alpha=0.05, zorder=0)
        a.set_xlabel("Año de registro")
        a.set_xlim(1997, 2017)
        a.set_xticks(range(1997, 2018, 4))
        a.grid(axis="y", color="#dddddd", lw=0.8)
        a.set_axisbelow(True)
        for lado in ("top", "right"):
            a.spines[lado].set_visible(False)

    plt.tight_layout()
    ruta = os.path.join(salida, "g1_delitos.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("\nGráfica 1 — tasas nacionales en años seleccionados")
    print(tasa.loc[[1997, 2007, 2011, 2013, 2017]].round(2).to_string())
    return ruta


# --------------------------------------------------------------------------- #
# 4. ESRU-EMOVI: índice de origen y exposición formativa
# --------------------------------------------------------------------------- #
def indice_pca(datos, columnas, numericas=None):
    """Primer componente principal sobre reactivos dicotómicos de activos.

    Implementado con numpy (SVD) para no depender de scikit-learn. El signo del
    componente se orienta para que valores altos signifiquen más recursos.
    """
    X = datos[columnas].copy()
    for c in columnas:
        X[c] = (datos[c] == 1).astype(float)
        X.loc[datos[c].isin([8, 9]), c] = np.nan      # 8 = no sabe, 9 = no contesta
    if numericas:
        for c in numericas:
            v = pd.to_numeric(datos[c], errors="coerce")
            v[v > 20] = np.nan                        # topes implausibles
            X[c] = (v - v.mean()) / v.std()

    X = X.fillna(X.mean())
    X = (X - X.mean()) / X.std().replace(0, 1)
    M = X.to_numpy()
    _, s, Vt = np.linalg.svd(M - M.mean(axis=0), full_matrices=False)
    comp = (M - M.mean(axis=0)) @ Vt[0]
    if np.corrcoef(comp, M.mean(axis=1))[0, 1] < 0:
        comp = -comp
    varianza = s[0] ** 2 / (s ** 2).sum()
    return comp, varianza


def cargar_emovi(carpeta_data, panel_sesnsp):
    """Carga la encuesta, construye el índice de origen y la exposición formativa."""
    import pyreadstat
    df, _ = pyreadstat.read_dta(os.path.join(carpeta_data, "entrevistado_2023.dta"),
                                apply_value_formats=False)
    df["nac"] = 2023 - df.edad

    df["idx_ori"], var = indice_pca(df, ORIGEN, numericas=["p30"])
    print(f"\nÍndice de origen: {len(ORIGEN) + 1} reactivos, "
          f"{var:.1%} de la varianza en el primer componente")

    # Cohortes según la coincidencia entre la ventana formativa y el repunte.
    df["coh"] = pd.cut(df.nac, [1958, 1984, 1988, 1992, 1998],
                       labels=["D", "C", "B", "A"])

    # Exposición individual: promedio del índice de la entidad de residencia a
    # los 14 años (p19) durante los años en que la persona tuvo 10 a 18 años.
    clave = panel_sesnsp.set_index(["cve", "year"]).indice

    def exposicion(fila):
        anios = [a for a in range(fila.nac + 10, fila.nac + 19) if 1997 <= a <= 2017]
        vals = [clave[(fila.p19, a)] for a in anios if (fila.p19, a) in clave.index]
        return np.mean(vals) if vals else np.nan

    df["exp_idx"] = df.apply(exposicion, axis=1)
    return df


# --------------------------------------------------------------------------- #
# 5. GRÁFICA 2
# --------------------------------------------------------------------------- #
def grafica2(df, salida, min_casos=25):
    """Exposición formativa promedio de la cohorte A por entidad de origen.

    El panel de dispersión contra la persistencia que incluía una versión previa
    se retiró: con 22 entidades y celdas pequeñas en el quintil de origen, la
    correlación no es estimable con precisión.
    """
    A = df[(df.coh == "A") & df.exp_idx.notna() & (df.p19 <= 32)]
    g = (A.groupby("p19")
           .agg(exp=("exp_idx", "mean"), n=("exp_idx", "size")))
    g = g[g.n >= min_casos].sort_values("exp")
    g["ent"] = [ABREV[i] for i in g.index]

    fig, ax = plt.subplots(figsize=(9.6, 4.3))
    colores = [COL["negativo"] if v < 0 else COL["positivo"] for v in g.exp]
    ax.bar(range(len(g)), g.exp, color=colores, alpha=0.9)
    ax.axhline(0, color="#666666", lw=0.8)
    ax.set_xticks(range(len(g)))
    ax.set_xticklabels(g.ent, rotation=90, fontsize=7.5)
    ax.set_ylabel("Índice de exposición formativa\n(desviaciones estándar)")
    ax.grid(axis="y", color="#e6e6e6", lw=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

    plt.tight_layout()
    ruta = os.path.join(salida, "g2_exposicion.png")
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"\nGráfica 2 — {len(g)} entidades con al menos {min_casos} casos "
          f"en la cohorte A")
    print(f"  mínimo  {g.exp.min():+.2f} ({g.ent.iloc[0]})")
    print(f"  máximo  {g.exp.max():+.2f} ({g.ent.iloc[-1]})")
    print(f"  amplitud {g.exp.max() - g.exp.min():.2f} desviaciones estándar")
    print(f"  entidades por debajo del promedio del periodo: {(g.exp < 0).sum()}")
    return ruta


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sesnsp", required=True, help="IDEFC_MAnterior_ago2024.csv")
    ap.add_argument("--emovi", required=True, help="carpeta Data de la ESRU-EMOVI 2023")
    ap.add_argument("--salida", default=".", help="carpeta donde guardar las gráficas")
    args = ap.parse_args()
    os.makedirs(args.salida, exist_ok=True)

    pob = poblacion_anual(range(1997, 2025))
    panel, delitos = cargar_sesnsp(args.sesnsp, pob)
    r1 = grafica1(panel, delitos, args.salida)

    df = cargar_emovi(args.emovi, panel)
    r2 = grafica2(df, args.salida)

    print(f"\nGuardadas:\n  {r1}\n  {r2}")


if __name__ == "__main__":
    main()
