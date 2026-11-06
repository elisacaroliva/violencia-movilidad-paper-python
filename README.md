# Violencia del crimen organizado y persistencia intergeneracional en México

Paquete de replicación del manuscrito del **Equipo 4** (Revilla, Flores, Ortega, Oliva).
Todo el análisis está en Python; el ensamblado opcional de los `.docx` usa Node.js.

**Semilla aleatoria: 20261102**, fijada en todo script que sortea números: las pruebas de
permutación, las inicializaciones de k-medias y la estabilidad por submuestras se reproducen
exactamente.

Ninguna cifra del artículo está escrita a mano: todas salen de
`output/resultados/resultados.json`, que escribe `03_congelar.py` y completan los pasos 4-13.
Los scripts de cuadros sólo dan formato y no hacen aritmética.

---

## Inicio rápido

```bash
# 1. Clonar
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>

# 2. Entorno de Python (>= 3.10)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. (Opcional) Node.js para armar los .docx
npm install

# 4. Colocar las bases en data/raw/  ->  ver INSTRUCCIONES_DATOS.md
python scripts/00_correr_todo.py --revisar

# 5. Correr todo
python scripts/00_correr_todo.py
```

`00_correr_todo.py` es el equivalente de `source("scripts/00_correr_todo.R")`: corre cada paso en
orden, salta (y avisa) los que no tienen sus insumos y deja la bitácora en
`output/logs/corrida.csv`. Opciones: `--desde N`, `--solo N M`, `--sin-docx`, `--continuar`.

## Rutas: el equivalente a `here::here()`

En la raíz hay un archivo marcador **`.here`**. `scripts/funciones/rutas.py` lo busca hacia
arriba y construye todas las rutas desde ahí:

```python
import rutas as _r
_r.here("data", "raw", "sesnsp")    # <raíz>/data/raw/sesnsp
_r.SES, _r.EMO, _r.SAL              # constantes con las rutas de cada insumo y salida
```

Por eso los scripts corren igual en cualquier computadora, desde cualquier carpeta, sin editar
una sola línea. Si los datos viven en otro disco, basta con definir la variable de entorno
`PROYECTO_RAIZ`.

## Estructura

```
.
├── .here                         marcador de raíz (como here::here())
├── README.md
├── INSTRUCCIONES_DATOS.md        de dónde bajar cada base y dónde ponerla
├── requirements.txt              dependencias de Python
├── package.json                  dependencia de Node (docx)
├── data/
│   ├── raw/                      bases originales  (NO se suben; ver .gitignore)
│   └── clean/                    derivados que escribe el pipeline
├── scripts/
│   ├── 00_correr_todo.py         corre el pipeline completo
│   ├── funciones/                módulos compartidos (se importan, no se corren)
│   │   ├── rutas.py              here() y todas las rutas del proyecto
│   │   ├── graficas_entregable1.py  cargadores: población, panel SESNSP, índices
│   │   ├── base.py               muestra, rangos ponderados, dosis y estimador de triple diferencia
│   │   ├── municipal.py          diseño municipal intraestatal
│   │   ├── conglomerados_perm.py inferencia por permutación (FWL + una sola QR)
│   │   └── guardar.py            escritura atómica de resultados.json
│   ├── limpieza/
│   │   ├── 01_poblacion_municipal.py
│   │   └── 02_inegi_homicidios.py
│   ├── resultados/
│   │   ├── 03_congelar.py        script maestro: cada estimación del manuscrito
│   │   ├── 04_congelar2.py       eventos municipal, DBSCAN municipal, transiciones
│   │   ├── 05_redatar.py         refechado de la dosis por quiebre estructural
│   │   ├── 06_movilidad_absoluta.py
│   │   ├── 07_recesion.py        control por la contracción de 2008-2009
│   │   ├── 08_inegi_analisis.py  tres índices de exposición de estadísticas vitales
│   │   ├── 09_inegi_cuadro9.py   cuadro 9: SESNSP contra INEGI
│   │   ├── 10_municipal_perfil.py
│   │   ├── 11_transiciones.py
│   │   ├── 12_pool_emovi.py      armonización EMOVI 2017-2023
│   │   └── 13_verificar.py       recomputa cifras heredadas; agrupamiento contra k = 1
│   ├── figuras/
│   │   ├── 14_figuras_articulo.py   figuras 1-4 (inglés), 174 mm, 600 ppp
│   │   ├── 15_figuras_es.py         figuras en español
│   │   └── 16_figsize.py            proporciones para el .docx
│   ├── manuscrito/
│   │   ├── 17_tablas.py / 18_tablas_es.py   formato de cuadros -> manuscrito/*/tables.json
│   │   ├── 19_limpiar_math.py               LaTeX -> álgebra legible
│   │   └── 20_build.js / 21_build_es.js     ensamblan los .docx
│   └── exploratorio/             diagnóstico previo al congelado; no alimenta el documento
├── manuscrito/
│   ├── en/                       manuscript.md, anexos.md, references.md
│   └── es/
└── output/
    ├── resultados/               resultados.json, t*.csv, objetos intermedios
    ├── figuras/{en,es}/
    ├── docx/
    ├── logs/                     corrida.csv
    └── referencia/               resultados.json y tables*.json congelados, para comparar
```

`output/referencia/` guarda la versión congelada de los resultados que aparece en el
manuscrito, de modo que quien replique puede comparar su `output/resultados/resultados.json`
contra ella. Contiene sólo estimaciones agregadas, ningún microdato.

## Pasos y dependencias

| Paso | Script | Insumos | Tiempo aprox. |
|---|---|---|---|
| 1 | `limpieza/01_poblacion_municipal.py` | CONAPO | segundos |
| 2 | `limpieza/02_inegi_homicidios.py` | INEGI defunciones (DBF) | varios minutos |
| 3 | `resultados/03_congelar.py` | EMOVI 2023, SESNSP estatal y municipal, paso 1 | ~1 min |
| 4-6, 10, 11, 13 | `resultados/…` | `resultados.json` | segundos c/u |
| 7 | `resultados/07_recesion.py` | PIB estatal INEGI | segundos |
| 8-9 | `resultados/08_…`, `09_…` | paso 2 + CONAPO | ~1 min |
| 12 | `resultados/12_pool_emovi.py` | EMOVI 2017 | segundos |
| 14-16 | `figuras/…` | `resultados.json` | ~30 s |
| 17-19 | `manuscrito/…` | `resultados.json` completo (incluye 7-9) | segundos |
| 20-21 | `manuscrito/*.js` | Node + `npm install` | segundos |

El orden importa: `03_congelar.py` va primero porque todo lo que sigue lee su JSON.
`19_limpiar_math.py` sale con error si encuentra notación que no reconoce, lo cual es
deliberado. `21_build_es.js` degrada con gracia: si faltan cuadros o figuras, deja en su lugar
un recuadro que dice qué script los genera.

## Tres errores que corregimos, y cómo ver que lo hicimos

Cada uno se reproduce revirtiendo una línea, y cada uno cambió un resultado reportado.

1. **Escala de escolaridad truncada.** Una versión anterior filtraba la variable de trece
   categorías con `v.where(v <= 9)`, lo que tiraba las dos categorías de superior y el código
   de "ninguno". El arreglo es el mapeo `ANIOS_ESC` al inicio de `funciones/base.py`.
2. **Interacción cohorte por rango ausente en el estudio de eventos.** Sin el bloque de año de
   nacimiento por rango de origen, la prueba conjunta de tendencias previas rechazaba con
   p = 0.039; con el bloque pasa con p = 0.795.
3. **Codificación de rural.** `p21.isin([3,4,5])` clasificaba 68 % de la muestra como rural.
   La definición del INEGI es un solo código. Véase `funciones/base.py`.

Un cuarto, en los microdatos del INEGI, está documentado en `limpieza/02_inegi_homicidios.py`:
`ANIO_OCUR` viene en dos dígitos hasta 1998 y en cuatro desde 1999.

## Verificación de la replicación

Con EMOVI 2023 y las dos series del SESNSP, `03_congelar.py` reproduce exactamente la
especificación base de `output/referencia/resultados.json`:
β₃ = +0.0161, e.e. = 0.0255, n = 15 558.

## Pendiente conocido

`16_figsize.py` y `21_build_es.js` esperan también `delitos_es.png` y `exposicion_es.png`
(figuras 1 y 2 en español), pero ningún script del paquete las genera todavía; el `.docx` en
español deja un recuadro en su lugar. Las versiones en inglés (`Fig1.png`, `Fig2.png`) sí se
producen en el paso 14.

## Declaración sobre el uso de inteligencia artificial generativa

El código de este paquete se escribió con asistencia de un modelo grande de lenguaje, como se
declara en el anexo E del manuscrito. Los resultados se verificaron recorriendo el análisis
desde los archivos fuente públicos. Ningún resultado se aceptó por afirmación del modelo.
