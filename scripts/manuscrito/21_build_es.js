/*
 * build_es.js — ensambla la versión en español del Entregable 3 como .docx
 * =======================================================================
 * Mismo formato que build.js, con rótulos en español (Cuadro, Figura,
 * Referencias, Anexo, Resumen, Palabras clave).
 *
 * Degrada con gracia: si no están tables.json, figsize.json ni las figuras
 * —porque no se ha corrido el pipeline en esta máquina— escribe el pie del
 * cuadro o de la figura y en su lugar un recuadro que dice qué script lo
 * genera. Con los datos en su sitio, el mismo script produce el documento
 * completo sin cambiar una línea.
 *
 * Uso:  node build_es.js
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ImageRun,
  PageBreak, Footer, PageNumber, LineRuleType,
} = require('docx');

// Rutas relativas a la raíz del repositorio (equivalente a here::here()):
// se busca hacia arriba el marcador `.here`, así que el script corre desde cualquier carpeta.
const RAIZ = (() => { let d = __dirname; while (!fs.existsSync(path.join(d, '.here'))) {
  const p = path.dirname(d); if (p === d) throw new Error('No encontré el marcador .here'); d = p; } return d; })();
const MAN = path.join(RAIZ, 'manuscrito', 'es');
const FIG = path.join(RAIZ, 'output', 'figuras', 'es');
const COD = path.join(RAIZ, 'scripts');
const DOCX = path.join(RAIZ, 'output', 'docx');
fs.mkdirSync(DOCX, { recursive: true });

const SERIF = 'Times New Roman';
const MONO = 'Courier New';
const ANCHO = 9360;               // 6.5 pulgadas en DXA
const PX = 624;                   // 6.5 pulgadas a 96 px/pulgada

// Numeración por orden de primera cita en el texto.
const NUM_TAB = { t1: 1, t2: 2, t3: 3, t5: 4, t7: 5, t4: 6, t6: 7, t8: 8, t9: 9 };
const NUM_FIG = { delitos_es: 1, exposicion_es: 2, evento_es: 3, conglomerados_es: 4 };

const hay = f => { try { return fs.existsSync(f); } catch (e) { return false; } };
const TABLAS = hay(`${MAN}/tables.json`)
  ? JSON.parse(fs.readFileSync(`${MAN}/tables.json`, 'utf8')) : null;
const FIGSIZE = hay(`${MAN}/figsize.json`)
  ? JSON.parse(fs.readFileSync(`${MAN}/figsize.json`, 'utf8')) : null;

// --------------------------------------------------------------- utilidades
const SIN = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const REGLA = { style: BorderStyle.SINGLE, size: 6, color: '000000' };

/** Convierte **negritas** y *cursivas* en runs. */
function runs(texto, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let i = 0, m;
  while ((m = re.exec(texto)) !== null) {
    if (m.index > i) out.push(new TextRun({ ...base, text: texto.slice(i, m.index) }));
    const t = m[0];
    if (t.startsWith('**')) {
      out.push(new TextRun({ ...base, text: t.slice(2, -2), bold: true }));
    } else {
      out.push(new TextRun({ ...base, text: t.slice(1, -1), italics: true }));
    }
    i = m.index + t.length;
  }
  if (i < texto.length) out.push(new TextRun({ ...base, text: texto.slice(i) }));
  return out.length ? out : [new TextRun({ ...base, text: '' })];
}

function celda(texto, w, opts = {}) {
  const { bold = false, align = AlignmentType.LEFT, size = 19,
          bordeAbajo = false, bordeArriba = false } = opts;
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    borders: {
      top: bordeArriba ? REGLA : SIN,
      bottom: bordeAbajo ? REGLA : SIN,
      left: SIN, right: SIN,
    },
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({
      alignment: align,
      spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
      children: [new TextRun({ text: texto, bold, size, font: SERIF })],
    })],
  });
}

/** Cuadro del manuscrito, en estilo de reglas horizontales. */
function tabla(t) {
  const w = t.anchos.map(a => Math.round(ANCHO * a / 100));
  w[0] += ANCHO - w.reduce((a, b) => a + b, 0);     // cuadra el redondeo
  const paneles = new Set(t.paneles || []);

  const filas = [];
  filas.push(new TableRow({
    tableHeader: true,
    children: t.cols.map((c, j) => celda(c, w[j], {
      bold: true, bordeAbajo: true, bordeArriba: true,
      align: j === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
    })),
  }));
  t.filas.forEach((f, i) => {
    const esPanel = paneles.has(i);
    const ultima = i === t.filas.length - 1;
    filas.push(new TableRow({
      children: f.map((v, j) => celda(v, w[j], {
        bold: esPanel,
        bordeAbajo: ultima,
        align: j === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
      })),
    }));
  });

  return new Table({
    columnWidths: w,
    width: { size: ANCHO, type: WidthType.DXA },
    borders: { top: SIN, bottom: SIN, left: SIN, right: SIN,
               insideHorizontal: SIN, insideVertical: SIN },
    rows: filas,
  });
}

/** Recuadro que ocupa el lugar de un exhibit que aún no se ha generado. */
function pendiente(texto) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 240, line: 300, lineRule: LineRuleType.AUTO },
    border: {
      top: { style: BorderStyle.SINGLE, size: 4, color: '888888', space: 8 },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: '888888', space: 8 },
      left: { style: BorderStyle.SINGLE, size: 4, color: '888888', space: 8 },
      right: { style: BorderStyle.SINGLE, size: 4, color: '888888', space: 8 },
    },
    children: [new TextRun({ text: texto, size: 20, font: SERIF, italics: true,
                             color: '555555' })],
  });
}

function bloqueTabla(id, pie) {
  const num = TABLAS && TABLAS[id] ? TABLAS[id].num : NUM_TAB[id];
  const titulo = TABLAS && TABLAS[id] ? TABLAS[id].titulo : pie;
  const out = [
    new Paragraph({
      spacing: { before: 240, after: 100, line: 240, lineRule: LineRuleType.AUTO },
      keepNext: true,
      children: [
        new TextRun({ text: `Cuadro ${num}`, bold: true, size: 22, font: SERIF }),
        new TextRun({ text: `  ${titulo}`, size: 22, font: SERIF }),
      ],
    }),
  ];
  if (TABLAS && TABLAS[id]) {
    out.push(tabla(TABLAS[id]));
    if (TABLAS[id].nota) {
      out.push(new Paragraph({
        spacing: { before: 100, after: 240, line: 240, lineRule: LineRuleType.AUTO },
        children: [
          new TextRun({ text: 'Notas: ', italics: true, size: 19, font: SERIF }),
          new TextRun({ text: TABLAS[id].nota, size: 19, font: SERIF }),
        ],
      }));
    }
  } else {
    out.push(pendiente(
      `[Cuadro ${num} — cuerpo numérico. Lo genera codigo/tablas_es.py a partir de ` +
      `resultados/resultados.json, clave «${id}». Pendiente de recomputar.]`));
  }
  return out;
}

function bloqueFigura(nombre, pie) {
  const num = NUM_FIG[nombre] || nombre.replace(/\D/g, '');
  const ruta = `${FIG}/${nombre}.png`;
  const out = [];
  if (hay(ruta) && FIGSIZE && FIGSIZE[nombre]) {
    const data = fs.readFileSync(ruta);
    const alto = Math.round(PX * FIGSIZE[nombre].ratio);
    out.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 240, after: 100, line: 240, lineRule: LineRuleType.AUTO },
      keepNext: true,
      children: [new ImageRun({ data, type: 'png',
                                transformation: { width: PX, height: alto } })],
    }));
  } else {
    out.push(pendiente(
      `[Figura ${num} — imagen. La genera codigo/figuras_es.py, archivo ` +
      `figuras_es/${nombre}.png. Pendiente de recomputar.]`));
  }
  out.push(new Paragraph({
    spacing: { before: 0, after: 240, line: 240, lineRule: LineRuleType.AUTO },
    children: [
      new TextRun({ text: `Figura ${num}`, bold: true, size: 20, font: SERIF }),
      new TextRun({ text: `  ${pie}`, size: 20, font: SERIF }),
    ],
  }));
  return out;
}

/** Cuadro escrito en markdown dentro de los anexos. */
function tablaMarkdown(lineas) {
  const filas = lineas
    .filter(l => !/^\|[\s:|-]+\|$/.test(l.trim()))
    .map(l => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|')
               .map(c => c.trim()));
  const ncol = Math.max(...filas.map(f => f.length));
  const w = new Array(ncol).fill(Math.floor(ANCHO / ncol));
  w[0] = ANCHO - w.slice(1).reduce((a, b) => a + b, 0);
  if (ncol === 2) { w[0] = Math.round(ANCHO * 0.30); w[1] = ANCHO - w[0]; }
  if (ncol === 3) { w[0] = Math.round(ANCHO * 0.30); w[1] = Math.round(ANCHO * 0.40);
                    w[2] = ANCHO - w[0] - w[1]; }

  return new Table({
    columnWidths: w,
    width: { size: ANCHO, type: WidthType.DXA },
    borders: { top: SIN, bottom: SIN, left: SIN, right: SIN,
               insideHorizontal: SIN, insideVertical: SIN },
    rows: filas.map((f, i) => new TableRow({
      tableHeader: i === 0,
      children: Array.from({ length: ncol }, (_, j) => {
        const texto = (f[j] || '').replace(/\*\*/g, '').replace(/\*/g, '');
        return celda(texto, w[j], {
          bold: i === 0,
          bordeArriba: i === 0,
          bordeAbajo: i === 0 || i === filas.length - 1,
        });
      }),
    })),
  });
}

// ------------------------------------------------------- analizador de texto
function analizar(texto) {
  if (texto === undefined || texto === null) return [];
  const hijos = [];
  const lineas = String(texto).split('\n');
  let i = 0;
  while (i < lineas.length) {
    const l = lineas[i];
    const t = l.trim();

    if (t === '' || t === '---') { i++; continue; }

    if (t.startsWith('|')) {
      const bloque = [];
      while (i < lineas.length && lineas[i].trim().startsWith('|')) {
        bloque.push(lineas[i]); i++;
      }
      hijos.push(tablaMarkdown(bloque));
      hijos.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
      continue;
    }

    let m;
    if ((m = t.match(/^\[TABLE:(\w+)\|([\s\S]*)\]$/))) {
      hijos.push(...bloqueTabla(m[1], m[2])); i++; continue;
    }
    if ((m = t.match(/^\[FIGURE:(\w+)\|([\s\S]*)\]$/))) {
      hijos.push(...bloqueFigura(m[1], m[2])); i++; continue;
    }
    if ((m = t.match(/^\[EQ\](.*)\[\/EQ\]$/))) {
      hijos.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 120, line: 240, lineRule: LineRuleType.AUTO },
        children: [new TextRun({ text: m[1], size: 23, font: SERIF, italics: true })],
      }));
      i++; continue;
    }

    if (t.startsWith('### ')) {
      hijos.push(new Paragraph({
        heading: HeadingLevel.HEADING_2, keepNext: true,
        spacing: { before: 240, after: 120, line: 300, lineRule: LineRuleType.AUTO },
        children: [new TextRun({ text: t.slice(4), bold: true, size: 24, font: SERIF,
                                 color: '000000' })],
      }));
      i++; continue;
    }
    if (t.startsWith('## ')) {
      hijos.push(new Paragraph({
        heading: HeadingLevel.HEADING_1, keepNext: true,
        spacing: { before: 320, after: 140, line: 300, lineRule: LineRuleType.AUTO },
        children: [new TextRun({ text: t.slice(3), bold: true, size: 26, font: SERIF,
                                 color: '000000' })],
      }));
      i++; continue;
    }
    if (t.startsWith('# ')) {
      hijos.push(new Paragraph({
        heading: HeadingLevel.HEADING_1, pageBreakBefore: true, keepNext: true,
        spacing: { before: 0, after: 200, line: 300, lineRule: LineRuleType.AUTO },
        children: [new TextRun({ text: t.slice(2), bold: true, size: 28, font: SERIF,
                                 color: '000000' })],
      }));
      i++; continue;
    }

    if ((m = t.match(/^(\d+)\.\s+(.*)$/))) {
      hijos.push(new Paragraph({
        spacing: { before: 60, after: 60, line: 360, lineRule: LineRuleType.AUTO },
        indent: { left: 400, hanging: 280 },
        children: runs(`${m[1]}.  ${m[2]}`, { size: 24, font: SERIF }),
      }));
      i++; continue;
    }

    hijos.push(new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { before: 0, after: 120, line: 360, lineRule: LineRuleType.AUTO },
      children: runs(t, { size: 24, font: SERIF }),
    }));
    i++;
  }
  return hijos.flat();
}

// ------------------------------------------------------------- insumos
const man = fs.readFileSync(`${MAN}/manuscript.md`, 'utf8');
const refs = fs.readFileSync(`${MAN}/references.md`, 'utf8');
const anx = fs.readFileSync(`${MAN}/anexos.md`, 'utf8');

const titulo = man.match(/^#\s+(.*)$/m)[1];
const resumen = man.split('[ABSTRACT]')[1].split('[/ABSTRACT]')[0].trim();
const claves = man.split('[KEYWORDS]')[1].split('[/KEYWORDS]')[0].trim();
const jel = man.split('[JEL]')[1].split('[/JEL]')[0].trim();
const cuerpo = man.split('[/JEL]')[1];

// Conteo estricto: prosa de las secciones 1 a 7. Se excluyen los encabezados
// y los marcadores de cuadro y figura COMPLETOS, incluido su pie, porque la
// revista cuenta sólo el cuerpo. El contador anterior partía las palabras
// acentuadas y dejaba pasar parte de los pies, así que daba de más.
const contar = (t) => (t
  .replace(/^\s*\[(TABLE|FIGURE):[^\n]*$/gmu, ' ')
  .replace(/\[\/?EQ[^\]]*\]/gu, ' ')
  .replace(/^#+ .*$/gmu, ' ')
  .match(/\p{L}[\p{L}\p{M}'\u2019-]*/gu) || []).length;
const palabras = contar(cuerpo);
const _ab = (man.match(/\[ABSTRACT\]([\s\S]*?)\[\/ABSTRACT\]/) || [, ''])[1];
const palabras_resumen = (_ab.match(/\p{L}[\p{L}\p{M}'\u2019-]*/gu) || []).length;

const trozos = anx.split(/\n(?=# Anexo )/);
const declaraciones = trozos[0];
const apendices = {};
trozos.slice(1).forEach(s => {
  const m = s.match(/^# Anexo (\w)/);
  if (m) apendices[m[1]] = s;
});

// --------------------------------------------------------- Anexo D: el código
const ARCHIVOS = [
  ['funciones/graficas_entregable1.py', 'Cargadores de datos: población estatal, panel delictivo del SESNSP, índice de violencia y componente principal del índice de activos.'],
  ['funciones/base.py', 'Construcción compartida de la muestra analítica, los rangos, la dosis y el estimador de triple diferencia.'],
  ['funciones/municipal.py', 'Diseño municipal intraestatal: tasas municipales de homicidio, estimación y estudio de eventos municipal.'],
  ['funciones/conglomerados_perm.py', 'Inferencia por permutación dentro de un subconjunto de entidades.'],
  ['resultados/03_congelar.py', 'Script maestro. Produce cada cifra del manuscrito y escribe resultados.json.'],
  ['resultados/04_congelar2.py', 'Complementos: estudio de eventos municipal con y sin controles de tamaño de localidad, DBSCAN municipal, transiciones por quintil.'],
  ['resultados/05_redatar.py', 'Refechado de la dosis por quiebre estructural a nivel de conglomerado y de entidad.'],
  ['resultados/06_movilidad_absoluta.py', 'Perfil del efecto sobre el rango esperado de destino por percentil de origen.'],
  ['resultados/07_recesion.py', 'Control por la contracción estatal de 2008-2009 con el PIB por entidad del INEGI.'],
  ['limpieza/02_inegi_homicidios.py', 'Paneles de homicidio por entidad y municipio a partir de los microdatos de defunciones del INEGI, 1990-2020.'],
  ['resultados/08_inegi_analisis.py', 'Reestimación con los tres índices de exposición construidos sobre estadísticas vitales.'],
  ['resultados/13_verificar.py', 'Recomputa las figuras heredadas en lugar de confiar en ellas y calcula las métricas de agrupamiento contra el modelo de referencia k = 1.'],
  ['figuras/15_figuras_es.py', 'Las cuatro figuras en español, al ancho, resolución y tipografía que pide la revista.'],
  ['manuscrito/18_tablas_es.py', 'Da formato a resultados.json y produce los nueve cuadros en español.'],
  ['resultados/11_transiciones.py', 'La ruta de transiciones por quintil y el tipo de cambio entre escalas.'],
  ['resultados/12_pool_emovi.py', 'Armonización de las rondas ESRU-EMOVI 2017 y 2023.'],
  ['manuscrito/21_build_es.js', 'Ensamblado de este documento.'],
];

function anexoD() {
  const out = [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
      spacing: { after: 200, line: 300, lineRule: LineRuleType.AUTO },
      children: [new TextRun({ text: 'Anexo D. Código reproducible', bold: true,
                               size: 28, font: SERIF, color: '000000' })],
    }),
    ...analizar(
      'Cada cuadro y cada figura de este manuscrito los produce el código que sigue, a partir de las fuentes públicas nombradas en la declaración de disponibilidad de datos. ' +
      'La semilla aleatoria está fijada en 20261102 y se establece en cada script que sortea números, de modo que las pruebas de permutación, las inicializaciones de k-medias y el ejercicio de estabilidad por submuestras se reproducen exactamente. ' +
      'El pipeline corre en el orden listado: primero los cargadores y el módulo de construcción compartida, luego el script maestro, después los complementos y la verificación, enseguida las figuras y los cuadros, y al final este script de ensamblado. ' +
      'Software: Python 3.13 con numpy, pandas, statsmodels, scipy, scikit-learn, pyreadstat, matplotlib y Pillow; Node.js con el paquete docx. ' +
      'Las rutas al inicio de cada script apuntan a los archivos fuente y son las únicas líneas que hay que cambiar para correr el código en otra máquina.'
    ),
  ];
  out.push(new Paragraph({
    spacing: { before: 200, after: 120, line: 300, lineRule: LineRuleType.AUTO },
    children: [new TextRun({ text: 'D.1 Inventario de archivos', bold: true,
                             size: 24, font: SERIF })],
  }));
  const w = [Math.round(ANCHO * 0.26), Math.round(ANCHO * 0.10)];
  w.push(ANCHO - w[0] - w[1]);
  const presentes = ARCHIVOS.filter(([f]) => hay(path.join(COD, f)));
  out.push(new Table({
    columnWidths: w,
    width: { size: ANCHO, type: WidthType.DXA },
    borders: { top: SIN, bottom: SIN, left: SIN, right: SIN,
               insideHorizontal: SIN, insideVertical: SIN },
    rows: [
      new TableRow({ tableHeader: true, children: [
        celda('Archivo', w[0], { bold: true, bordeArriba: true, bordeAbajo: true }),
        celda('Líneas', w[1], { bold: true, bordeArriba: true, bordeAbajo: true, align: AlignmentType.CENTER }),
        celda('Qué hace', w[2], { bold: true, bordeArriba: true, bordeAbajo: true }),
      ] }),
      ...presentes.map(([f, d], i) => {
        const src = fs.readFileSync(path.join(COD, f), 'utf8');
        const ult = i === presentes.length - 1;
        return new TableRow({ children: [
          celda(f, w[0], { bordeAbajo: ult }),
          celda(String(src.split('\n').length), w[1], { align: AlignmentType.CENTER, bordeAbajo: ult }),
          celda(d, w[2], { bordeAbajo: ult }),
        ] });
      }),
    ],
  }));

  presentes.forEach(([f], k) => {
    const src = fs.readFileSync(path.join(COD, f), 'utf8');
    out.push(new Paragraph({
      pageBreakBefore: true,
      spacing: { before: 0, after: 120, line: 280, lineRule: LineRuleType.AUTO },
      children: [new TextRun({ text: `D.${k + 2}  ${f}`, bold: true, size: 24, font: SERIF })],
    }));
    src.split('\n').forEach(linea => {
      out.push(new Paragraph({
        spacing: { before: 0, after: 0, line: 200, lineRule: LineRuleType.AUTO },
        children: [new TextRun({ text: linea === '' ? ' ' : linea, size: 13, font: MONO })],
      }));
    });
  });
  return out;
}

// ------------------------------------------------------------- portada
const AUTORES = '[NOMBRE COMPLETO 1], [NOMBRE COMPLETO 2], [NOMBRE COMPLETO 3], [NOMBRE COMPLETO 4]';
const AFILIACION = 'Tecnológico de Monterrey, Escuela de Ciencias Sociales y Gobierno';
const CORREO = 'a01665438@tec.mx';

function portada() {
  const c = (texto, opts = {}) => new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: opts.after || 160, line: 300, lineRule: LineRuleType.AUTO },
    children: [new TextRun({ text: texto, size: opts.size || 24, font: SERIF,
                             bold: opts.bold, italics: opts.italics })],
  });
  const campo = (rotulo, texto) => new Paragraph({
    spacing: { before: 0, after: 100, line: 300, lineRule: LineRuleType.AUTO },
    children: [
      new TextRun({ text: `${rotulo}  `, bold: true, size: 23, font: SERIF }),
      new TextRun({ text: texto, size: 23, font: SERIF }),
    ],
  });
  return [
    new Paragraph({ spacing: { after: 400 }, children: [] }),
    c(titulo, { size: 32, bold: true, after: 400 }),
    c(AUTORES, { size: 24, after: 100 }),
    c(AFILIACION, { size: 22, italics: true, after: 100 }),
    c(`Autor de correspondencia: ${CORREO}`, { size: 22, after: 500 }),
    new Paragraph({
      spacing: { before: 0, after: 120, line: 300, lineRule: LineRuleType.AUTO },
      children: [new TextRun({ text: 'Resumen', bold: true, size: 24, font: SERIF })],
    }),
    new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { before: 0, after: 240, line: 300, lineRule: LineRuleType.AUTO },
      children: [new TextRun({ text: resumen, size: 23, font: SERIF })],
    }),
    campo('Palabras clave', claves),
    campo('Clasificación JEL', jel),
    campo('Extensión', `${palabras.toLocaleString('es-MX')} palabras en el cuerpo ` +
      '(secciones 1 a 7), sin contar portada, referencias, cuadros, pies de figura ni anexos.'),
    campo('Revista destino', 'Empirical Economics (Springer). Formateado según sus ' +
      'instrucciones para autores; véase el anexo A. Donde la revista no especifica ' +
      'aplica el formato del curso: Times New Roman 12, interlineado 1.5.'),
    campo('Nota sobre esta versión', 'Traducción al español de la versión sometida en ' +
      'inglés. El texto es el mismo; la versión en inglés es la que cumple el límite de ' +
      '9 000 palabras de la revista, porque el español corre alrededor de 14 por ciento ' +
      'más largo a contenido igual.'),
  ];
}

// ------------------------------------------------------------- referencias
function referencias() {
  const lineas = refs.split('\n').map(s => s.trim())
                     .filter(s => s && !/^##\s/.test(s));
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
      spacing: { before: 0, after: 200, line: 300, lineRule: LineRuleType.AUTO },
      children: [new TextRun({ text: 'Referencias', bold: true, size: 26, font: SERIF,
                               color: '000000' })],
    }),
    ...lineas.map(l => new Paragraph({
      spacing: { before: 0, after: 120, line: 300, lineRule: LineRuleType.AUTO },
      indent: { left: 480, hanging: 480 },
      children: runs(l, { size: 23, font: SERIF }),
    })),
  ];
}

// --------------------------------------------------------------- documento
const orden = ['A', 'B', 'C'].filter(k => apendices[k]).map(k => analizar(apendices[k]));
const cola = ['E', 'F'].filter(k => apendices[k]).map(k => analizar(apendices[k]));

const doc = new Document({
  creator: 'Equipo 4',
  title: titulo,
  description: 'Entregable 3 — artículo de investigación (versión en español)',
  styles: {
    default: {
      document: { run: { font: SERIF, size: 24 },
                  paragraph: { spacing: { line: 360, lineRule: LineRuleType.AUTO } } },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], size: 20, font: SERIF })],
        })],
      }),
    },
    children: [
      ...portada(),
      new Paragraph({ children: [new PageBreak()] }),
      ...analizar(cuerpo),
      ...analizar(declaraciones),
      ...referencias(),
      ...orden.flat(),
      ...anexoD(),
      ...cola.flat(),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  const salida = `${DOCX}/Entregable3_Equipo4_ESPANOL.docx`;
  fs.writeFileSync(salida, buf);
  console.log(`Escrito: ${salida}  (${(buf.length / 1e6).toFixed(2)} MB)`);
  console.log(`Palabras en el resumen: ${palabras_resumen}`);
  console.log(`Palabras en el cuerpo: ${palabras.toLocaleString('es-MX')}`);
  console.log(`Anexos incluidos: ${Object.keys(apendices).sort().join(', ')}  (D se genera aquí)`);
  console.log(`Cuadros con cuerpo numérico: ${TABLAS ? 'sí' : 'NO — pendientes de recomputar'}`);
  console.log(`Figuras incrustadas: ${FIGSIZE ? 'sí' : 'NO — pendientes de recomputar'}`);
});
