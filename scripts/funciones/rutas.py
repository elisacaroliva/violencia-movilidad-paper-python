# -*- coding: utf-8 -*-
"""
rutas.py — equivalente en Python de here::here() de R
======================================================
Todas las rutas del proyecto se construyen desde la raíz del repositorio, que
se reconoce por el archivo marcador `.here`. Así los scripts corren igual en
cualquier computadora y desde cualquier carpeta, sin editar una sola línea.

Uso (al inicio de cada script):

    import sys, pathlib
    sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents
                                if (p / ".here").exists()) / "scripts" / "funciones"))
    from rutas import here, SAL, EMO, ...

    here("data", "raw", "sesnsp")   ->  <raíz>/data/raw/sesnsp

Si por alguna razón se quiere apuntar a otra raíz (por ejemplo, datos en un
disco externo), basta con definir la variable de entorno PROYECTO_RAIZ.
"""
import os
from pathlib import Path


def _raiz() -> Path:
    env = os.environ.get("PROYECTO_RAIZ")
    if env:
        return Path(env).resolve()
    for p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (p / ".here").exists():
            return p
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / ".here").exists():
            return p
    raise FileNotFoundError(
        "No encontré el marcador `.here`. Corre los scripts desde dentro del "
        "repositorio o define la variable de entorno PROYECTO_RAIZ.")


RAIZ = _raiz()


def here(*partes) -> str:
    """Ruta absoluta (como texto) relativa a la raíz del proyecto."""
    return str(RAIZ.joinpath(*partes))


def asegurar(*carpetas) -> None:
    """Crea las carpetas de salida si no existen."""
    for c in carpetas:
        os.makedirs(c, exist_ok=True)


# ------------------------------------------------------------- insumos (raw)
EMO     = here("data", "raw", "emovi")                       # entrevistado_2023.dta, hogar_2023.dta
EMO17   = here("data", "raw", "emovi2017")                   # entrevistado_2017.dta, hogar_2017.dta
SES     = here("data", "raw", "sesnsp", "IDEFC_MAnterior_ago2024.csv")
MUN     = here("data", "raw", "sesnsp_municipal", "IDM_MAnterior_ago2024.csv")
CON     = here("data", "raw", "conapo", "pobproy_inddemo.csv")
INEGI_MICRO = here("data", "raw", "inegi_defunciones")       # DEFUNxx.dbf, 1990-2020
PIBE    = here("data", "raw", "inegi_pibe", "conjunto_de_datos",
               "conjunto_de_datos_pibe_actividad_pibe2024_r.csv")

# ------------------------------------------------------------ derivados (clean)
POB     = here("data", "clean", "pob_municipal_2011_2017.csv")
INE     = here("data", "clean", "inegi")                     # hom_*.csv de 02_inegi_homicidios.py

# ------------------------------------------------------------------- salidas
SAL     = here("output", "resultados")                       # resultados.json, t*.csv, *.pkl
OUT     = here("output", "exploratorio")                     # gráficas de scripts exploratorios
FIG_EN  = here("output", "figuras", "en")
FIG_ES  = here("output", "figuras", "es")
DOCX    = here("output", "docx")
MAN_EN  = here("manuscrito", "en")                           # manuscript.md, anexos.md, references.md
MAN_ES  = here("manuscrito", "es")

asegurar(SAL, OUT, FIG_EN, FIG_ES, DOCX, INE, here("data", "clean"), here("output", "logs"),
         EMO, EMO17, os.path.dirname(SES), os.path.dirname(MUN), os.path.dirname(CON),
         INEGI_MICRO, here("data", "raw", "inegi_pibe"))
