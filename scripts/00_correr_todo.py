# -*- coding: utf-8 -*-
"""
00_correr_todo.py — corre el paquete de replicación completo, en orden
======================================================================
Equivalente a `source("scripts/00_correr_todo.R")` en los proyectos de R.

Uso (desde cualquier carpeta dentro del repositorio):

    python scripts/00_correr_todo.py                 # todo
    python scripts/00_correr_todo.py --desde 14      # de las figuras en adelante
    python scripts/00_correr_todo.py --solo 3 4      # sólo esos pasos
    python scripts/00_correr_todo.py --sin-docx      # sin ensamblar los .docx (no requiere Node)
    python scripts/00_correr_todo.py --continuar     # no se detiene si un paso falla
    python scripts/00_correr_todo.py --revisar       # sólo revisa qué insumos faltan

Antes de correr, coloca las bases en data/raw/ (ver INSTRUCCIONES_DATOS.md).
Cada paso declara sus insumos; si falta uno, el paso se salta y se avisa.
Al final se escribe output/logs/corrida.csv con el estado y el tiempo de cada paso.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "funciones"))
import rutas as r  # noqa: E402

PY = sys.executable
# (número, script relativo a scripts/, insumos que deben existir, descripción)
PASOS = [
    (1,  "limpieza/01_poblacion_municipal.py",   [r.CON],
         "Población municipal CONAPO promedio 2011-2017"),
    (2,  "limpieza/02_inegi_homicidios.py",      [r.INEGI_MICRO + "/"],
         "Paneles de homicidio INEGI 1990-2020 (lee ~1.9 GB de DBF)"),
    (3,  "resultados/03_congelar.py",            [r.EMO + "/entrevistado_2023.dta", r.EMO + "/hogar_2023.dta",
                                                  r.SES, r.MUN, r.POB],
         "Script maestro: cada estimación -> output/resultados/resultados.json"),
    (4,  "resultados/04_congelar2.py",           [r.SAL + "/resultados.json", r.MUN],
         "Estudio de eventos municipal, DBSCAN municipal, transiciones"),
    (5,  "resultados/05_redatar.py",             [r.SAL + "/resultados.json"],
         "Refechado de la dosis por quiebre estructural"),
    (6,  "resultados/06_movilidad_absoluta.py",  [r.SAL + "/resultados.json"],
         "Perfil por percentil de origen"),
    (7,  "resultados/07_recesion.py",            [r.SAL + "/resultados.json", r.PIBE],
         "Control por la contracción de 2008-2009 (PIB estatal INEGI)"),
    (8,  "resultados/08_inegi_analisis.py",      [r.SAL + "/resultados.json", r.CON,
                                                  r.INE + "/hom_entidad_ocurrencia.csv"],
         "Tres índices de exposición de estadísticas vitales"),
    (9,  "resultados/09_inegi_cuadro9.py",       [r.SAL + "/resultados.json", r.CON,
                                                  r.INE + "/hom_entidad_ocurrencia.csv"],
         "Cuadro 9: SESNSP contra INEGI"),
    (10, "resultados/10_municipal_perfil.py",    [r.SAL + "/resultados.json"],
         "Perfil municipal por percentil"),
    (11, "resultados/11_transiciones.py",        [r.SAL + "/resultados.json"],
         "Transiciones por quintil y tipo de cambio entre escalas"),
    (12, "resultados/12_pool_emovi.py",          [r.EMO17 + "/entrevistado_2017.dta"],
         "Armonización ESRU-EMOVI 2017 y 2023 (cotejo entre rondas)"),
    (13, "resultados/13_verificar.py",           [r.SAL + "/resultados.json"],
         "Recomputa cifras heredadas; métricas de agrupamiento contra k = 1"),
    (14, "figuras/14_figuras_articulo.py",       [r.SAL + "/resultados.json"],
         "Figuras 1-4 en inglés"),
    (15, "figuras/15_figuras_es.py",             [r.SAL + "/resultados.json"],
         "Figuras 1-4 en español"),
    (16, "figuras/16_figsize.py",                [],
         "Proporción de cada figura para los .docx"),
    (17, "manuscrito/17_tablas.py",              [r.SAL + "/resultados.json"],
         "Cuadros en inglés -> manuscrito/en/tables.json"),
    (18, "manuscrito/18_tablas_es.py",           [r.SAL + "/resultados.json"],
         "Cuadros en español -> manuscrito/es/tables.json"),
    (19, "manuscrito/19_limpiar_math.py",        [r.MAN_EN + "/manuscript.md"],
         "Sustituye LaTeX por álgebra legible"),
    (20, "manuscrito/20_build.js",               [r.MAN_EN + "/tables.json"],
         "Ensambla el .docx en inglés"),
    (21, "manuscrito/21_build_es.js",            [],
         "Ensambla el .docx en español"),
]


def faltantes(insumos):
    """Insumos ausentes. Una ruta que termina en '/' es carpeta y debe traer
    al menos un archivo además del .gitkeep."""
    out = []
    for i in insumos:
        if i.endswith("/"):
            d = i.rstrip("/")
            if not os.path.isdir(d) or not [f for f in os.listdir(d) if f != ".gitkeep"]:
                out.append(i)
        elif not os.path.exists(i):
            out.append(i)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", type=int, default=1)
    ap.add_argument("--solo", type=int, nargs="*")
    ap.add_argument("--sin-docx", action="store_true")
    ap.add_argument("--continuar", action="store_true")
    ap.add_argument("--revisar", action="store_true")
    a = ap.parse_args()

    if a.revisar:
        print(f"Raíz del proyecto: {r.RAIZ}\n")
        for n, s, ins, d in PASOS:
            f = [os.path.relpath(x.rstrip('/'), r.RAIZ) for x in faltantes(ins)
                 if "output" not in x and "clean" not in x and "manuscrito" not in x]
            print(f"{n:>2}  {'OK      ' if not f else 'FALTA   '}{s}" + (f"  <- {', '.join(f)}" if f else ""))
        return

    pasos = [p for p in PASOS if (a.solo and p[0] in a.solo) or (not a.solo and p[0] >= a.desde)]
    if a.sin_docx:
        pasos = [p for p in pasos if not p[1].endswith(".js")]

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    log, falla = [], False
    print(f"Raíz del proyecto: {r.RAIZ}")
    for n, s, ins, d in pasos:
        print(f"\n{'=' * 78}\n[{n:02d}] {s}\n     {d}\n{'=' * 78}")
        f = faltantes(ins)
        if f:
            msg = "; ".join(os.path.relpath(x.rstrip('/'), r.RAIZ) for x in f)
            print(f"  SE SALTA: faltan insumos -> {msg}")
            log.append([n, s, "saltado", 0, msg])
            continue
        if s.endswith(".js"):
            if not shutil.which("node"):
                print("  SE SALTA: Node.js no está instalado")
                log.append([n, s, "saltado", 0, "sin node"])
                continue
            cmd = ["node", str(r.RAIZ / "scripts" / s)]
        else:
            cmd = [PY, str(r.RAIZ / "scripts" / s)]
        t0 = time.time()
        res = subprocess.run(cmd, cwd=r.RAIZ, env=env)
        dt = round(time.time() - t0, 1)
        ok = res.returncode == 0
        log.append([n, s, "ok" if ok else "error", dt, "" if ok else f"código {res.returncode}"])
        print(f"  -> {'OK' if ok else 'ERROR'} en {dt} s")
        if not ok and not a.continuar:
            falla = True
            break

    os.makedirs(r.here("output", "logs"), exist_ok=True)
    with open(r.here("output", "logs", "corrida.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["paso", "script", "estado", "segundos", "nota"])
        w.writerows(log)
    print("\nResumen:")
    for n, s, e, dt, nota in log:
        print(f"  {n:>2}  {e:<8} {dt:>7} s  {s}  {nota}")
    print(f"\nBitácora: {r.here('output', 'logs', 'corrida.csv')}")
    sys.exit(1 if falla else 0)


if __name__ == "__main__":
    main()
