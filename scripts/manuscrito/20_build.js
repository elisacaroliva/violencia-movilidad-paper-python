/*
 * build.js — ensambla el Entregable 3 como .docx
 * ==============================================
 * Formato: las reglas de Empirical Economics prevalecen; donde la revista
 * no especifica, aplica el formato del curso (Times New Roman 12,
 * interlineado 1.5).
 *
 *   - encabezados decimales de dos niveles, con estilos integrados para que
 *     Word los reconozca como estructura
 *   - citas autor-año, referencias alfabetizadas con sangría francesa y DOI
 *   - tablas con la función de tabla de Word, reglas superior e inferior y
 *     una regla bajo el encabezado, sin cuadrícula interna
 *   - pies de tabla arriba, pies de figura abajo empezando con "Fig." en
 *     negritas y sin puntuación final
 *   - números de página en todas las páginas
 *   - sección de declaraciones antes de las referencias
 *
 * Uso:  node build.js
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ImageRun,
  PageBreak, Footer, PageNumber, TabStopType, LevelFormat, convertInchesToTwip,
} = require('docx');

// Rutas relativas a la raíz del repositorio (equivalente a here::here()):
// se busca hacia arriba el marcador `.here`, así que el script corre desde cualquier carpeta.
const RAIZ = (() => { let d = __dirname; while (!fs.existsSync(path.join(d, '.here'))) {
  const p = path.dirname(d); if (p === d) throw new Error('No encontré el marcador .here'); d = p; } return d; })();
const MAN = path.join(RAIZ, 'manuscrito', 'en');
const FIG = path.join(RAIZ, 'output', 'figuras', 'en');
const COD = path.join(RAIZ, 'scripts');
const DOCX = path.join(RAIZ, 'output', 'docx');
fs.mkdirSync(DOCX, { recursive: true });

const SERIF = 'Times New Roman';
const MONO = 'Courier New';
const ANCHO = 9360;               // 6.5 pulgadas en DXA
const PX = 624;                   // 6.5 pulgadas a 96 px/pulgada

const tablas = JSON.parse(fs.readFileSync(`${MAN}/tables.json`, 'utf8'));
const figsize = JSON.parse(fs.readFileSync(`${MAN}/figsize.json`, 'utf8'));

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

function p(texto, opts = {}) {
  const { size = 24, font = SERIF, ...rest } = opts;
  return new Paragraph({ children: runs(texto, { size, font }), ...rest });
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
      spacing: { before: 0, after: 0, line: 240 },
      children: [new TextRun({ text: texto, bold, size, font: SERIF })],
    })],
  });
}

/** Tabla del manuscrito, en estilo de reglas horizontales. */
function tabla(t) {
  const w = t.anchos.map(a => Math.round(ANCHO * a / 100));
  w[0] += ANCHO - w.reduce((a, b) => a + b, 0);     // cuadra el redondeo
  const paneles = new Set(t.paneles || []);

  const filas = [];
  // encabezado
  filas.push(new TableRow({
    tableHeader: true,
    children: t.cols.map((c, j) => celda(c, w[j], {
      bold: true, bordeAbajo: true, bordeArriba: true,
      align: j === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
    })),
  }));
  // cuerpo
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

function bloqueTabla(id) {
  const t = tablas[id];
  const out = [
    new Paragraph({
      spacing: { before: 240, after: 100, line: 240 },
      keepNext: true,
      children: [
        new TextRun({ text: `Table ${t.num}`, bold: true, size: 22, font: SERIF }),
        new TextRun({ text: `  ${t.titulo}`, size: 22, font: SERIF }),
      ],
    }),
    tabla(t),
  ];
  if (t.nota) {
    out.push(new Paragraph({
      spacing: { before: 100, after: 240, line: 240 },
      children: [
        new TextRun({ text: 'Notes: ', italics: true, size: 19, font: SERIF }),
        new TextRun({ text: t.nota, size: 19, font: SERIF }),
      ],
    }));
  }
  return out;
}

function bloqueFigura(nombre, pie) {
  const data = fs.readFileSync(`${FIG}/${nombre}.png`);
  const alto = Math.round(PX * figsize[nombre].ratio);
  const num = nombre.replace('Fig', '');
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 240, after: 100 },
      keepNext: true,
      children: [new ImageRun({ data, type: 'png',
                                transformation: { width: PX, height: alto } })],
    }),
    new Paragraph({
      spacing: { before: 0, after: 240, line: 240 },
      children: [
        new TextRun({ text: `Fig. ${num}`, bold: true, size: 20, font: SERIF }),
        new TextRun({ text: `  ${pie}`, size: 20, font: SERIF }),
      ],
    }),
  ];
}

/** Tabla escrita en markdown dentro de los anexos. */
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
  const hijos = [];
  const lineas = texto.split('\n');
  let i = 0;
  while (i < lineas.length) {
    const l = lineas[i];
    const t = l.trim();

    if (t === '' || t === '---') { i++; continue; }

    // tabla en markdown
    if (t.startsWith('|')) {
      const bloque = [];
      while (i < lineas.length && lineas[i].trim().startsWith('|')) {
        bloque.push(lineas[i]); i++;
      }
      hijos.push(tablaMarkdown(bloque));
      hijos.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
      continue;
    }

    // marcadores
    let m;
    if ((m = t.match(/^\[TABLE:(\w+)\|/))) { hijos.push(...bloqueTabla(m[1])); i++; continue; }
    if ((m = t.match(/^\[FIGURE:(\w+)\|(.*)\]$/))) {
      hijos.push(...bloqueFigura(m[1], m[2])); i++; continue;
    }
    if ((m = t.match(/^\[EQ\](.*)\[\/EQ\]$/))) {
      hijos.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 120, line: 240 },
        children: [new TextRun({ text: m[1], size: 23, font: SERIF, italics: true })],
      }));
      i++; continue;
    }

    // encabezados
    if (t.startsWith('### ')) {
      hijos.push(new Paragraph({
        heading: HeadingLevel.HEADING_2, keepNext: true,
        spacing: { before: 240, after: 120, line: 300 },
        children: [new TextRun({ text: t.slice(4), bold: true, size: 24, font: SERIF })],
      }));
      i++; continue;
    }
    if (t.startsWith('## ')) {
      hijos.push(new Paragraph({
        heading: HeadingLevel.HEADING_1, keepNext: true,
        spacing: { before: 320, after: 140, line: 300 },
        children: [new TextRun({ text: t.slice(3), bold: true, size: 26, font: SERIF })],
      }));
      i++; continue;
    }
    if (t.startsWith('# ')) {
      hijos.push(new Paragraph({
        heading: HeadingLevel.HEADING_1, pageBreakBefore: true, keepNext: true,
        spacing: { before: 0, after: 200, line: 300 },
        children: [new TextRun({ text: t.slice(2), bold: true, size: 28, font: SERIF })],
      }));
      i++; continue;
    }

    // listas numeradas de los anexos
    if ((m = t.match(/^(\d+)\.\s+(.*)$/))) {
      hijos.push(new Paragraph({
        spacing: { before: 60, after: 60, line: 360 },
        indent: { left: 400, hanging: 280 },
        children: runs(`${m[1]}.  ${m[2]}`, { size: 24, font: SERIF }),
      }));
      i++; continue;
    }

    // párrafo normal, justificado
    hijos.push(new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { before: 0, after: 120, line: 360 },
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

// anexos: se parten por "# Appendix" y se recolocan en el orden de la revista
const trozos = anx.split(/\n(?=# Appendix )/);
const declaraciones = trozos[0];
const apendices = {};
trozos.slice(1).forEach(s => { apendices[s.match(/^# Appendix (\w)/)[1]] = s; });

// --------------------------------------------------------- Anexo D: el código
const ARCHIVOS = [
  ['funciones/graficas_entregable1.py', 'Data loaders: state population, SESNSP crime panel, the violence index and the asset-index principal component.'],
  ['funciones/base.py', 'Shared construction of the analytical sample, the ranks, the dose and the triple-difference estimator.'],
  ['funciones/municipal.py', 'Within-state municipal design: municipal homicide rates, estimation and municipal event study.'],
  ['funciones/conglomerados_perm.py', 'Permutation inference within a subset of states.'],
  ['resultados/03_congelar.py', 'Master script. Produces every number in the manuscript and writes resultados.json.'],
  ['resultados/04_congelar2.py', 'Supplements: municipal event study with and without locality-size controls, municipal DBSCAN, quintile transitions.'],
  ['resultados/13_verificar.py', 'Re-checks figures inherited from earlier work and computes the clustering metrics against the k = 1 benchmark.'],
  ['figuras/14_figuras_articulo.py', 'The four figures, at the journal’s required width, resolution and lettering.'],
  ['manuscrito/17_tablas.py', 'Formats resultados.json into the six tables.'],
  ['resultados/11_transiciones.py', 'The quintile-transition route and the exchange rate between scales.'],
  ['resultados/12_pool_emovi.py', 'Harmonisation of the ESRU-EMOVI 2017 and 2023 rounds.'],
  ['manuscrito/20_build.js', 'Assembly of this document.'],
];

function anexoD() {
  const out = [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
      spacing: { after: 200, line: 300 },
      children: [new TextRun({ text: 'Appendix D. Reproducible code', bold: true, size: 28, font: SERIF })],
    }),
    ...analizar(
      'Every table and figure in this manuscript is produced by the code below from the three public sources named in the Data availability statement. ' +
      'The random seed is fixed at 20261102 and is set in each script that draws random numbers, so the permutation tests, the k-means initialisations and the subsample stability exercise all reproduce exactly. ' +
      'The pipeline runs in the order listed: the loaders and the shared construction module first, then the master script, then the supplements and the verification, then the figures and the tables, then this assembly script. ' +
      'Software: Python 3.13 with numpy, pandas, statsmodels, scipy, scikit-learn, pyreadstat, matplotlib and Pillow; Node.js with the docx package. ' +
      'Paths at the top of each script point to the raw source files and are the only lines that need changing to run the code elsewhere.'
    ),
  ];
  out.push(new Paragraph({
    spacing: { before: 200, after: 120, line: 300 },
    children: [new TextRun({ text: 'D.1 File inventory', bold: true, size: 24, font: SERIF })],
  }));
  const w = [Math.round(ANCHO * 0.26), Math.round(ANCHO * 0.10)];
  w.push(ANCHO - w[0] - w[1]);
  out.push(new Table({
    columnWidths: w,
    width: { size: ANCHO, type: WidthType.DXA },
    borders: { top: SIN, bottom: SIN, left: SIN, right: SIN,
               insideHorizontal: SIN, insideVertical: SIN },
    rows: [
      new TableRow({ tableHeader: true, children: [
        celda('File', w[0], { bold: true, bordeArriba: true, bordeAbajo: true }),
        celda('Lines', w[1], { bold: true, bordeArriba: true, bordeAbajo: true, align: AlignmentType.CENTER }),
        celda('What it does', w[2], { bold: true, bordeArriba: true, bordeAbajo: true }),
      ] }),
      ...ARCHIVOS.map(([f, d], i) => {
        const src = fs.readFileSync(path.join(COD, f), 'utf8');
        return new TableRow({ children: [
          celda(f, w[0], { bordeAbajo: i === ARCHIVOS.length - 1 }),
          celda(String(src.split('\n').length), w[1], { align: AlignmentType.CENTER, bordeAbajo: i === ARCHIVOS.length - 1 }),
          celda(d, w[2], { bordeAbajo: i === ARCHIVOS.length - 1 }),
        ] });
      }),
    ],
  }));

  ARCHIVOS.forEach(([f], k) => {
    const src = fs.readFileSync(path.join(COD, f), 'utf8');
    out.push(new Paragraph({
      pageBreakBefore: true,
      spacing: { before: 0, after: 120, line: 280 },
      children: [new TextRun({ text: `D.${k + 2}  ${f}`, bold: true, size: 24, font: SERIF })],
    }));
    src.split('\n').forEach(linea => {
      out.push(new Paragraph({
        spacing: { before: 0, after: 0, line: 200 },
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
    spacing: { before: 0, after: opts.after || 160, line: 300 },
    children: [new TextRun({ text: texto, size: opts.size || 24, font: SERIF,
                             bold: opts.bold, italics: opts.italics })],
  });
  return [
    new Paragraph({ spacing: { after: 400 }, children: [] }),
    c(titulo, { size: 32, bold: true, after: 400 }),
    c(AUTORES, { size: 24, after: 100 }),
    c(AFILIACION, { size: 22, italics: true, after: 100 }),
    c(`Corresponding author: ${CORREO}`, { size: 22, after: 500 }),
    new Paragraph({
      spacing: { before: 0, after: 120, line: 300 },
      children: [new TextRun({ text: 'Abstract', bold: true, size: 24, font: SERIF })],
    }),
    new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { before: 0, after: 240, line: 300 },
      children: [new TextRun({ text: resumen, size: 23, font: SERIF })],
    }),
    new Paragraph({
      spacing: { before: 0, after: 100, line: 300 },
      children: [
        new TextRun({ text: 'Keywords  ', bold: true, size: 23, font: SERIF }),
        new TextRun({ text: claves, size: 23, font: SERIF }),
      ],
    }),
    new Paragraph({
      spacing: { before: 0, after: 100, line: 300 },
      children: [
        new TextRun({ text: 'JEL classification  ', bold: true, size: 23, font: SERIF }),
        new TextRun({ text: jel, size: 23, font: SERIF }),
      ],
    }),
    new Paragraph({
      spacing: { before: 0, after: 100, line: 300 },
      children: [
        new TextRun({ text: 'Word count  ', bold: true, size: 23, font: SERIF }),
        new TextRun({ text: `${palabras.toLocaleString('en-US')} words in the body ` +
                           '(Sections 1 to 7), excluding the title page, references, ' +
                           'tables, figure captions and appendices.',
                      size: 23, font: SERIF }),
      ],
    }),
    new Paragraph({
      spacing: { before: 0, after: 100, line: 300 },
      children: [
        new TextRun({ text: 'Target journal  ', bold: true, size: 23, font: SERIF }),
        new TextRun({ text: 'Empirical Economics (Springer). Formatted to its author ' +
                           'guidelines; see Appendix A. Where the journal is silent the ' +
                           'course format applies: Times New Roman 12, line spacing 1.5.',
                      size: 23, font: SERIF }),
      ],
    }),
  ];
}

// ------------------------------------------------------------- referencias
function referencias() {
  const lineas = refs.split('\n').map(s => s.trim()).filter(s => s && s !== '## References');
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
      spacing: { before: 0, after: 200, line: 300 },
      children: [new TextRun({ text: 'References', bold: true, size: 26, font: SERIF })],
    }),
    ...lineas.map(l => new Paragraph({
      spacing: { before: 0, after: 120, line: 300 },
      indent: { left: 480, hanging: 480 },
      children: runs(l, { size: 23, font: SERIF }),
    })),
  ];
}

// --------------------------------------------------------------- documento
const doc = new Document({
  creator: 'Equipo 4',
  title: titulo,
  description: 'Entregable 3 — artículo de investigación',
  styles: {
    default: {
      document: { run: { font: SERIF, size: 24 },
                  paragraph: { spacing: { line: 360 } } },
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
      ...analizar(apendices.A),
      ...analizar(apendices.B),
      ...analizar(apendices.C),
      ...anexoD(),
      ...analizar(apendices.E),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  const salida = `${DOCX}/Entregable3_Equipo4.docx`;
  fs.writeFileSync(salida, buf);
  console.log(`Escrito: ${salida}  (${(buf.length / 1e6).toFixed(2)} MB)`);
  console.log(`Palabras en el resumen: ${palabras_resumen}`);
  console.log(`Palabras en el cuerpo: ${palabras.toLocaleString('en-US')}`);
});
