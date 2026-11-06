# -*- coding: utf-8 -*-
"""
figsize.py — relación alto/ancho de cada figura, para los constructores docx
=============================================================================
`build.js` y `build_es.js` incrustan cada PNG a un ancho fijo y necesitan su
proporción para no deformarla. Antes se calculaba a mano; aquí queda escrito
para que el pipeline no dependa de un paso manual.

Uso:  python -I codigo/figsize.py
"""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import json
import os
from PIL import Image

PARES = [(_r.FIG_EN, _r.MAN_EN + "/figsize.json",
          ["Fig1", "Fig2", "Fig3", "Fig4"]),
         (_r.FIG_ES, _r.MAN_ES + "/figsize.json",
          ["delitos_es", "exposicion_es", "evento_es", "conglomerados_es"])]

for carpeta, salida, nombres in PARES:
    d = {}
    for n in nombres:
        ruta = os.path.join(carpeta, f"{n}.png")
        if not os.path.exists(ruta):
            print(f"  falta {ruta}")
            continue
        with Image.open(ruta) as im:
            w, h = im.size
        d[n] = {"w": w, "h": h, "ratio": round(h / w, 6)}
    tmp = f"{salida}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, salida)
    print(f"{salida}: " + ", ".join(f"{k} {v['ratio']}" for k, v in d.items()))
