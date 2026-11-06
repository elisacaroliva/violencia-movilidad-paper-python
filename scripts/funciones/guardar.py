# -*- coding: utf-8 -*-
"""
guardar.py — escritura segura de resultados.json
=================================================
Dos fallos reales motivaron este módulo y los dos dejaron el archivo de
resultados inservible a media escritura:

  1. `json.dump` escribe directo al descriptor. Si falla a la mitad —por
     ejemplo con una clave que no sabe serializar— el archivo ya quedó
     truncado y se perdió la corrida completa. Se serializa a cadena
     primero y se escribe a un temporal que luego se renombra, de modo que
     el archivo bueno sólo se sustituye cuando el nuevo está completo.

  2. pandas y numpy devuelven `int32`, `int64` y `float64` donde uno espera
     `int` y `float`. Como valores el codificador los tolera mal y como
     CLAVES de diccionario los rechaza de plano. `limpio` los normaliza en
     claves y en valores, recorriendo la estructura entera.

Uso:
    from guardar import guardar
    guardar(R, f"{SAL}/resultados.json")
"""
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import json
import os


def limpio(o):
    """Convierte escalares de numpy y pandas a tipos nativos de Python.

    Recorre diccionarios, listas y tuplas, y normaliza tanto las claves como
    los valores. Lo que no reconoce lo deja intacto para que el codificador
    falle con un mensaje claro en lugar de escribir algo a medias.
    """
    if isinstance(o, dict):
        return {(k if isinstance(k, (str, bool)) or k is None else
                 int(k) if hasattr(k, "__index__") else str(k)): limpio(v)
                for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [limpio(v) for v in o]
    if isinstance(o, bool):
        return o
    if hasattr(o, "item") and not isinstance(o, (str, bytes)):
        try:
            return o.item()                       # escalar de numpy
        except (ValueError, AttributeError):
            return o
    return o


def guardar(R, ruta, indent=2):
    """Escribe R como JSON de forma atómica. Nunca deja el destino truncado."""
    txt = json.dumps(limpio(R), indent=indent, ensure_ascii=False)
    tmp = f"{ruta}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, ruta)
