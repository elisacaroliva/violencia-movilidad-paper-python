# Cómo obtener las bases de datos

Este repositorio **no incluye ninguna base**. La ESRU-EMOVI la distribuye el CEEY a solicitud y
las demás fuentes son públicas pero pesan demasiado para GitHub. Descarga cada archivo y
colócalo **exactamente** en la carpeta y con el nombre que se indican; todas las rutas se
resuelven desde la raíz del proyecto con `scripts/funciones/rutas.py` (el equivalente a
`here::here()`), así que no hay que editar ningún script.

Para revisar qué falta en cualquier momento:

```bash
python scripts/00_correr_todo.py --revisar
```

## Resumen

| # | Fuente | Archivo(s) esperado(s) | Carpeta | ¿Obligatorio? |
|---|---|---|---|---|
| 1 | CEEY, ESRU-EMOVI 2023 | `entrevistado_2023.dta`, `hogar_2023.dta` | `data/raw/emovi/` | Sí |
| 2 | SESNSP, incidencia estatal, metodología anterior 1997-2017 | `IDEFC_MAnterior_ago2024.csv` | `data/raw/sesnsp/` | Sí |
| 3 | SESNSP, incidencia municipal, metodología anterior 2011-2017 | `IDM_MAnterior_ago2024.csv` | `data/raw/sesnsp_municipal/` | Sí |
| 4 | CONAPO, proyecciones de población municipal | `pobproy_inddemo.csv` | `data/raw/conapo/` | Sí |
| 5 | INEGI, defunciones generales (microdatos DBF) 1990-2020 | `DEFUN90.dbf` … `DEFUN20.dbf` | `data/raw/inegi_defunciones/` | Para el cuadro de índices INEGI (pasos 2, 8, 9) |
| 6 | INEGI, PIB por entidad federativa, base 2018 | `conjunto_de_datos/conjunto_de_datos_pibe_actividad_pibe2024_r.csv` | `data/raw/inegi_pibe/` | Para el control de recesión (paso 7) |
| 7 | CEEY, ESRU-EMOVI 2017 | `entrevistado_2017.dta`, `hogar_2017.dta` | `data/raw/emovi2017/` | Sólo para el cotejo entre rondas (paso 12) |

Los pasos 17 y 18 (cuadros) leen las secciones de `resultados.json` que producen los pasos 7-9,
así que para reproducir **el documento completo** se necesitan las siete fuentes. Sin las
opcionales, el pipeline produce igual todas las estimaciones principales, el diseño municipal,
el estudio de eventos, la inferencia por permutación, el agrupamiento y las figuras.

---

## 1. ESRU-EMOVI 2023 (CEEY)

- **Dónde:** <https://ceey.org.mx/encuesta-esru-de-movilidad-social-en-mexico-2023/>
- **Cómo:** el CEEY entrega las bases a solicitud (formulario en su sitio). Pide la versión en
  Stata (`.dta`).
- **Qué colocar:** `data/raw/emovi/entrevistado_2023.dta` y `data/raw/emovi/hogar_2023.dta`.
- **Variables que se usan:** ver `scripts/funciones/base.py` (`construir()`) y
  `scripts/funciones/graficas_entregable1.py` (`indice_pca()`).

## 2. SESNSP estatal, metodología anterior (1997-2017)

- **Dónde:** <https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva>
  → sección *Incidencia delictiva del fuero común, metodología anterior* → serie **estatal
  1997-2017**.
- **Qué colocar:** el CSV, renombrado a `data/raw/sesnsp/IDEFC_MAnterior_ago2024.csv`.
  (Se usó el corte publicado en agosto de 2024. Si el sitio sólo ofrece una versión posterior
  de la misma serie, las cifras deberían coincidir porque la serie está cerrada desde 2017.)
- **Formato esperado:** codificación latin-1, una fila por entidad-año-delito con columnas
  `ENERO` … `DICIEMBRE`.

## 3. SESNSP municipal, metodología anterior (2011-2017)

- **Dónde:** misma página que el punto 2 → *2011-2017 (Fuero común - Delitos). Incidencia
  delictiva municipal*. Viene en `.zip`; descomprímelo.
- **Qué colocar:** `data/raw/sesnsp_municipal/IDM_MAnterior_ago2024.csv`.
- **Columnas que se usan:** `INEGI` (clave municipal), `AÑO`, `MODALIDAD`, `TIPO`,
  `ENERO` … `DICIEMBRE`.

## 4. CONAPO, proyecciones de población municipal

- **Dónde:** <https://www.gob.mx/conapo> → *Proyecciones de la población de los municipios de
  México, 2015-2030* (CONAPO, 2023), datos abiertos, archivo de indicadores demográficos.
- **Qué colocar:** `data/raw/conapo/pobproy_inddemo.csv`.
- **Columnas que deben venir:** `CLAVE` (clave municipal de 5 dígitos), `CLAVE_ENT`, `ANO`,
  `POB_MIT_MUN` (población a mitad de año). Si tu descarga trae otro nombre de archivo pero
  esas columnas, basta con renombrarlo.
- **Derivado:** el paso 1 (`scripts/limpieza/01_poblacion_municipal.py`) promedia
  `POB_MIT_MUN` de 2011 a 2017 por `CLAVE` y escribe `data/clean/pob_municipal_2011_2017.csv`
  (deben salir 2 475 municipios).

## 5. INEGI, microdatos de defunciones 1990-2020

- **Dónde:** <https://www.inegi.org.mx/programas/mortalidad/#datos_abiertos> → *Microdatos*,
  un archivo por año, formato **DBF**.
- **Qué colocar:** descomprime todos los años dentro de `data/raw/inegi_defunciones/` (pueden
  quedar en subcarpetas; el script busca `DEFUN*.dbf` de forma recursiva). Son alrededor de
  1.9 GB.
- **Derivado:** el paso 2 escribe en `data/clean/inegi/` los paneles
  `hom_entidad_ocurrencia.csv`, `hom_entidad_residencia.csv` y `hom_municipio_ocurrencia.csv`.
  El script imprime los totales nacionales por año para cotejarlos con las cifras publicadas
  (por ejemplo, 2007 debe dar 8 866 contra 8 867 publicados).

## 6. INEGI, PIB por entidad federativa (base 2018)

- **Dónde:** <https://www.inegi.org.mx/programas/pibent/2018/#datos_abiertos> → datos abiertos
  por actividad.
- **Qué colocar:** descomprime de modo que exista
  `data/raw/inegi_pibe/conjunto_de_datos/conjunto_de_datos_pibe_actividad_pibe2024_r.csv`.

## 7. ESRU-EMOVI 2017 (CEEY)

- **Dónde:** <https://ceey.org.mx> → ESRU-EMOVI 2017, a solicitud, como la de 2023.
- **Qué colocar:** `data/raw/emovi2017/entrevistado_2017.dta` y `hogar_2017.dta`.

---

## Estructura final esperada

```
data/
├── raw/
│   ├── emovi/              entrevistado_2023.dta, hogar_2023.dta
│   ├── emovi2017/          entrevistado_2017.dta, hogar_2017.dta
│   ├── sesnsp/             IDEFC_MAnterior_ago2024.csv
│   ├── sesnsp_municipal/   IDM_MAnterior_ago2024.csv
│   ├── conapo/             pobproy_inddemo.csv
│   ├── inegi_defunciones/  DEFUN90.dbf … DEFUN20.dbf
│   └── inegi_pibe/         conjunto_de_datos/conjunto_de_datos_pibe_actividad_pibe2024_r.csv
└── clean/                  (lo escribe el pipeline; no se edita a mano)
```

`.gitignore` impide que cualquier archivo de `data/` se suba a GitHub, salvo los `.gitkeep`
que conservan la estructura de carpetas.
