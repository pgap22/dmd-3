import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

// The presentation runtime is bundled with Codex. Keep the authoring workflow
// inside this package and use the first-party artifact tool only.
const SKILL_DIR = "C:\\Users\\Gerardo\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.1025.11240\\skills\\presentations";
const RUNTIME_NODE_MODULES = "C:\\Users\\Gerardo\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const RUNTIME_PYTHON = "C:\\Users\\Gerardo\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
process.env.RUNTIME_NODE_MODULES = process.env.RUNTIME_NODE_MODULES || RUNTIME_NODE_MODULES;

const workspaceDir = path.dirname(fileURLToPath(import.meta.url));
const taskWorkspaceDir = path.resolve(workspaceDir, "..");
const buildDir = path.join(workspaceDir, ".build-presentation");
const renderDir = path.join(workspaceDir, "renders");
const stagingDir = path.join(taskWorkspaceDir, ".codex-finalizer");
const finalPptx = path.join(workspaceDir, "Presentacion_Fase3_NYC311.pptx");
const finalPdf = path.join(workspaceDir, "Presentacion_Fase3_NYC311.pdf");
const candidatePath = path.join(stagingDir, "candidate.pptx");
const validationReceipt = path.join(stagingDir, "Presentacion_Fase3_NYC311.validation.json");

const { importRuntimeModule } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools", "runtime_helpers.mjs")).href);
const { finalizePresentation, makeNativeBulletParagraphs } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href,
);
const { Presentation, PresentationFile, FileBlob, registerPdfFontFace } = await importRuntimeModule("@oai/artifact-tool");

const FONT = "Arial";
const W = 1280;
const H = 720;
const FONT_ROOT = "C:\\Users\\Gerardo\\AppData\\Local\\Programs\\orca\\resources\\app.asar.unpacked\\out\\renderer\\standard_fonts";

const C = {
  bg: "#F7F8FB",
  white: "#FFFFFF",
  ink: "#111827",
  navy: "#14243D",
  blue: "#2463EB",
  blueSoft: "#DCE8FF",
  violet: "#6D4AFF",
  violetSoft: "#EEE9FF",
  gray: "#667085",
  gray2: "#98A2B3",
  line: "#D9DEE8",
  pale: "#EEF1F6",
  muted: "#CBD1DC",
  risk: "#B85C68",
};

const pos = (left, top, width, height) => ({ left, top, width, height });

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function registerPresentationFonts() {
  const faces = [
    { style: "normal", weight: 400, file: "LiberationSans-Regular.ttf" },
    { style: "normal", weight: 700, file: "LiberationSans-Bold.ttf" },
    { style: "italic", weight: 400, file: "LiberationSans-Italic.ttf" },
    { style: "italic", weight: 700, file: "LiberationSans-BoldItalic.ttf" },
  ];
  for (const face of faces) {
    registerPdfFontFace({
      family: FONT,
      style: face.style,
      weight: face.weight,
      source: await readBytes(path.join(FONT_ROOT, face.file)),
    });
  }
}

function addText(slide, text, position, style = {}, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: options.name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: style.fontSize ?? 20,
    color: style.color ?? C.ink,
    bold: style.bold ?? false,
    italic: style.italic ?? false,
    alignment: style.alignment ?? "left",
    verticalAlignment: style.verticalAlignment ?? "top",
    autoFit: style.autoFit ?? "none",
    wrap: "square",
    lineSpacing: style.lineSpacing ?? 1.05,
    insets: style.insets ?? 0,
  };
  return shape;
}

function addSurface(slide, position, options = {}) {
  return slide.shapes.add({
    geometry: options.geometry ?? "roundRect",
    name: options.name,
    position,
    fill: options.fill ?? C.white,
    line: options.line ?? { style: "solid", fill: C.line, width: 1 },
    borderRadius: options.borderRadius ?? "rounded-xl",
  });
}

function addRule(slide, left, top, width, color = C.line, thickness = 1) {
  return slide.shapes.add({
    geometry: "line",
    position: pos(left, top, width, 0),
    fill: "none",
    line: { style: "solid", fill: color, width: thickness },
  });
}

function addHeader(slide, number, title, subtitle, section = "NYC311 / FASE 3") {
  addText(slide, section, pos(64, 30, 280, 20), { fontSize: 13, color: C.blue, bold: true });
  addText(slide, `${String(number).padStart(2, "0")} / 13`, pos(1128, 30, 88, 20), {
    fontSize: 13,
    color: C.gray2,
    bold: true,
    alignment: "right",
  });
  addText(slide, title, pos(64, 66, 1040, 64), {
    fontSize: 38,
    color: C.navy,
    bold: true,
    lineSpacing: 0.95,
    autoFit: "shrinkText",
  });
  if (subtitle) {
    addText(slide, subtitle, pos(64, 136, 1040, 38), {
      fontSize: 18,
      color: C.gray,
      lineSpacing: 1,
      autoFit: "shrinkText",
    });
  }
  addRule(slide, 64, 184, 1152, C.line, 1);
}

function addFooter(slide, text) {
  addText(slide, text, pos(64, 684, 1152, 20), {
    fontSize: 12,
    color: C.gray2,
    autoFit: "shrinkText",
  });
}

function addNativeBullets(slide, items, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = makeNativeBulletParagraphs(items, {
    marginLeftPoints: style.marginLeftPoints ?? 18,
    hangingPoints: style.hangingPoints ?? 9,
    spaceAfterPoints: style.spaceAfterPoints ?? 8,
  });
  shape.text.style = {
    typeface: FONT,
    fontSize: style.fontSize ?? 21,
    color: style.color ?? C.ink,
    lineSpacing: style.lineSpacing ?? 1.08,
    autoFit: style.autoFit ?? "shrinkText",
    verticalAlignment: "top",
    insets: 0,
  };
  return shape;
}

function addNote(slide, source, extra = "") {
  slide.speakerNotes.text = `Fuente interna: ${source}${extra ? `\n${extra}` : ""}`;
  slide.speakerNotes.setVisible(true);
}

function addChart(slide, type, config) {
  const chartTextStyle = (style = {}) => ({ typeface: FONT, ...style });
  const axisStyle = (axis) => axis ? { ...axis, textStyle: chartTextStyle(axis.textStyle) } : axis;
  const dataLabelStyle = config.dataLabels
    ? { ...config.dataLabels, textStyle: chartTextStyle(config.dataLabels.textStyle) }
    : config.dataLabels;
  const chart = slide.charts.add(type, {
    ...config,
    titleTextStyle: chartTextStyle(config.titleTextStyle),
    xAxis: axisStyle(config.xAxis),
    yAxis: axisStyle(config.yAxis),
    secondaryXAxis: axisStyle(config.secondaryXAxis),
    secondaryYAxis: axisStyle(config.secondaryYAxis),
    dataLabels: dataLabelStyle,
    chartFill: config.chartFill ?? C.white,
    plotAreaFill: config.plotAreaFill ?? C.white,
    chartLine: config.chartLine ?? { style: "solid", fill: C.line, width: 1 },
  });
  return chart;
}

async function addImage(slide, filePath, position, alt) {
  return slide.images.add({
    blob: await readBytes(filePath),
    contentType: "image/png",
    alt,
    fit: "contain",
    position,
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
}

function setupSlide(slide) {
  slide.background.fill = C.bg;
}

function addFlowNode(slide, x, title, body, accent = C.blue) {
  const box = addSurface(slide, pos(x, 230, 248, 190), {
    fill: C.white,
    line: { style: "solid", fill: C.line, width: 1 },
  });
  addRule(slide, x + 20, 262, 208, accent, 4);
  addText(slide, title, pos(x + 20, 282, 208, 40), {
    fontSize: 21,
    color: C.navy,
    bold: true,
    autoFit: "shrinkText",
  });
  addText(slide, body, pos(x + 20, 330, 208, 72), {
    fontSize: 16,
    color: C.gray,
    autoFit: "shrinkText",
    lineSpacing: 1.08,
  });
  return box;
}

function connectFlow(slide, from, to, color = C.gray2) {
  slide.shapes.connect(from, to, {
    kind: "straight",
    fromSide: "right",
    toSide: "left",
    line: { style: "solid", fill: color, width: 2 },
    tail: { type: "triangle", width: "sm", length: "sm" },
  });
}

function addMetric(slide, value, label, x, y, width, color = C.navy) {
  addText(slide, value, pos(x, y, width, 58), {
    fontSize: 46,
    color,
    bold: true,
    autoFit: "shrinkText",
  });
  addText(slide, label, pos(x, y + 58, width, 34), {
    fontSize: 16,
    color: C.gray,
    autoFit: "shrinkText",
  });
}

function addStep(slide, number, title, body, x, y, width = 400, accent = C.blue) {
  addText(slide, number, pos(x, y, 42, 42), { fontSize: 28, color: accent, bold: true });
  addText(slide, title, pos(x + 52, y, width - 52, 30), { fontSize: 21, color: C.navy, bold: true });
  addText(slide, body, pos(x + 52, y + 32, width - 52, 44), { fontSize: 16, color: C.gray, autoFit: "shrinkText" });
}

function buildCover(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.bg;
  addText(slide, "DMD104 / UNIVERSIDAD DON BOSCO", pos(72, 58, 520, 22), { fontSize: 15, color: C.blue, bold: true });
  addText(slide, "NYC311\nFase 3", pos(72, 130, 650, 170), {
    fontSize: 70,
    color: C.navy,
    bold: true,
    lineSpacing: 0.88,
  });
  addText(slide, "Del dato abierto a la decisión operativa", pos(76, 326, 620, 48), { fontSize: 25, color: C.ink, bold: true });
  addText(slide, "Data Warehouse · Minería · Power BI", pos(76, 382, 580, 30), { fontSize: 20, color: C.gray });
  addRule(slide, 76, 456, 550, C.violet, 4);
  addText(slide, "Defensa · 26 octubre 2026", pos(76, 478, 350, 24), { fontSize: 17, color: C.gray });
  addText(slide, "Lemus Mejía · Bonilla Saz · Chávez Castillo\nLópez Ortiz · Galdámez Soto", pos(76, 526, 520, 54), { fontSize: 16, color: C.gray, lineSpacing: 1.12 });
  const panel = addSurface(slide, pos(930, 52, 270, 610), { fill: C.navy, line: { style: "solid", fill: C.navy, width: 0 }, borderRadius: "rounded-2xl" });
  addText(slide, "NYC\n311", pos(970, 124, 190, 160), { fontSize: 76, color: C.white, bold: true, lineSpacing: 0.82 });
  addRule(slide, 970, 318, 152, C.violet, 5);
  addText(slide, "1,312,465\nsolicitudes", pos(970, 360, 170, 82), { fontSize: 25, color: C.white, bold: true, lineSpacing: 0.95 });
  addText(slide, "BI: enero y abril–julio 2026", pos(970, 462, 210, 24), { fontSize: 14, color: C.blueSoft, autoFit: "shrinkText" });
  addText(slide, "F1  →  F2  →  F3", pos(970, 564, 190, 24), { fontSize: 16, color: C.white, bold: true });
  addNote(slide, "Fuentes de Fase 2 y validación del modelo BI (comprobación: 26 de octubre de 2026).", "Portada académica. La cifra grande corresponde al universo validado en SQL Server y Power BI.");
}

function buildProblem(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 2, "La demora está concentrada y el dato faltante debe quedar visible", "BI actual: enero y abril–julio 2026. El snapshot F2 abril–julio se conserva como referencia histórica.");
  addMetric(slide, "1,312,465", "solicitudes en el BI actual", 72, 240, 400);
  addMetric(slide, "63,467", "sin duración observada", 72, 372, 400, C.risk);
  addText(slide, "El BI actual conserva NULL cuando no existe fecha de cierre. Esos casos quedan fuera de la etiqueta de demora alta.", pos(72, 518, 420, 68), { fontSize: 18, color: C.gray, autoFit: "shrinkText", lineSpacing: 1.1 });
  addChart(slide, "bar", {
    position: pos(590, 230, 600, 350),
    title: "Minutos de resolución",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Mediana observada", "P75 histórico"],
    series: [{ name: "Minutos", values: [330, 4329], fill: C.blue }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 58 },
    hasLegend: false,
    xAxis: { numberFormatCode: "#,##0", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 16 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 15, bold: true }, numberFormatCode: "#,##0" },
  });
  addText(slide, "P75 = 4,329 min\nUmbral histórico, no SLA", pos(590, 604, 600, 48), { fontSize: 17, color: C.gray, bold: true, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: Fase 2 README y validación BI. La mediana se calcula solo con duración observada.");
  addNote(slide, "Informe de Fase 2 y validación del modelo BI.", "La duración NULL no es demora normal. El P75 es la regla histórica usada para demora_alta y no representa un compromiso de servicio.");
}

function buildEvidence(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 3, "La cuadratura se conserva del DW al tablero", "El modelo BI mantiene el grano de una fila por solicitud y el LEFT JOIN no multiplica registros.");
  addText(slide, "1,312,465", pos(72, 232, 350, 70), { fontSize: 56, color: C.navy, bold: true });
  addText(slide, "DW · minería · vista BI", pos(74, 302, 350, 28), { fontSize: 18, color: C.gray });
  addRule(slide, 72, 354, 410, C.blue, 3);
  addText(slide, "1 fila = 1 solicitud\nCero multiplicación en la integración", pos(72, 380, 380, 72), { fontSize: 22, color: C.ink, bold: true, lineSpacing: 1.05 });
  addText(slide, "La población con duración observada y la población sin duración suman exactamente el universo.", pos(72, 492, 385, 58), { fontSize: 17, color: C.gray, autoFit: "shrinkText" });
  addChart(slide, "bar", {
    position: pos(560, 232, 635, 300),
    title: "Cobertura de duración observada",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Con duración", "Sin duración"],
    series: [{ name: "Solicitudes", values: [1248998, 63467], fill: C.blue }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 60 },
    hasLegend: false,
    xAxis: { numberFormatCode: "#,##0", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 16 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 15, bold: true }, numberFormatCode: "#,##0" },
  });
  addText(slide, "313,360 demoras altas\n25.09% entre los 1,248,998 casos con tiempo", pos(560, 566, 635, 64), { fontSize: 20, color: C.violet, bold: true, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: validación del modelo BI y medidas DAX ejecutadas en VertiPaq.");
  addNote(slide, "Validación del modelo BI, sección de medidas DAX.", "La tasa de demora alta usa como denominador las 1,230,737 solicitudes con duración observada.");
}

function buildArchitecture(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 4, "Arquitectura F1: una cadena de datos con grano explícito", "La Fase 1 prepara el hecho dimensional que F2 y F3 consumen sin cambiar la unidad de análisis.");
  const n1 = addFlowNode(slide, 64, "Fuente", "NYC Open Data\nSolicitudes 311", C.blue);
  const n2 = addFlowNode(slide, 346, "ETL", "raw → stg\nlimpieza y llaves", C.violet);
  const n3 = addFlowNode(slide, 628, "DW", "dw.FactSolicitud\n1 fila por solicitud", C.blue);
  const n4 = addFlowNode(slide, 910, "Dimensiones", "Fecha · agencia\nproblema · geografía\nestado · canal", C.violet);
  connectFlow(slide, n1, n2);
  connectFlow(slide, n2, n3);
  connectFlow(slide, n3, n4);
  addRule(slide, 64, 500, 1094, C.navy, 2);
  addText(slide, "Medida central", pos(64, 528, 180, 24), { fontSize: 15, color: C.blue, bold: true });
  addText(slide, "minutos_resolucion", pos(64, 554, 260, 34), { fontSize: 23, color: C.navy, bold: true });
  addText(slide, "NULL cuando no existe fecha de cierre", pos(64, 594, 330, 24), { fontSize: 16, color: C.gray });
  addText(slide, "F2 y F3", pos(470, 528, 180, 24), { fontSize: 15, color: C.blue, bold: true });
  addText(slide, "mining.vw_dataset_fase2\nbi.vw_solicitudes_segmentadas", pos(470, 554, 370, 60), { fontSize: 21, color: C.navy, bold: true, lineSpacing: 1.04 });
  addText(slide, "Unión nulo-segura por agencia + complaint_type + borough", pos(900, 548, 288, 48), { fontSize: 16, color: C.gray, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: Fase 1 DDL/SSIS y docs/02-INTEGRACION-DATOS.md. La conexión BI validada usa SQL Server DW_NYC311 en modo Import.");
  addNote(slide, "DDL y paquete SSIS de Fase 1; guía de integración y ficha del modelo BI.", "El diagrama conserva únicamente objetos y relaciones documentados. La ejecución histórica del SSIS se presenta como evidencia de Fase 1, no como una ejecución repetida en esta sesión.");
}

function buildMining(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 5, "Minería F2: el P75 convierte la demora en una etiqueta histórica", "El árbol se entrenó sobre variables disponibles antes del cierre y se evaluó en un conjunto de prueba.");
  addText(slide, "4,329", pos(72, 236, 320, 74), { fontSize: 64, color: C.violet, bold: true });
  addText(slide, "minutos", pos(76, 310, 250, 30), { fontSize: 22, color: C.navy, bold: true });
  addRule(slide, 76, 366, 350, C.violet, 4);
  addText(slide, "demora_alta = 1\nsi la duración observada supera el P75", pos(76, 396, 360, 74), { fontSize: 23, color: C.ink, bold: true, lineSpacing: 1.05 });
  addText(slide, "Sin cierre: demora_alta = NULL", pos(76, 506, 360, 30), { fontSize: 18, color: C.risk, bold: true });
  addChart(slide, "bar", {
    position: pos(520, 232, 675, 330),
    title: "Métricas del árbol en prueba",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Recall", "F1", "ROC-AUC"],
    series: [{ name: "Valor", values: [0.9515, 0.7837, 0.952], fill: C.blue }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 52 },
    hasLegend: false,
    xAxis: { min: 0, max: 1, majorUnit: 0.25, numberFormatCode: "0%", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 16 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 15, bold: true }, numberFormatCode: "0%" },
  });
  addText(slide, "Métricas de test. No representan un score de producción ni prueban causalidad.", pos(520, 590, 675, 38), { fontSize: 17, color: C.gray, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: informe de Fase 2 y guía de defensa.");
  addNote(slide, "Informe de Fase 2, guía de defensa y ficha de hechos comprobados.", "El P75 se calculó sobre las duraciones observadas de abril–julio 2026. La etiqueta no se asigna a solicitudes sin duración.");
}

function buildKmeans(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 6, "K-Means segmentó perfiles operativos, no tickets individuales", "La terna agencia + tipo de reclamo + borough define el perfil. El universo no elegible queda visible.");
  const stages = [
    ["912", "perfiles iniciales F2"],
    ["487", "con volumen ≥ 100"],
    ["480", "modelados · K = 3"],
  ];
  stages.forEach(([value, label], index) => {
    const x = 72 + index * 178;
    addText(slide, value, pos(x, 220, 150, 54), { fontSize: 44, color: index === 2 ? C.violet : C.navy, bold: true, alignment: "center" });
    addText(slide, label, pos(x, 276, 150, 35), { fontSize: 15, color: C.gray, alignment: "center", autoFit: "shrinkText" });
    if (index < stages.length - 1) {
      slide.shapes.add({ geometry: "rightArrow", position: pos(x + 152, 238, 28, 22), fill: C.line, line: { style: "solid", fill: C.line, width: 0 } });
    }
  });
  addText(slide, "BI actual: 481 perfiles", pos(430, 314, 180, 24), { fontSize: 15, color: C.violet, bold: true, alignment: "center", autoFit: "shrinkText" });
  addText(slide, "Silhouette = 0.421", pos(650, 232, 250, 38), { fontSize: 28, color: C.violet, bold: true });
  addText(slide, "separación útil, todavía moderada", pos(650, 274, 330, 28), { fontSize: 17, color: C.gray });
  addChart(slide, "bar", {
    position: pos(72, 350, 1128, 272),
    title: "Solicitudes por perfil y fuera de perfil",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Rápida / baja demora", "Prolongada / alta demora", "Rezago crítico", "Sin perfil K-Means"],
    series: [{
      name: "Solicitudes",
      values: [910529, 358005, 29621, 14310],
      fill: C.blue,
      points: [{ idx: 1, fill: C.violet }, { idx: 2, fill: "#9B8AF2" }, { idx: 3, fill: C.gray2 }],
    }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 38 },
    hasLegend: false,
    xAxis: { numberFormatCode: "#,##0", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 15 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 14, bold: true }, numberFormatCode: "#,##0" },
  });
  addText(slide, "1,298,155 segmentadas + 14,310 sin perfil = 1,312,465 solicitudes", pos(72, 642, 1128, 25), { fontSize: 17, color: C.ink, bold: true });
  addFooter(slide, "Fuente: validación del modelo BI. La cobertura actual es 98.91%; F2 original documentó 480 perfiles.");
  addNote(slide, "Informe de Fase 2, ficha de hechos comprobados y validación del modelo BI.", "Los valores de volumen corresponden a la vista BI validada. Sin perfil K-Means no es un cuarto clúster y se conserva como categoría de auditoría.");
}

function buildTreeLimits(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 7, "El árbol prioriza revisión, pero sus límites siguen visibles", "La métrica clave es Recall en prueba. La clasificación histórica no equivale a predicción productiva.");
  addText(slide, "95.15%", pos(72, 226, 300, 72), { fontSize: 62, color: C.violet, bold: true });
  addText(slide, "Recall en prueba", pos(76, 298, 280, 30), { fontSize: 20, color: C.navy, bold: true });
  addText(slide, "Predictores válidos", pos(76, 372, 280, 26), { fontSize: 16, color: C.blue, bold: true });
  addText(slide, "agency · complaint_type · borough\ncanal · mes · día de semana", pos(76, 402, 360, 54), { fontSize: 19, color: C.ink, bold: true, lineSpacing: 1.05 });
  addText(slide, "Excluidos para evitar fuga: duración, estado, ID y coordenadas", pos(76, 496, 360, 50), { fontSize: 17, color: C.gray, autoFit: "shrinkText" });
  addChart(slide, "bar", {
    position: pos(510, 230, 690, 250),
    title: "Demoras verdaderas en el conjunto de prueba",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Detectadas", "No detectadas"],
    series: [{ name: "Casos", values: [58549, 2982], fill: C.blue, points: [{ idx: 1, fill: C.risk }] }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 60 },
    hasLegend: false,
    xAxis: { numberFormatCode: "#,##0", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 16 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 15, bold: true }, numberFormatCode: "#,##0" },
  });
  addSurface(slide, pos(510, 526, 690, 104), { fill: C.violetSoft, line: { style: "solid", fill: C.violetSoft, width: 0 } });
  addText(slide, "Límites", pos(536, 546, 100, 25), { fontSize: 16, color: C.violet, bold: true });
  addText(slide, "Sin validación temporal · sin prueba causal · sin score por solicitud en producción", pos(536, 576, 620, 30), { fontSize: 18, color: C.navy, bold: true, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: informe de Fase 2. Recall, F1 y AUC son métricas del conjunto de prueba.");
  addNote(slide, "Informe de Fase 2, guía de defensa y especificación del dashboard.", "La cifra de 2,982 corresponde a falsos negativos reportados en prueba. No se presenta como una cantidad operativa actual.");
}

async function buildPanorama(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 8, "Panorama Power BI: una lectura del universo completo", "La página 1 combina volumen, mediana observada, demora alta y solicitudes sin duración.");
  addMetric(slide, "1,312,465", "solicitudes distintas", 72, 238, 360);
  addMetric(slide, "330 min", "mediana observada", 72, 360, 360, C.violet);
  addText(slide, "La primera lectura debe responder tres preguntas: cuánto entra, cuánto tarda y qué parte no puede clasificarse por falta de duración.", pos(72, 506, 350, 96), { fontSize: 18, color: C.gray, autoFit: "shrinkText", lineSpacing: 1.08 });
  addChart(slide, "bar", {
    position: pos(492, 214, 730, 300),
    title: "Cobertura temporal de las solicitudes",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Con duración observada", "Sin duración observada"],
    series: [{ name: "Solicitudes", values: [1248998, 63467], fill: C.blue, points: [{ idx: 1, fill: C.risk }] }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 55 },
    hasLegend: false,
    xAxis: { numberFormatCode: "#,##0", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 16 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 15, bold: true }, numberFormatCode: "#,##0" },
  });
  addSurface(slide, pos(492, 548, 730, 112), { fill: C.blueSoft, line: { style: "solid", fill: C.blueSoft, width: 0 } });
  addText(slide, "Lectura de gestión", pos(520, 568, 220, 24), { fontSize: 16, color: C.blue, bold: true });
  addText(slide, "La demora alta se calcula solo sobre cierres observados; los 63,467 casos sin duración permanecen como sin clasificar.", pos(520, 598, 650, 36), { fontSize: 18, color: C.navy, bold: true, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: PBIX final y validación del modelo. Las cifras se presentan como conteos del universo, no como captura de pantalla.");
  addNote(slide, "La diapositiva resume las medidas del PBIX final: solicitudes distintas, mediana observada y cobertura de duración.", "Las cifras distinguen casos observados de casos sin duración; no se imputan demoras.");
}

async function buildDiagnostics(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 9, "Diagnóstico operativo: dónde concentrar capacidad", "La página 2 cruza mediana observada, borough, canal y estado sin convertir NULL en demora normal.");
  addMetric(slide, "330 min", "mediana global observada", 72, 238, 300, C.navy);
  addMetric(slide, "4,329 min", "P75 histórico; no es SLA", 390, 238, 300, C.violet);
  addMetric(slide, "63,467", "sin duración observada", 708, 238, 300, C.risk);
  addSurface(slide, pos(72, 400, 1130, 242), { fill: C.white, line: { style: "solid", fill: C.line, width: 1 } });
  addText(slide, "Ejemplo de drilldown interactivo", pos(100, 428, 400, 26), { fontSize: 18, color: C.blue, bold: true });
  addText(slide, "Borough / agencia / canal", pos(100, 474, 360, 40), { fontSize: 26, color: C.navy, bold: true, autoFit: "shrinkText" });
  addText(slide, "Aplicar un filtro y leer el volumen y la mediana observada resultantes", pos(100, 520, 480, 48), { fontSize: 19, color: C.ink, bold: true, autoFit: "shrinkText" });
  addSurface(slide, pos(630, 438, 2, 174), { fill: C.line, line: { style: "solid", fill: C.line, width: 0 } });
  addText(slide, "Preguntas que responde el tablero", pos(672, 428, 420, 26), { fontSize: 18, color: C.blue, bold: true });
  addText(slide, "¿Qué borough, agencia o canal concentra volumen?\n¿Dónde sube la mediana observada?\n¿Qué casos requieren revisión por falta de duración?", pos(672, 474, 480, 110), { fontSize: 18, color: C.navy, bold: true, lineSpacing: 1.18 });
  addFooter(slide, "Fuente: PBIX final y validación del modelo. El drilldown de Bronx es un ejemplo de lectura, no una conclusión causal.");
  addNote(slide, "La diapositiva usa medidas y el filtro de Bronx validados contra el modelo tabular del PBIX final.", "La mediana solo describe cierres observados; el tablero sirve para orientar capacidad y priorizar revisión, no para atribuir causas.");
}

function buildSegmentation(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 10, "Segmentación: cobertura alta, universo completo", "Los tres perfiles sirven para orientar investigación y capacidad. El cuarto renglón solo identifica casos fuera de perfil.");
  addMetric(slide, "481", "perfiles modelados en BI", 72, 224, 280, C.violet);
  addMetric(slide, "98.91%", "cobertura de solicitudes", 340, 224, 320, C.navy);
  addChart(slide, "bar", {
    position: pos(72, 350, 770, 284),
    title: "Volumen por perfil operativo",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, fill: C.navy, bold: true },
    categories: ["Rápida / baja demora", "Prolongada / alta demora", "Rezago crítico", "Sin perfil K-Means"],
    series: [{ name: "Solicitudes", values: [910529, 358005, 29621, 14310], fill: C.blue, points: [{ idx: 1, fill: C.violet }, { idx: 2, fill: "#9B8AF2" }, { idx: 3, fill: C.gray2 }] }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 38 },
    hasLegend: false,
    xAxis: { numberFormatCode: "#,##0", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.pale, width: 1 }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { fill: C.navy, fontSize: 15 }, line: { style: "solid", fill: C.line, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.navy, fontSize: 14, bold: true }, numberFormatCode: "#,##0" },
  });
  addSurface(slide, pos(900, 350, 292, 284), { fill: C.navy, line: { style: "solid", fill: C.navy, width: 0 } });
  addText(slide, "Cuadratura", pos(928, 380, 220, 28), { fontSize: 17, color: C.blueSoft, bold: true });
  addText(slide, "1,298,155\nsegmentadas", pos(928, 428, 220, 66), { fontSize: 30, color: C.white, bold: true, lineSpacing: 0.9 });
  addRule(slide, 928, 522, 210, C.violet, 4);
  addText(slide, "+ 14,310\nsin perfil", pos(928, 548, 220, 58), { fontSize: 24, color: C.white, bold: true, lineSpacing: 0.92 });
  addFooter(slide, "Fuente: modelo de perfiles K-Means y validación BI. `Sin perfil K-Means` preserva el 100% del universo.");
  addNote(slide, "Informe de Fase 2, guía de integración y validación del modelo BI.", "La segmentación no asigna un clúster a cada ticket por inferencia individual. La vista BI expone los casos fuera de perfil para auditoría.");
}

function buildValueCosts(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 11, "Valor y costo: escenario, no ROI observado", "Horizonte de 3 años. La sensibilidad cambia las horas de análisis evitadas, no las métricas de minería.");
  addText(slide, "CAPEX", pos(72, 214, 150, 22), { fontSize: 15, color: C.blue, bold: true });
  addText(slide, "4,520 USD", pos(72, 238, 230, 42), { fontSize: 30, color: C.navy, bold: true });
  addText(slide, "OPEX anual", pos(360, 214, 180, 22), { fontSize: 15, color: C.blue, bold: true });
  addText(slide, "4,200 USD", pos(360, 238, 230, 42), { fontSize: 30, color: C.navy, bold: true });
  addText(slide, "TCO 3 años", pos(648, 214, 180, 22), { fontSize: 15, color: C.blue, bold: true });
  addText(slide, "17,120 USD", pos(648, 238, 240, 42), { fontSize: 30, color: C.violet, bold: true });
  addText(slide, "Supuesto de tarifa: 18 USD/hora", pos(936, 232, 260, 30), { fontSize: 17, color: C.gray, autoFit: "shrinkText" });
  const table = slide.tables.add({
    rows: 4,
    columns: 5,
    left: 72,
    top: 332,
    width: 1128,
    height: 250,
    columnWidths: [270, 180, 230, 210, 238],
    values: [
      ["Escenario", "Ahorro h/sem", "Beneficio/año", "ROI 3 años", "Punto de equilibrio"],
      ["Conservador", "8", "7,488 USD", "31.2%", "Mes 28"],
      ["Base", "16", "14,976 USD", "162.4%", "Mes 14"],
      ["Optimista", "24", "22,464 USD", "293.6%", "Mes 10"],
    ],
  });
  table.styleOptions = { headerRow: true, bandedRows: true };
  table.borders.assign({ style: "solid", fill: C.line, width: 1 });
  for (let row = 0; row < 4; row += 1) {
    for (let col = 0; col < 5; col += 1) {
      const cell = table.getCell(row, col);
      cell.text.style = {
        typeface: FONT,
        fontSize: row === 0 ? 16 : 18,
        color: row === 0 ? C.white : C.ink,
        bold: row === 0 || (row === 2 && (col === 0 || col === 3)),
        verticalAlignment: "middle",
        autoFit: "shrinkText",
      };
      cell.fill = row === 0 ? C.navy : (row === 2 ? C.violetSoft : C.white);
    }
  }
  addText(slide, "El informe modela ahorro de horas. No monetiza Recall, falsos negativos ni una adopción que todavía no existe.", pos(72, 618, 1128, 34), { fontSize: 17, color: C.gray, autoFit: "shrinkText" });
  addFooter(slide, "Fuente: Documento Fase 3, sección de viabilidad. Marco de referencia: Horngren et al. (2012), Ross et al. (2019) y Storment & Fuller (2020).");
  addNote(slide, "Documento Fase 3, sección de costos y viabilidad; guía de costos y ficha del modelo BI.", "El CAPEX, OPEX, TCO y ROI son supuestos de escenario para defender viabilidad. No representan un retorno observado por NYC311.");
}

function buildConclusion(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 12, "Cierre y demo: de la evidencia a una acción concreta", "La defensa termina mostrando una interacción real y nombrando lo que el modelo todavía no puede afirmar.");
  addText(slide, "Tres decisiones defendibles", pos(72, 228, 420, 32), { fontSize: 23, color: C.navy, bold: true });
  addNativeBullets(slide, [
    "Conservar NULL y separar calidad de dato de demora alta.",
    "Usar K-Means para orientar capacidad por perfil, no para etiquetar causalidad.",
    "Usar el árbol como filtro de revisión humana, no como decisión automática.",
  ], pos(72, 278, 490, 170), { fontSize: 20, spaceAfterPoints: 11 });
  addSurface(slide, pos(72, 498, 490, 128), { fill: C.violetSoft, line: { style: "solid", fill: C.violetSoft, width: 0 } });
  addText(slide, "Lo que sí sabemos", pos(96, 520, 180, 24), { fontSize: 16, color: C.violet, bold: true });
  addText(slide, "El tablero permite comparar volumen y demora con el mismo filtro.", pos(96, 552, 420, 42), { fontSize: 20, color: C.navy, bold: true, autoFit: "shrinkText" });
  addText(slide, "Demo en 3 pasos", pos(670, 228, 330, 32), { fontSize: 23, color: C.navy, bold: true });
  addStep(slide, "01", "Filtrar un borough", "Leer volumen y mediana observada con el filtro aplicado", 670, 282, 470, C.blue);
  addRule(slide, 691, 370, 420, C.line, 2);
  addStep(slide, "02", "Aislar sin perfil", "14,310 solicitudes · la cuadratura se conserva", 670, 396, 470, C.violet);
  addRule(slide, 691, 484, 420, C.line, 2);
  addStep(slide, "03", "Volver al universo", "1,312,465 solicitudes · P75 histórico 4,329 min", 670, 510, 470, C.blue);
  addFooter(slide, "Fuentes: validación del modelo BI y guion de defensa. Marco ético: Ley de Protección de Datos Personales (2024).");
  addNote(slide, "Validación del modelo BI, guion de defensa y guía de defensa.", "Las tres interacciones de demo están documentadas como consultas DAX parametrizadas. La revisión humana final debe abrir el PBIX en Power BI Desktop.");
}

function buildReferences(presentation) {
  const slide = presentation.slides.add();
  setupSlide(slide);
  addHeader(slide, 13, "Marco teórico y referencias académicas", "Sustentación metodológica, normativa y bibliográfica de las Fases 1, 2 y 3 (documentos de referencia).");

  // Box 1: Data Warehouse & Kimball (Top Left)
  addSurface(slide, pos(64, 204, 556, 214), { fill: C.white, line: { style: "solid", fill: C.line, width: 1 } });
  addText(slide, "Data Warehouse y Modelado Dimensional", pos(88, 218, 508, 26), { fontSize: 17, color: C.navy, bold: true });
  addText(slide, "· Kimball, R., et al. (1998). The Data Warehouse Lifecycle Toolkit. Metodología de 10 etapas; hecho atómico dw.FactSolicitud y dimensiones conformadas.\n· Microsoft Learn (2026). SQL Server Integration Services (SSIS). Flujos ETL y staging.\n· NYC Open Data (2026). 311 Service Requests (erm2-nwe9). Fuente primaria de datos abiertos.", pos(88, 250, 508, 154), { fontSize: 14.5, color: C.gray, lineSpacing: 1.15, autoFit: "shrinkText" });

  // Box 2: Minería de Datos & KDD (Bottom Left)
  addSurface(slide, pos(64, 434, 556, 214), { fill: C.white, line: { style: "solid", fill: C.line, width: 1 } });
  addText(slide, "Minería de Datos y Proceso KDD", pos(88, 448, 508, 26), { fontSize: 17, color: C.navy, bold: true });
  addText(slide, "· Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR.\n· Scikit-learn Developers (2026). Árboles CART con GridSearchCV y K-Means.\n· Metodología KDD: selección, limpieza, transformación, minería y evaluación en prueba (Recall 95.15% en test; K=3 sobre 480 perfiles F2). La publicación BI actual reejecutada conserva 481 perfiles.", pos(88, 480, 508, 154), { fontSize: 14.5, color: C.gray, lineSpacing: 1.15, autoFit: "shrinkText" });

  // Box 3: Costos, Finanzas y FinOps (Top Right)
  addSurface(slide, pos(656, 204, 560, 214), { fill: C.white, line: { style: "solid", fill: C.line, width: 1 } });
  addText(slide, "Finanzas, CAPEX/OPEX y FinOps", pos(680, 218, 512, 26), { fontSize: 17, color: C.navy, bold: true });
  addText(slide, "· Horngren, C. T., et al. (2012). Contabilidad de costos: un enfoque gerencial. Escenario de CAPEX (US$4,520) y OPEX anual (US$4,200).\n· Ross, S. A., et al. (2019). Fundamentals of Corporate Finance. TCO 3 años (US$17,120), análisis de sensibilidad y ROI (31.2% a 293.6%).\n· Storment, J. R., & Fuller, M. (2020). Cloud FinOps. Sostenibilidad y costos elásticos.", pos(680, 250, 512, 154), { fontSize: 14.5, color: C.gray, lineSpacing: 1.15, autoFit: "shrinkText" });

  // Box 4: Operaciones y Marco Legal (Bottom Right)
  addSurface(slide, pos(656, 434, 560, 214), { fill: C.white, line: { style: "solid", fill: C.line, width: 1 } });
  addText(slide, "Operaciones y Marco Normativo Ético", pos(680, 448, 512, 26), { fontSize: 17, color: C.navy, bold: true });
  addText(slide, "· Richards, G. (2018). Warehouse Management. Gestión de cuellos de botella y balanceo de cuadrillas en perfiles de resolución prolongada.\n· Asamblea Legislativa de El Salvador (2024). Ley para la Protección de Datos Personales (Decreto 144). Principios de minimización, anonimización espacial y supervisión humana obligatoria (Human-in-the-Loop) sin decisiones punitivas automáticas.", pos(680, 480, 512, 154), { fontSize: 14.5, color: C.gray, lineSpacing: 1.15, autoFit: "shrinkText" });

  addFooter(slide, "Referencias académicas y normativas consolidadas según premisa general de la cátedra DMD104 (Universidad Don Bosco).");
  addNote(slide, "Fuentes teóricas y normativas del proyecto consolidado.", "Sustenta la base conceptual de modelado dimensional, procesos ETL, KDD, formulación de costos CAPEX/OPEX, evaluación financiera y gobernanza ética de datos.");
}

async function buildDeck() {
  await registerPresentationFonts();
  await fs.mkdir(buildDir, { recursive: true });
  await fs.mkdir(renderDir, { recursive: true });
  await fs.mkdir(stagingDir, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  buildCover(presentation);
  buildProblem(presentation);
  buildEvidence(presentation);
  buildArchitecture(presentation);
  buildMining(presentation);
  buildKmeans(presentation);
  buildTreeLimits(presentation);
  await buildPanorama(presentation);
  await buildDiagnostics(presentation);
  buildSegmentation(presentation);
  buildValueCosts(presentation);
  buildConclusion(presentation);
  buildReferences(presentation);

  const draftPath = path.join(buildDir, "draft.pptx");
  const draft = await PresentationFile.exportPptx(presentation);
  await draft.save(draftPath);
  await writeBlob(path.join(buildDir, "draft.pdf"), await presentation.export({ format: "pdf" }));
  await writeBlob(path.join(buildDir, "draft-montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 0.5 }));
  for (let index = 0; index < presentation.slides.items.length; index += 1) {
    await writeBlob(path.join(buildDir, `slide-${String(index + 1).padStart(2, "0")}.png`), await presentation.export({ slide: presentation.slides.items[index], format: "png", scale: 1 }));
  }

  await fs.rm(finalPptx, { force: true });
  await fs.rm(finalPdf, { force: true });
  await fs.rm(candidatePath, { force: true });
  await fs.rm(validationReceipt, { force: true });

  const result = await finalizePresentation({
    explicitTotalSlideCount: 13,
    workspaceDir: taskWorkspaceDir,
    candidatePath: draftPath,
    finalPath: finalPptx,
    pythonExecutable: RUNTIME_PYTHON,
    integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-bullet-geometry",
      "--validate-heading-fit",
      "--validate-heading-punctuation",
      "--require-native-table-slide", "11",
    ],
    requiredNativeTableOwnerSlides: [11],
    fontPolicy: { basis: "design", families: [FONT] },
    verifyArtifactToolImport: true,
    materializeLiteralChartWorkbooks: true,
    receiptPath: validationReceipt,
  });

  const finalPresentation = await PresentationFile.importPptx(await FileBlob.load(finalPptx));
  await writeBlob(finalPdf, await finalPresentation.export({ format: "pdf" }));
  for (let index = 0; index < finalPresentation.slides.items.length; index += 1) {
    await writeBlob(path.join(renderDir, `slide-${String(index + 1).padStart(2, "0")}.png`), await finalPresentation.export({ slide: finalPresentation.slides.items[index], format: "png", scale: 1 }));
  }
  await writeBlob(path.join(renderDir, "deck-montage.webp"), await finalPresentation.export({ format: "webp", montage: true, scale: 0.5 }));
  const inspect = await finalPresentation.inspect({ kind: "slide,textbox,shape,image,table,chart,notes", maxChars: 16000 });
  await fs.writeFile(path.join(renderDir, "inspection.ndjson"), inspect.ndjson, "utf8");

  // Copiar archivos finales también a dmd-3/fase-3/
  const fase3Pptx = path.resolve(taskWorkspaceDir, "..", "..", "fase-3", "Presentacion_Fase3_NYC311.pptx");
  const fase3Pdf = path.resolve(taskWorkspaceDir, "..", "..", "fase-3", "Presentacion_Fase3_NYC311.pdf");
  await fs.copyFile(finalPptx, fase3Pptx);
  await fs.copyFile(finalPdf, fase3Pdf);
  console.log(`Copia a fase-3 completada:\n - ${fase3Pptx}\n - ${fase3Pdf}`);

  console.log(JSON.stringify({
    finalPptx,
    finalPdf,
    fase3Pptx,
    fase3Pdf,
    slideCount: finalPresentation.slides.items.length,
    receipt: result.receiptPath,
    renderDir,
  }, null, 2));
}

buildDeck().catch((error) => {
  console.error(error?.stack || error?.message || String(error));
  process.exitCode = 1;
});
