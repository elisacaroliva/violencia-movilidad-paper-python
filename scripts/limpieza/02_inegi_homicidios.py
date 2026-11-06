# -*- coding: utf-8 -*-
"""
inegi_homicidios.py — panel de homicidios de INEGI, 1990-2020
==============================================================
Lee los microdatos de defunciones generales y construye paneles de homicidio
por entidad-año y municipio-año, de ocurrencia y de residencia.

Por qué esta fuente y no el SESNSP
----------------------------------
  * Cuenta DEFUNCIONES, es decir víctimas, no expedientes abiertos ante el
    ministerio público. Un homicidio con tres víctimas son tres registros.
  * Un acta de defunción se subregistra mucho menos que una denuncia.
  * Empieza en 1990, siete años antes que la serie estatal del SESNSP y
    veintiuno antes que la municipal.

Identificación del homicidio
----------------------------
Se usa PRESUNTO == 2, que es la clasificación de la propia INEGI y es
consistente a través del cambio de CIE-9 a CIE-10 en 1998. Se verifica contra
los códigos de causa: E960-E969 en CIE-9 (que en el archivo vienen sin la E,
como 9654) y X85-Y09 en CIE-10.

Año de ocurrencia, no de registro
---------------------------------
Una muerte ocurrida en diciembre puede registrarse al año siguiente y aparece
en el archivo del año siguiente. Por eso se agrega por ANIO_OCUR recorriendo
TODOS los archivos, no por el año del archivo. El último año queda incompleto
por las defunciones que se registrarán después, y se marca como tal.

Uso:  python -I inegi_homicidios.py <carpeta_de_microdatos> <carpeta_salida>
"""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import collections
import glob
import os
import sys

from dbfread import DBF

RAIZ = sys.argv[1] if len(sys.argv) > 1 else _r.INEGI_MICRO
SAL = sys.argv[2] if len(sys.argv) > 2 else _r.INE
os.makedirs(SAL, exist_ok=True)

CAMPOS = ("PRESUNTO", "ENT_OCURR", "MUN_OCURR", "ENT_RESID", "MUN_RESID",
          "ANIO_OCUR", "SEXO", "EDAD")


def archivos():
    """Un DEFUNxx.dbf por año, sin repetir, ordenados."""
    vistos = {}
    for p in glob.glob(f"{RAIZ}/**/*.dbf", recursive=True) + \
             glob.glob(f"{RAIZ}/**/*.DBF", recursive=True):
        n = os.path.basename(p).lower()
        if not n.startswith("defun"):
            continue
        vistos.setdefault(n, p)
    return [vistos[k] for k in sorted(vistos)]


def ent(v):
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    return v if 1 <= v <= 32 else None


def mun(e, m):
    try:
        m = int(m)
    except (TypeError, ValueError):
        return None
    return e * 1000 + m if 1 <= m <= 570 else None


def anio(v):
    """El año viene en dos dígitos hasta 1998 y en cuatro desde 1999.

    En los archivos de dos dígitos, 99 es el código de "ignorado" y no el año
    1999, porque esos archivos no pueden contener defunciones de 1999. En los
    de cuatro dígitos el código de ignorado es 9999.
    """
    s = str(v).strip()
    if not s.isdigit():
        return None
    n = int(s)
    if len(s) <= 2:
        return 1900 + n if 80 <= n <= 98 else None
    return n if 1979 <= n <= 2021 else None


def edad_anios(v):
    """EDAD viene como unidad+cantidad: 4xxx son años cumplidos."""
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    if 4001 <= v <= 4120:
        return v - 4000
    if v < 4000:
        return 0                       # horas, días o meses
    return None


ent_oc = collections.Counter()
mun_oc = collections.Counter()
ent_re = collections.Counter()
mun_re = collections.Counter()
h1539 = collections.Counter()
cie = collections.Counter()
total_leidos = 0
total_hom = 0

for ruta in archivos():
    t = DBF(ruta, encoding="latin-1", load=False, ignore_missing_memofile=True)
    campos = set(t.field_names)
    falta = [c for c in CAMPOS if c not in campos]
    n_arch = 0
    for r in t:
        total_leidos += 1
        if r.get("PRESUNTO") not in (2, "2"):
            continue
        a = anio(r.get("ANIO_OCUR"))
        if a is None:
            continue
        total_hom += 1
        n_arch += 1
        c = str(r.get("CAUSA_DEF") or "")[:4]
        cie[("CIE9" if c[:2] == "96" and not c[:1].isalpha() else
             "CIE10" if c[:1] in "XY" else "otro")] += 1
        eo = ent(r.get("ENT_OCURR"))
        if eo:
            ent_oc[(eo, a)] += 1
            mo = mun(eo, r.get("MUN_OCURR"))
            if mo:
                mun_oc[(mo, a)] += 1
            s = r.get("SEXO")
            ed = edad_anios(r.get("EDAD"))
            if s in (1, "1") and ed is not None and 15 <= ed <= 39:
                h1539[(eo, a)] += 1
        er = ent(r.get("ENT_RESID"))
        if er:
            ent_re[(er, a)] += 1
            mr = mun(er, r.get("MUN_RESID"))
            if mr:
                mun_re[(mr, a)] += 1
    print(f"  {os.path.basename(ruta):16s} {len(t):>9,} registros  "
          f"{n_arch:>7,} homicidios"
          + (f"  [faltan campos: {','.join(falta)}]" if falta else ""),
          flush=True)

print(f"\nLeidos {total_leidos:,} registros; {total_hom:,} homicidios.")
print("Reparto por era de CIE:", dict(cie))


def escribir(cont, nombre, col):
    import csv
    with open(f"{SAL}/{nombre}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([col, "anio", "homicidios"])
        for (k, a), v in sorted(cont.items()):
            w.writerow([k, a, v])
    print(f"  {SAL}/{nombre}.csv  ({len(cont):,} celdas)")


print("\nEscrito:")
escribir(ent_oc, "hom_entidad_ocurrencia", "cve")
escribir(ent_re, "hom_entidad_residencia", "cve")
escribir(mun_oc, "hom_municipio_ocurrencia", "cvemun")
escribir(mun_re, "hom_municipio_residencia", "cvemun")
escribir(h1539, "hom_hombres_15_39_ocurrencia", "cve")

print("\nTotales nacionales por año de ocurrencia (para cotejar):")
nac = collections.Counter()
for (e, a), v in ent_oc.items():
    nac[a] += v
for a in sorted(nac):
    if 1990 <= a <= 2020:
        print(f"  {a}: {nac[a]:>7,}")
