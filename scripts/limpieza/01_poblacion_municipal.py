# -*- coding: utf-8 -*-
"""
01_poblacion_municipal.py — población municipal promedio 2011-2017
==================================================================
Insumo : data/raw/conapo/pobproy_inddemo.csv
         (CONAPO, proyecciones de población municipal: CLAVE, ANO, POB_MIT_MUN)
Salida : data/clean/pob_municipal_2011_2017.csv   (CLAVE, pob)

Promedia la población a mitad de año de 2011 a 2017 por municipio. Es el
denominador de la tasa municipal de homicidio que usa funciones/municipal.py.
Debe dar 2 475 municipios.
"""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import os
import pandas as pd

if not os.path.exists(_r.CON):
    sys_msg = (f"Falta {_r.CON}.\nDescárgalo siguiendo INSTRUCCIONES_DATOS.md "
               "(CONAPO, proyecciones municipales).")
    raise SystemExit(sys_msg)

pob = pd.read_csv(_r.CON, encoding="latin-1", low_memory=False,
                  usecols=["CLAVE", "ANO", "POB_MIT_MUN"])
out = (pob[pob.ANO.between(2011, 2017)]
       .groupby("CLAVE").POB_MIT_MUN.mean().rename("pob").reset_index())
out.to_csv(_r.POB, index=False)
print(f"Escrito: {_r.POB}  ({len(out):,} municipios; se esperan 2,475)")
