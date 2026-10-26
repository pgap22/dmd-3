from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
DMD3_DIR = ROOT.parents[2]  # C:\Users\Gerardo\udb\dmd-fase-3\dmd-3
WORKSPACE = DMD3_DIR.parent  # C:\Users\Gerardo\udb\dmd-fase-3
FASE3_DIR = DMD3_DIR / "fase-3"
OUT_DOCX_QA = ROOT / "Documento_Fase3.docx"
OUT_DOCX_FASE3 = FASE3_DIR / "Documento_Fase3.docx"
OUT_PDF_FASE3 = FASE3_DIR / "Documento_Fase3.pdf"
OUT_PDF_QA = ROOT / "Documento_Fase3.pdf"
SOURCE_LOGO = WORKSPACE / "tmp" / "docx_image1.png"

NAVY = "17365D"
BLUE = "1F4E79"
LIGHT_BLUE = "DCE6F1"
PALE_BLUE = "F3F7FB"
GRAY = "666666"
LIGHT_GRAY = "D9E2F3"
BLACK = "000000"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, **kwargs) -> None:
    """Establece bordes visibles en las celdas de tabla."""
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge not in kwargs:
            continue
        tag = "w:%s" % edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        for key in ["val", "sz", "space", "color"]:
            if key in kwargs[edge]:
                element.set(qn("w:%s" % key), str(kwargs[edge][key]))


def set_cell_width(cell, width_inches: float) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width_inches * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def set_font(run, name="Aptos", size=10.2, color=BLACK, bold=False, italic=False) -> None:
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    run.bold = bold
    run.italic = italic


def set_paragraph_spacing(paragraph, before=0, after=6, line=1.08) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line


def add_bookmark(paragraph, name: str, bookmark_id: int) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def add_internal_link(paragraph, text: str, anchor: str, color=BLUE, underline=True) -> None:
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), anchor)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Aptos")
    rFonts.set(qn("w:hAnsi"), "Aptos")
    rPr.append(rFonts)
    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    rPr.append(c)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "20")
    rPr.append(sz)
    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rPr.append(u)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    hyperlink.append(r)
    paragraph._p.append(hyperlink)


def add_external_link(paragraph, label: str, url: str, color=BLUE) -> None:
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    rPr.append(c)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.text = label
    r.append(t)
    hyperlink.append(r)
    paragraph._p.append(hyperlink)


def add_page_field(paragraph) -> None:
    r = paragraph.add_run()
    fld1 = OxmlElement("w:fldSimple")
    fld1.set(qn("w:instr"), "PAGE")
    r._r.append(fld1)


def set_keep(paragraph, keep_next=False, keep_lines=True) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    if keep_next:
        kn = OxmlElement("w:keepNext")
        p_pr.append(kn)
    if keep_lines:
        kl = OxmlElement("w:keepLines")
        p_pr.append(kl)


def add_para(doc, text="", style="Normal", before=0, after=6, line=1.08, align=None, color=BLACK, size=10.2, bold=False, italic=False):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    set_paragraph_spacing(p, before=before, after=after, line=line)
    if text:
        r = p.add_run(text)
        set_font(r, size=size, color=color, bold=bold, italic=italic)
    return p


def add_heading(doc, text: str, level: int, bookmark: str, bookmark_id: int):
    p = doc.add_paragraph(style=f"Heading {level}")
    add_bookmark(p, bookmark, bookmark_id)
    set_keep(p, keep_next=True, keep_lines=True)
    if level == 1:
        set_paragraph_spacing(p, before=14, after=4, line=1.05)
        r = p.add_run(text)
        set_font(r, size=15.5, color=NAVY, bold=True)
        # Enlace sutil para volver al indice
        back = doc.add_paragraph()
        set_paragraph_spacing(back, before=0, after=5, line=1.0)
        add_internal_link(back, "Volver al índice", "indice", color=GRAY, underline=False)
    elif level == 2:
        set_paragraph_spacing(p, before=10, after=3, line=1.05)
        r = p.add_run(text)
        set_font(r, size=12.2, color=BLUE, bold=True)
        back = doc.add_paragraph()
        set_paragraph_spacing(back, before=0, after=4, line=1.0)
        add_internal_link(back, "Volver al índice", "indice", color=GRAY, underline=False)
    else:
        set_paragraph_spacing(p, before=7, after=2, line=1.05)
        r = p.add_run(text)
        set_font(r, size=10.5, color=NAVY, bold=True)
    return p


def add_caption(doc, text: str):
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=3, after=6, line=1.0)
    r = p.add_run(text)
    set_font(r, size=8.5, color=GRAY, italic=True)
    return p


def add_bullets(doc, items: Iterable[str], level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        set_paragraph_spacing(p, before=0, after=3, line=1.05)
        r = p.add_run(item)
        set_font(r, size=9.8, color=BLACK)


def add_table(doc, headers, rows, widths, font_size=8.6, header_fill=BLUE, first_col_bold=False):
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False

    # Header
    set_repeat_table_header(t.rows[0])
    for j, h in enumerate(headers):
        cell = t.cell(0, j)
        set_cell_width(cell, widths[j])
        set_cell_shading(cell, header_fill)
        set_cell_border(cell, top={"val": "single", "sz": "4", "color": BLUE},
                              bottom={"val": "single", "sz": "8", "color": NAVY},
                              left={"val": "single", "sz": "4", "color": LIGHT_GRAY},
                              right={"val": "single", "sz": "4", "color": LIGHT_GRAY})
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        set_paragraph_spacing(p, before=2, after=2, line=1.0)
        r = p.add_run(str(h))
        set_font(r, size=font_size + 0.3, color="FFFFFF", bold=True)

    # Rows
    for i, row in enumerate(rows):
        fill = PALE_BLUE if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            cell = t.cell(i + 1, j)
            set_cell_width(cell, widths[j])
            set_cell_shading(cell, fill)
            set_cell_border(cell, top={"val": "single", "sz": "4", "color": LIGHT_GRAY},
                                  bottom={"val": "single", "sz": "4", "color": LIGHT_GRAY},
                                  left={"val": "single", "sz": "4", "color": LIGHT_GRAY},
                                  right={"val": "single", "sz": "4", "color": LIGHT_GRAY})
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            set_paragraph_spacing(p, before=2, after=2, line=1.0)
            r = p.add_run(str(val))
            set_font(r, size=font_size, color=BLACK, bold=(first_col_bold and j == 0))

    spacer = doc.add_paragraph()
    set_paragraph_spacing(spacer, before=0, after=5, line=1.0)
    return t


def add_callout(doc, title: str, body: str):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.cell(0, 0)
    set_cell_width(cell, 6.75)
    set_cell_shading(cell, "F5F8FC")
    set_cell_border(cell, left={"val": "single", "sz": "24", "color": BLUE},
                          top={"val": "single", "sz": "4", "color": LIGHT_GRAY},
                          bottom={"val": "single", "sz": "4", "color": LIGHT_GRAY},
                          right={"val": "single", "sz": "4", "color": LIGHT_GRAY})
    p = cell.paragraphs[0]
    set_paragraph_spacing(p, before=3, after=2, line=1.05)
    r_t = p.add_run(title + ": ")
    set_font(r_t, size=9.4, color=NAVY, bold=True)
    r_b = p.add_run(body)
    set_font(r_b, size=9.4, color=BLACK)
    spacer = doc.add_paragraph()
    set_paragraph_spacing(spacer, before=0, after=4, line=1.0)
    return t


def set_style_defaults(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.2)
    normal.font.color.rgb = RGBColor.from_string(BLACK)
    normal.paragraph_format.line_spacing = 1.08
    normal.paragraph_format.space_after = Pt(6)


def add_header_footer(section):
    # Header
    header = section.header
    hp = header.paragraphs[0]
    set_paragraph_spacing(hp, before=0, after=0, line=1.0)
    hr = hp.add_run("NYC311 · Solución Analítica Integral | DW · Minería · Power BI · Fase 3")
    set_font(hr, size=8.4, color=GRAY, italic=True)

    # Footer
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_paragraph_spacing(fp, before=0, after=0, line=1.0)
    fr1 = fp.add_run("Universidad Don Bosco · DMD104 | Página ")
    set_font(fr1, size=8.4, color=GRAY)
    add_page_field(fp)


def build() -> None:
    doc = Document()
    set_style_defaults(doc)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.75)
    section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    add_header_footer(section)

    # ----------------------------------------------------
    # COVER
    # ----------------------------------------------------
    cover_spacer = doc.add_paragraph()
    cover_spacer.paragraph_format.space_after = Pt(3)
    if SOURCE_LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_spacing(p, before=2, after=8, line=1.0)
        p.add_run().add_picture(str(SOURCE_LOGO), width=Inches(1.12))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=4, line=1.0)
    r = p.add_run("UNIVERSIDAD DON BOSCO")
    set_font(r, size=13, color=NAVY, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=12, line=1.0)
    r = p.add_run("FACULTAD DE ESTUDIOS TECNOLÓGICOS / ESCUELA DE COMPUTACIÓN")
    set_font(r, size=9.5, color=GRAY, bold=True)

    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=10, after=6, line=1.0)
    r = p.add_run("Solución analítica integral para NYC311")
    set_font(r, size=26, color=BLACK, bold=True)

    p = doc.add_paragraph(style="Subtitle")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=6, line=1.0)
    r = p.add_run("Informe analítico consolidado de entrega y defensa oral | Fase 3")
    set_font(r, size=13.5, color=NAVY, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=14, line=1.0)
    r = p.add_run("Integración de Data Warehouse, Descubrimiento de Conocimiento (KDD) y Business Intelligence")
    set_font(r, size=10.5, color=GRAY, italic=True)

    cover_info = [
        "Asignatura: Data Warehouse y Minería de Datos (DMD104)",
        "Caso de estudio: Solicitudes de servicio ciudadano no urgente de la Ciudad de Nueva York (NYC311)",
        "Período BI actual: enero y abril a julio de 2026 | F2 original: abril a julio de 2026",
        "Fecha de entrega y defensa: octubre de 2026",
    ]
    for line in cover_info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_spacing(p, before=0, after=2.5, line=1.0)
        r = p.add_run(line)
        set_font(r, size=9.8, color=BLACK)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=12, after=4, line=1.0)
    r = p.add_run("Integrantes del equipo de trabajo:")
    set_font(r, size=10.5, color=NAVY, bold=True)

    integrantes = [
        ("Lemus Mejía, Fernando José", "LM212528", "Analista / Modelador Dimensional"),
        ("Bonilla Saz, Gerardo Rafael", "BS242634", "Investigador / Ingeniero de Datos"),
        ("Chávez Castillo, Edson Enrique", "CC242635", "Investigador / Modelador de Minería"),
        ("López Ortiz, César Giovanni", "LO232756", "Diseñador / Especialista Power BI"),
        ("Galdámez Soto, Juan José", "GS242646", "Redactor / Integrador Metodológico"),
    ]
    for nom, carnet, rol in integrantes:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_spacing(p, before=0, after=2, line=1.0)
        r1 = p.add_run(nom)
        set_font(r1, size=9.5, color=BLACK, bold=True)
        r2 = p.add_run(f" · Carnet: {carnet} ({rol})")
        set_font(r2, size=9.0, color=GRAY)

    add_callout(doc, "Propósito del informe", "Presentar en una sola narrativa estructurada la trazabilidad completa del proyecto NYC311: desde el modelado dimensional Kimball y los procesos ETL de la Fase 1, pasando por el proceso KDD con árboles CART y K-Means en la Fase 2, hasta el portal ejecutivo en Power BI, el análisis de costos CAPEX/OPEX y la viabilidad FinOps de la Fase 3.")

    doc.add_page_break()

    # ----------------------------------------------------
    # RESUMEN EJECUTIVO
    # ----------------------------------------------------
    add_heading(doc, "Resumen ejecutivo", 1, "resumen", 1)
    add_para(doc, "Este documento consolida la entrega final del proyecto analítico de la asignatura Data Warehouse y Minería de Datos (DMD104) para el caso de estudio de solicitudes ciudadanas no urgentes NYC311. El flujo de trabajo articula de forma verificable tres etapas continuas: la Fase 1 estructuró las solicitudes operativas en un Data Warehouse relacional bajo esquema estrella; la Fase 2 ejecutó el proceso de descubrimiento de conocimiento (KDD) entrenando un árbol de decisión supervisado y un agrupamiento K-Means sobre perfiles operativos; finalmente, la Fase 3 integró estos componentes en un modelo semántico interactivo en Power BI y un cubo OLAP multidimensional en SSAS, complementado con un análisis riguroso de costos (CAPEX/OPEX), viabilidad financiera y marco ético-legal.")
    add_para(doc, "La base analítica actual del DW integra exactamente 1,312,465 solicitudes disponibles entre enero y julio de 2026, con registros en enero y abril–julio, desde el portal oficial NYC Open Data (dataset erm2-nwe9). En estricto apego a las reglas de integridad de datos, 63,467 solicitudes carecen de fecha observada de cierre; estos registros se mantienen explícitamente como NULL y no se imputan arbitrariamente como demoras normales ni como cierres inmediatos. Para las 1,248,998 solicitudes con tiempo de resolución medido, se conserva el P75 histórico de 4,329 minutos (~72.2 horas) como umbral comparable de demora alta, sin presentarlo como SLA.")
    add_para(doc, "El experimento F2 original conserva sus métricas de prueba: CART con Recall de 95.15%, F1 de 78.37% y ROC-AUC de 0.952, y K-Means sobre 480 perfiles del snapshot abril–julio. La publicación BI actual reejecutada sobre el rango disponible integra 481 perfiles, cubre 1,298,155 solicitudes y mantiene visibles 14,310 solicitudes fuera de perfil. En ambos casos, K-Means se aplica a perfiles agregados por agencia + complaint_type + borough, no a solicitudes individuales.")
    add_callout(doc, "Conclusión directiva", "El tablero de Power BI no sustituye el juicio de las agencias municipales ni formula atribuciones causales; su ventaja reside en otorgar a la gerencia municipal visibilidad centralizada, permitiendo auditar la cobertura de cierre, priorizar cuadrillas en perfiles de resolución prolongada y simular ahorros de reportería bajo escenarios transparentes.")

    add_heading(doc, "Cuadro de mando resumen de evidencia", 2, "resumen-lectura", 2)
    add_table(doc, ["Dimensión o artefacto", "Métrica / Evidencia documentada", "Interpretación y lectura analítica válida"], [
        ("Universo BI actual", "1,312,465 solicitudes", "Población disponible en el DW entre enero y julio de 2026; preservada en la vista BI."),
        ("Calidad de datos BI", "63,467 sin resolución (4.84%)", "Casos sin cierre observado; conservados como NULL sin imputación."),
        ("Población con tiempo", "1,248,998 solicitudes (95.16%)", "Denominador real sobre el cual se calculan medianas y tasas de demora."),
        ("Umbral P75 histórico", "4,329 minutos (72.2 horas)", "Corte empírico del período analizado para definir demora alta; no es un SLA normativo."),
        ("Árbol de Decisión CART", "Recall: 95.15% · ROC-AUC: 0.952", "Detecta 58,549 de 61,531 demoras reales en prueba; útil como filtro de triaje."),
        ("Clustering K-Means", "481 perfiles BI · 480 en F2", "Agrupa perfiles de agencia+tipo+borough en 3 clusters; cubre 1,298,155 solicitudes actuales."),
        ("Casos fuera de perfil", "14,310 solicitudes (1.09%)", "Solicitudes no elegibles para perfil; visibles bajo la etiqueta 'Sin perfil K-Means'."),
        ("TCO a 3 años", "US$17,120 (CAPEX + OPEX)", "US$4,520 de inversión inicial + US$4,200 anuales de operación y licenciamiento."),
        ("ROI Escenario Base", "162.4% (Payback en mes 14)", "Escenario basado exclusivamente en horas de reportería liberadas valoradas a US$18/h."),
    ], [1.6, 2.0, 3.15], font_size=8.2, first_col_bold=True)

    doc.add_page_break()

    # ----------------------------------------------------
    # ÍNDICE ESTÁTICO
    # ----------------------------------------------------
    toc = doc.add_paragraph()
    add_bookmark(toc, "indice", 50)
    toc.style = doc.styles["Heading 1"]
    set_paragraph_spacing(toc, before=0, after=8, line=1.0)
    r = toc.add_run("Índice de contenido")
    set_font(r, size=17, color=BLACK, bold=True)
    add_para(doc, "Índice navegable con vínculos internos. Haga clic en cualquier sección para desplazarse directamente al capítulo correspondiente.", size=9.3, color=GRAY, italic=True, after=8)

    entries = [
        ("1. Contexto organizacional y alcance del proyecto", "cap1"),
        ("2. Fase 1: El Data Warehouse y el Ciclo de Vida Kimball", "cap2"),
        ("3. Fase 2: Minería de datos y descubrimiento de conocimiento (KDD)", "cap3"),
        ("4. Fase 3: Business Intelligence en Power BI y procesamiento OLAP", "cap4"),
        ("5. Costos, viabilidad financiera y marco FinOps", "cap5"),
        ("6. Hallazgos cuantitativos para la gestión operativa", "cap6"),
        ("7. Límites metodológicos, supuestos y marco ético-legal", "cap7"),
        ("8. Conclusiones y recomendaciones estratégicas", "cap8"),
        ("9. Fuentes consultadas y referencias bibliográficas", "cap9"),
    ]
    for label, anchor in entries:
        p = doc.add_paragraph()
        set_paragraph_spacing(p, before=1.5, after=6, line=1.0)
        add_internal_link(p, label, anchor, color=BLUE, underline=True)
        p.paragraph_format.left_indent = Cm(0.45)

    add_callout(doc, "Criterio de integridad y rigor académico", "Todas las cifras de solicitudes, tiempos observados y parámetros de minería provienen de los artefactos y repositorios genuinos de Fase 1 (catedra_fase1) y Fase 2 (dmd-fase2). Los costos y retornos se presentan como escenarios metodológicos de viabilidad fundamentados en la literatura financiera (Ross et al., 2019; Horngren et al., 2012; Storment & Fuller, 2020), evitando atribuir ahorros automáticos o causalidades no probadas.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 1
    # ----------------------------------------------------
    add_heading(doc, "1. Contexto organizacional y alcance del proyecto", 1, "cap1", 10)
    add_para(doc, "El sistema NYC311 constituye la ventanilla única de atención para requerimientos y reclamos ciudadanos de servicios municipales no urgentes en la Ciudad de Nueva York. A través de canales telefónicos, portal web, aplicaciones móviles y datos abiertos, el sistema recibe millones de solicitudes anuales que son derivadas a diversas dependencias especializadas, tales como el Departamento de Policía (NYPD), el Departamento de Preservación y Desarrollo de la Vivienda (HPD), el Departamento de Transporte (DOT), el Departamento de Saneamiento (DSNY) y el Departamento de Protección Ambiental (DEP).")
    add_para(doc, "El problema de negocio radica en que, en su formato operacional transaccional, los registros de NYC311 dificultan a los tomadores de decisiones evaluar de forma unificada la carga de trabajo, los patrones temporales de atención y los cuellos de botella que provocan rezagos críticos. La unidad atómica de análisis de esta investigación es la solicitud individual de servicio, identificada de manera unívoca por su clave de negocio codigo_solicitud (Unique Key en la fuente abierta).")
    add_para(doc, "La publicación BI actual integra los registros disponibles entre enero y julio de 2026, con presencia en enero y abril–julio, para un total de 1,312,465 solicitudes. La Fase 2 original conserva su ventana homogénea de abril–julio con 1,293,816 solicitudes; ambas poblaciones se distinguen para evitar mezclar granos ni atribuir al snapshot histórico cifras de la publicación actual.")

    add_heading(doc, "Preguntas de decisión que responde la solución", 2, "cap1-preguntas", 11)
    add_bullets(doc, [
        "¿Cuál es el volumen mensual de solicitudes ciudadanas y cómo se distribuye territorialmente entre los cinco condados (boroughs)?",
        "¿Cuáles agencias municipales, canales de ingreso y tipologías de reclamos presentan las mayores medianas observadas de atención?",
        "¿Qué proporción de las solicitudes no registra fecha de cierre en los sistemas y cómo impacta esto en la medición de eficiencia institucional?",
        "¿Cómo se configuran los perfiles operativos homogéneos de atención mediante clustering no supervisado para orientar la distribución de cuadrillas de campo?",
        "¿Es factible predecir con alta sensibilidad si un reclamo entrante se ubicará en el cuartil superior de demora (P75) para activar revisiones preventivas?",
    ])

    add_heading(doc, "Límites explícitos y lo que no se afirma", 2, "cap1-noafirma", 12)
    add_para(doc, "En cumplimiento de las normas de integridad técnica, este proyecto establece demarcaciones analíticas claras:")
    add_bullets(doc, [
        "No causalidad: El modelo predictivo identifica asociaciones estadísticas entre características del reclamo y la probabilidad de demora; bajo ninguna circunstancia demuestra que una agencia o sector geográfico sea la causa intrínseca del retraso.",
        "No SLA contractual: El percentil 75 histórico (4,329 minutos) es un umbral empírico derivado de la distribución de tiempos del período abril-julio 2026; no constituye un acuerdo formal de nivel de servicio (SLA) comprometido por la alcaldía.",
        "Tratamiento estricto de nulos: Una solicitud sin fecha de resolución observada no representa una atención inmediata ni una demora normal; se conserva como valor NULL y se audita de forma independiente en la tasa de resolución.",
        "Sin pronóstico ciego en producción: Las métricas de desempeño del árbol de decisión corresponden estrictamente al conjunto de evaluación de prueba; no representan pronósticos operativos ya desplegados en tiempo real.",
    ])

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 2
    # ----------------------------------------------------
    add_heading(doc, "2. Fase 1: El Data Warehouse y el Ciclo de Vida Kimball", 1, "cap2", 20)
    add_para(doc, "La Fase 1 sentó los cimientos de la arquitectura de datos construyendo un Data Warehouse corporativo en Microsoft SQL Server (base DW_NYC311). La fuente operacional de extracción corresponde al conjunto oficial '311 Service Requests from 2020 to Present' de NYC Open Data, identificado bajo el identificador de API erm2-nwe9. La ingesta y transformación se diseñaron mediante paquetes de SQL Server Integration Services (SSIS), transitando rigurosamente por capas raw, staging (stg), procedimientos de control (etl) y el esquema dimensional definitivo (dw).")

    add_heading(doc, "Alineación con el Ciclo de Vida Dimensional de Kimball", 2, "cap2-kimball", 21)
    add_para(doc, "El diseño y despliegue del Data Warehouse se estructuró siguiendo formalmente las diez etapas del Ciclo de Vida Dimensional propuesto por Ralph Kimball (Kimball, Reeves, Ross, & Thornthwaite, 1998; citado en Lemus et al., 2026c). Esta metodología asegura que el almacenamiento multidimensional responda a las necesidades de análisis de negocio manteniendo una estricta coherencia arquitectónica:")

    add_table(doc, ["Fase del Ciclo de Vida (Kimball et al., 1998)", "Implementación específica en el proyecto NYC311", "Artefacto verificable"], [
        ("1. Planificación del proyecto", "Definición del caso de estudio NYC311, justificación analítica y objetivos de gestión.", "Plan de trabajo y alcance F1"),
        ("2. Definición de requerimientos", "Identificación de KPIs: volumen de solicitudes, tiempos de cierre y tasas de demora.", "Especificación de métricas"),
        ("3. Modelado dimensional", "Diseño de esquema estrella centrado en el hecho transaccional dw.FactSolicitud.", "Diagrama entidad-relación DW"),
        ("4. Diseño físico y almacenamiento", "Creación de schemas raw, stg, etl y dw en SQL Server DW_NYC311 con índices B-Tree.", "Scripts DDL (01, 02, 03_ddl.sql)"),
        ("5. Especificación del subsistema ETL", "Mapeo de atributos de la API SODA, tipado estricto y resolución de llaves foráneas.", "Matriz de mapeo operacional"),
        ("6. Desarrollo del proceso ETL", "Paquete SSIS Package.dtsx con flujos de control, data flow tasks y manejo de errores.", "catedra_fase1/ssis/Package.dtsx"),
        ("7. Instalación y configuración técnica", "Entorno local de base de datos SQL Server Developer Edition y herramientas de cliente.", "Servidor SQL Server local"),
        ("8. Herramientas analíticas y acceso", "Cubo multidimensional SSAS (CuboFase1) y vistas de minería y explotación.", "cubo_olap/ y mining.vw_dataset"),
        ("9. Despliegue de BI y aplicaciones", "Construcción del reporte ejecutivo interactivo en Power BI Desktop (Fase 3).", "NYC311_Fase3_Final.pbix"),
        ("10. Mantenimiento y gobernanza", "Validaciones de cardinalidad, no multiplicación de registros y auditoría continua.", "Consultas de validación SQL"),
    ], [1.7, 3.4, 1.65], font_size=7.9, first_col_bold=True)

    add_heading(doc, "Grano dimensional y catálogo de entidades", 2, "cap2-modelo", 22)
    add_para(doc, "El grano de la tabla de hechos dw.FactSolicitud es estrictamente atómico: una fila representa exactamente una solicitud ciudadana registrada. Cada registro mantiene su clave de negocio (codigo_solicitud) y se vincula mediante llaves subrogadas enteras a seis dimensiones conformadas. La medida numérica central es minutos_resolucion, calculada mediante la diferencia en minutos entre fecha_creacion y fecha_cierre (DATEDIFF); si la solicitud no cuenta con fecha de cierre en la fuente, el campo retiene su valor NULL.")

    add_table(doc, ["Tabla / Dimensión", "Clave / Grano", "Atributos principales", "Propósito en el análisis"], [
        ("dw.FactSolicitud", "1 fila = 1 solicitud", "minutos_resolucion, latitude, longitude, claves foráneas", "Medición de volumen y tiempos observados."),
        ("dw.DimFecha", "1 fila = 1 día calendario", "fecha, anio, mes, dia, dia_semana, es_fin_semana", "Análisis de estacionalidad (roles creación y cierre)."),
        ("dw.DimAgencia", "1 fila = 1 agencia municipal", "agency (siglas), agency_name (nombre completo)", "Responsabilidad institucional y capacidad instalada."),
        ("dw.DimProblema", "1 fila = 1 tipo de incidente", "complaint_type, descriptor", "Clasificación semántica del reclamo ciudadano."),
        ("dw.DimGeografia", "1 fila = 1 zona territorial", "borough, city, incident_zip", "Segmentación geográfica y equidad territorial."),
        ("dw.DimEstado", "1 fila = 1 estado de trámite", "status (Closed, Open, Pending, In Progress, etc.)", "Auditoría de ciclo de vida del reclamo."),
        ("dw.DimCanal", "1 fila = 1 canal de ingreso", "open_data_channel_type (Phone, Online, Mobile, Other)", "Evaluación de adopción de canales digitales."),
    ], [1.35, 1.35, 2.1, 1.95], font_size=7.8, first_col_bold=True)

    add_heading(doc, "Procesamiento analítico en línea (OLAP)", 2, "cap2-olap", 23)
    add_para(doc, "Como parte de la arquitectura multidimensional, el proyecto incluye un cubo OLAP desarrollado en SQL Server Analysis Services (SSAS), ubicado en dmd-3/fase1/cubo_olap/CuboFase1.dwproj. Este cubo estructura jerarquías de tiempo (Año-Mes-Día), geografía (Borough-Zip) y agrega como dimensión analítica especializada Dim PerfilCluster, permitiendo consultas multidimensionales MDX optimizadas para cruzar el rendimiento histórico con los clústeres de minería.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 3
    # ----------------------------------------------------
    add_heading(doc, "3. Fase 2: Minería de datos y descubrimiento de conocimiento (KDD)", 1, "cap3", 30)
    add_para(doc, "La Fase 2 ejecutó el proceso formal de Descubrimiento de Conocimiento en Bases de Datos (KDD) empleando la biblioteca de código abierto Scikit-learn (Pedregosa et al., 2011; Scikit-learn Developers, 2026). El conjunto de datos de partida se extrajo directamente del Data Warehouse a través de la vista especializada mining.vw_dataset_fase2, garantizando total linaje con la Fase 1. El experimento documentado en F2 corresponde al snapshot de 1,293,816 solicitudes registradas entre abril y julio de 2026; la publicación BI actual se documenta por separado en Fase 3.")

    add_heading(doc, "Construcción de la variable objetivo y manejo de valores faltantes", 2, "cap3-variable", 31)
    add_para(doc, "La variable binaria de interés, demora_alta, se formuló a partir del percentil 75 histórico de la duración observada (minutos_resolucion):")
    add_bullets(doc, [
        "Universo con duración válida observada: 1,230,737 solicitudes (95.13% del total).",
        "Valor del percentil 75 (P75): 4,329 minutos (equivalente a 72 horas con 9 minutos).",
        "Regla de asignación: Si minutos_resolucion > 4,329, demora_alta = 1 (alta demora, cuartil superior, 307,656 casos); si minutos_resolucion <= 4,329, demora_alta = 0 (demora estándar, 923,081 casos).",
        "Tratamiento de solicitudes abiertas: 63,079 solicitudes carecen de fecha de cierre observada (minutos_resolucion IS NULL). Se conservan estrictamente como demora_alta = NULL, separando la calidad y completitud de datos de la métrica de tiempo.",
    ])

    add_heading(doc, "Técnica Supervisada: Clasificación con Árbol de Decisión CART", 2, "cap3-arbol", 32)
    add_para(doc, "El objetivo del modelo predictivo es anticipar si una solicitud entrante corre riesgo de caer en demora alta para activar alertas operativas preventivas. Para garantizar un modelo generalizable y prevenir fugas de información (data leakage), se excluyeron taxativamente los atributos que sólo se conocen después del cierre o que actúan como sustitutos del objetivo: minutos_resolucion, status, fecha_cierre, codigo_solicitud, coordenadas geográficas finas y anio.")
    add_para(doc, "Las variables predictoras seleccionadas antes del cierre fueron: agency, complaint_type, borough, open_data_channel_type, mes y dia_semana. Las variables categóricas se transformaron mediante OneHotEncoder. El dataset se dividió en 80% para entrenamiento y 20% para prueba estratificada (semilla 42). El árbol se optimizó mediante GridSearchCV evaluando 54 combinaciones de hiperparámetros con validación cruzada en 5 pliegues:")

    add_table(doc, ["Métrica de Desempeño (Test Set)", "Valor Numérico", "Conteo Absoluto en Prueba", "Significado Operativo para la Gestión Municipal"], [
        ("Sensibilidad (Recall)", "95.15%", "58,549 de 61,531 demoras reales", "Detecta de manera preventiva el 95.15% de los incidentes que tardarán más del P75."),
        ("Precisión (Precision)", "66.63%", "58,549 TP / 87,877 Predichos Positivos", "2 de cada 3 alertas generadas son efectivamente demoras críticas reales."),
        ("Falsos Negativos (FN)", "4.85%", "2,982 solicitudes no detectadas", "Casos críticos que escaparon al filtro preventivo; riesgo operacional residual."),
        ("Falsos Positivos (FP)", "33.37%", "29,328 alertas de casos normales", "Casos alertados que se resolvieron a tiempo; justifican revisión humana previa."),
        ("Medida F1 (F1-Score)", "78.37%", "Media armónica balanceada", "Excelente equilibrio entre captura de demoras y control de falsas alarmas."),
        ("Área Bajo Curva ROC (AUC)", "0.952", "Capacidad discriminativa global", "Capacidad sobresaliente del modelo para ordenar reclamos de mayor a menor riesgo."),
    ], [1.7, 1.1, 1.85, 2.1], font_size=8.0, first_col_bold=True)

    add_heading(doc, "Técnica No Supervisada: Clustering K-Means sobre perfiles operativos", 2, "cap3-kmeans", 33)
    add_para(doc, "Contrario a la práctica ingenua de agrupar solicitudes individuales, la Fase 2 aplicó K-Means sobre perfiles operativos agregados por la terna (agency + complaint_type + borough). Este grano analítico representa unidades coherentes de decisión gerencial (por ejemplo, 'DOT + Pothole + Queens'). En el snapshot F2 se consolidaron 480 perfiles operativos elegibles. La reejecución integrada en Fase 3, sobre el rango actual del DW, produce 481 perfiles; no se deben presentar como la misma corrida.")
    add_para(doc, "Las variables de perfil (volumen transformado con log1p, tasa de demora alta, tasa de casos sin resolver y mediana de duración) fueron estandarizadas con StandardScaler. Mediante el método del codo y el análisis de coeficiente Silhouette (puntuación óptima de 0.421), se determinó K=3 como la estructura más interpretable y balanceada:")

    add_table(doc, ["Clúster Operativo Identificado", "Perfiles", "Solicitudes", "Mediana Duración", "Tasa Demora P75", "Tasa Sin Resolver", "Lectura Estratégica y Foco de Gestión"], [
        ("Cluster 0: Resolución rápida y baja demora", "206", "899,050", "143 min (~2.4 h)", "8.94%", "1.32%", "Operación altamente eficiente y resolutiva; bajo riesgo municipal."),
        ("Cluster 1: Resolución prolongada y alta demora", "245", "351,275", "11,376 min (~7.9 días)", "71.09%", "6.09%", "Principal foco de gestión: combina alto volumen con demoras sistemáticas."),
        ("Cluster 2: Rezago crítico y alta proporción sin resolver", "29", "29,467", "33,150 min (~23 días)", "79.10%", "82.72%", "Anomalía de flujo: 8 de cada 10 casos no tienen cierre; requiere auditar estados."),
        ("Fuera de perfil K-Means (no modelados)", "N/A", "14,024", "No asignado", "Variable", "Variable", "Combinaciones con volumen menor a 100; visibles para no omitir universo."),
    ], [1.75, 0.55, 0.85, 1.05, 0.75, 0.75, 1.55], font_size=7.3, first_col_bold=True)

    add_callout(doc, "Reejecución BI actual", "La vista bi.vw_solicitudes_segmentadas conserva el universo completo: 1,298,155 solicitudes segmentadas y 14,310 sin perfil. La corrida actual resume 203 perfiles de resolución rápida y baja demora (910,529 solicitudes; mediana 129 min), 249 perfiles de resolución prolongada y alta demora (358,005; mediana 11,241 min) y 29 perfiles de rezago crítico (29,621; mediana 21,277 min). Las tasas y medianas del remanente sin perfil son descriptivas, no resultados de un cuarto clúster.")

    add_callout(doc, "Cuadratura matemática del universo", "En la publicación BI actual, las solicitudes segmentadas (1,298,155) + las solicitudes fuera de perfil (14,310) = exactamente 1,312,465 solicitudes. En el snapshot histórico F2, la suma documentada fue 1,279,792 + 14,024 = 1,293,816. Cada ecuación pertenece a su propia corrida y no hay registros omitidos ni duplicados en la integración.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 4
    # ----------------------------------------------------
    add_heading(doc, "4. Fase 3: Business Intelligence en Power BI y procesamiento OLAP", 1, "cap4", 40)
    add_para(doc, "La Fase 3 materializa la capa de consumo gerencial unificando el Data Warehouse, los resultados de minería supervisada (señal CART) y la segmentación no supervisada (clusters K-Means). La integración se realizó en SQL Server mediante la vista bi.vw_solicitudes_segmentadas, la cual vincula dw.FactSolicitud con la dimensión bi.PerfilCluster a través de una combinación nulo-segura (LEFT JOIN) por agencia, tipo de reclamo y borough, garantizando que ninguna solicitud se duplique ni quede excluida del informe.")

    add_heading(doc, "Estructura del Informe interactivo en Power BI Desktop", 2, "cap4-paginas", 41)
    add_para(doc, "El entregable interactivo corresponde al archivo oficial NYC311_Fase3_Final.pbix (acompañado de su fuente PBIP/PBIR versionable), diseñado en relación de aspecto panorámica 16:9 y operando bajo el motor analítico columnar VertiPaq en modo Import. El tablero se compone de tres páginas temáticas complementarias:")

    add_table(doc, ["Página del Dashboard", "Pregunta de Negocio que Resuelve", "Elementos Visuales Clave", "Decisión Operativa que Habilita"], [
        ("1. Panorama de atención ciudadana", "¿Dónde se concentra el volumen de la demanda y cuánto tarda en atenderse?", "Tarjetas KPI (1,312,465 solicitudes, 330 min mediana, 313,360 demoras altas, 63,467 nulos), gráfico mensual, barras de carga por borough y segmentadores.", "Identificar picos mensuales de demanda y diagnosticar la calidad del registro de cierre por condado."),
        ("2. Dónde concentrar capacidad", "¿En cuáles agencias, condados y canales se concentran los tiempos más altos?", "Matriz de medianas por agencia y borough, distribución por canal de ingreso (Phone, Online, Mobile), estado y filtros territoriales; las cifras se leen con el filtro aplicado.", "Reasignar capacidad de respuesta hacia territorios y agencias con mayores medianas observadas, sin fijar un drilldown no comprobado."),
        ("3. Segmentación y valor operativo", "¿Cómo orientar la intervención preventiva según perfiles K-Means y reglas CART?", "Segmentador de Clusters (Rápida, Prolongada, Rezago Crítico, Sin Perfil), matriz de 481 perfiles BI y tarjeta de 14,310 solicitudes fuera de perfil.", "Focalizar auditorías en perfiles prolongados y críticos, manteniendo visible el remanente no modelado."),
    ], [1.55, 1.8, 1.85, 1.55], font_size=7.6, first_col_bold=True)

    add_heading(doc, "Catálogo de medidas DAX implementadas", 2, "cap4-dax", 42)
    add_para(doc, "El modelo semántico implementa medidas DAX formales optimizadas que calculan dinámicamente los denominadores correspondientes, evitando sumar erróneamente códigos de solicitud o imputar valores nulos:")

    add_table(doc, ["Medida DAX", "Fórmula Conceptual / Expresión", "Propósito y Comportamiento del Filtro"], [
        ("Total Solicitudes", "DISTINCTCOUNT(FactSolicitud[codigo_solicitud])", "Conteo exacto del universo actual; inmune a duplicaciones (1,312,465 a nivel general)."),
        ("Solicitudes con Tiempo", "CALCULATE([Total Solicitudes], NOT ISBLANK(minutos_resolucion))", "Filtra la población con cierre medido (1,248,998 casos); denominador de tasas de demora."),
        ("Solicitudes sin Duración", "CALCULATE([Total Solicitudes], ISBLANK(minutos_resolucion))", "Aísla las 63,467 solicitudes sin cierre observado para auditoría de calidad de datos."),
        ("Mediana Minutos Observados", "MEDIAN(FactSolicitud[minutos_resolucion])", "Mediana robusta ante valores atípicos; excluye automáticamente registros nulos (330 min global)."),
        ("Tasa Demora Alta", "DIVIDE([Demoras Altas], [Solicitudes con Tiempo], 0)", "Proporción de casos que superan el P75 histórico (25.0% sobre casos con duración)."),
        ("Solicitudes sin Perfil", "CALCULATE([Total Solicitudes], PerfilCluster[cluster_nombre] = 'Sin perfil K-Means')", "Monitorea las 14,310 solicitudes no modeladas para asegurar transparencia del modelo."),
    ], [1.6, 2.7, 2.45], font_size=7.8, first_col_bold=True)

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 5
    # ----------------------------------------------------
    add_heading(doc, "5. Costos, viabilidad financiera y marco FinOps", 1, "cap5", 50)
    add_para(doc, "En estricto apego a la rúbrica académica y a las directrices metodológicas (Lemus et al., 2026c; Horngren, Datar, & Rajan, 2012; Ross, Westerfield, & Jordan, 2019), el análisis de costos y beneficios se modela mediante escenarios transparentes con supuestos explícitos, diferenciando con rigor los costos medidos del prototipo, los costos cotizados de licencias oficiales y las proyecciones de ahorro técnico.")

    add_heading(doc, "Estructura de Costos: Distinción formal entre CAPEX y OPEX", 2, "cap5-capex", 51)
    add_para(doc, "Siguiendo los principios de contabilidad gerencial de Horngren et al. (2012), los costos del proyecto analítico se estructuran en dos categorías fundamentales:")
    add_bullets(doc, [
        "Gastos de Capital (CAPEX - Inversión Inicial): Comprende el esfuerzo técnico de ingeniería de datos, modelado dimensional, desarrollo ETL en SSIS, minería KDD en Python y diseño de tableros Power BI. El escenario académico modela una inversión inicial de US$4,520.00.",
        "Gastos Operativos (OPEX - Costos Recurrentes Anuales): Comprende soporte operativo, monitoreo, licenciamiento y continuidad del servicio analítico. El escenario académico modela un OPEX de US$4,200.00 anuales. Son supuestos de viabilidad, no facturas ni costos observados de NYC311.",
    ])

    add_table(doc, ["Categoría", "Rubro de Costo", "Base Metodológica y Supuesto", "Frecuencia", "Monto Escenario (USD)"], [
        ("CAPEX", "Desarrollo e Ingeniería", "Esfuerzo inicial modelado para integración, minería y BI", "Inversión inicial", "$4,520.00"),
        ("OPEX", "Operación y Mantenimiento", "Soporte, monitoreo y continuidad del servicio analítico", "Anual recurrente", "$4,200.00"),
        ("OPEX", "Licencias e infraestructura", "Supuesto agregado de publicación y operación; validar cotización antes de contratar", "Anual recurrente", "Incluido en OPEX"),
        ("OPEX", "Infraestructura de Servidor", "Prototipo en servidor local; producción en Azure SQL / Fabric", "Anual recurrente", "Variable (FinOps)"),
        ("TCO", "Costo Total 3 Años", "CAPEX ($4,520) + 3 años de OPEX ($4,200 × 3 = $12,600)", "Horizonte 3 años", "$17,120.00"),
    ], [1.1, 1.6, 2.5, 1.0, 1.15], font_size=7.8, first_col_bold=True)

    add_heading(doc, "Modelo de Viabilidad, Retorno de Inversión (ROI) y Análisis de Sensibilidad", 2, "cap5-roi", 52)
    add_para(doc, "De acuerdo con los fundamentos de finanzas corporativas de Ross et al. (2019), el Retorno sobre la Inversión (ROI) debe formularse sobre beneficios cuantificables verificables. Para evitar la falacia de monetizar automáticamente la precisión del árbol o los falsos negativos, el beneficio del proyecto se define exclusivamente como el ahorro en horas hombre de analistas y coordinadores dedicadas a la reportería manual y consolidación de datos, valoradas a una tarifa técnica conservadora de US$18.00/hora.")
    add_para(doc, "En un horizonte de evaluación estándar de tres (3) años con un TCO modelado de US$17,120.00, se modelan tres escenarios de sensibilidad variando el volumen semanal de horas técnicas liberadas gracias a la automatización del Data Warehouse y los paneles de Power BI:")

    add_table(doc, ["Escenario de Viabilidad", "Horas Ahorradas / Semana", "Beneficio Bruto Anual", "Beneficio Bruto 3 Años", "Beneficio Neto 3 Años", "ROI Estimado (3 Años)", "Punto de Equilibrio (Payback)"], [
        ("Conservador (Baja Adopción)", "8 h / semana", "$7,488.00", "$22,464.00", "$5,344.00", "31.2%", "Mes 28 (2.3 años)"),
        ("Base (Adopción Moderada)", "16 h / semana", "$14,976.00", "$44,928.00", "$27,808.00", "162.4%", "Mes 14 (1.2 años)"),
        ("Optimista (Plena Adopción)", "24 h / semana", "$22,464.00", "$67,392.00", "$50,272.00", "293.6%", "Mes 10 (0.8 años)"),
    ], [1.5, 1.05, 1.1, 1.1, 1.1, 0.9, 1.0], font_size=7.7, first_col_bold=True)

    add_callout(doc, "Interpretación metodológica del ROI", "La fórmula aplicada es: ROI = (Beneficio Neto 3 Años / TCO 3 Años) × 100. En el escenario base, el punto de equilibrio se alcanza aproximadamente en el mes 14. Este resultado representa una simulación paramétrica de viabilidad, condicionada a que la alcaldía mida una línea base de horas de reportería antes de desplegar la herramienta; no es ahorro realizado.")

    add_heading(doc, "Sostenibilidad y Prácticas Cloud FinOps", 2, "cap5-finops", 53)
    add_para(doc, "La investigación de referencia del equipo (Lemus et al., 2026c) analiza la sostenibilidad financiera mediante la metodología Cloud FinOps (Storment & Fuller, 2020). La decisión de utilizar una infraestructura local en SQL Server durante las Fases 1, 2 y 3 responde a la prudencia financiera de minimizar el CAPEX/OPEX durante la fase de desarrollo y validación. Para una transición productiva a la nube (Microsoft Fabric o Azure SQL Database), se recomienda adoptar prácticas FinOps de gobernanza continua: asignación de etiquetas de costo (cost tagging) por agencia municipal, aprovisionamiento bajo demanda (serverless compute) y auto-pausado de recursos en horarios de baja demanda nocturna, evitando costos descontrolados de procesamiento.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 6
    # ----------------------------------------------------
    add_heading(doc, "6. Hallazgos cuantitativos para la gestión operativa", 1, "cap6", 60)
    add_para(doc, "La articulación de las tres fases permite transformar datos crudos en conocimiento accionable para la optimización de los servicios públicos municipales, apoyándose en los principios de gestión operativa y control de cuellos de botella (Richards, 2018):")

    add_table(doc, ["Hallazgo Cuantitativo Identificado", "Sustento en Datos / Evidencia Verificable", "Recomendación Operativa y Acción Gerencial Habilitada"], [
        ("1. Concentración extrema de demoras en el percentil 75", "P75 = 4,329 min (~72.2 h); el 25% de solicitudes con tiempo (307,656) acumula la mayor fracción de horas de espera.", "Establecer un protocolo de escalamiento temprano a las 48 horas de apertura para evitar que reclamos estándar superen el umbral P75."),
        ("2. Foco prioritario en perfiles de resolución prolongada", "La publicación BI actual reúne 358,005 solicitudes en 249 perfiles con una mediana de 11,241 min y 75.12% de demora alta entre casos observados.", "Concentrar revisión de capacidad en estos perfiles, sin interpretar el agrupamiento como causalidad."),
        ("3. Brecha crítica de cierre", "La publicación BI actual reúne 29,621 solicitudes en 29 perfiles; 81.65% no tiene duración observada.", "Auditar los procesos de cierre en las agencias responsables y mantener NULL separado de demora alta."),
        ("4. Alta sensibilidad del árbol para triaje preventivo", "Recall de 95.15% en el conjunto de prueba independiente (58,549 de 61,531 demoras capturadas).", "Implementar la regla CART en la mesa de entrada como semáforo preventivo que asigne automáticamente orden de atención."),
        ("5. Variabilidad territorial significativa en medianas", "El tablero permite comparar borough, agencia y canal bajo filtros; las cifras deben leerse en el contexto de la selección aplicada.", "Usar el drilldown interactivo para priorizar investigación territorial sin fijar una cifra no comprobada como conclusión general."),
    ], [1.7, 2.05, 2.8], font_size=7.7, first_col_bold=True)

    add_heading(doc, "Ventaja competitiva generada por la solución", 2, "cap6-valor", 61)
    add_para(doc, "La ventaja analítica reside en la consolidación de una única fuente de verdad (Single Source of Truth). Antes de la solución, coordinadores de agencias independientes analizaban planillas aisladas sin conocer la estacionalidad ni la tipología agregada. Al articular el Data Warehouse dimensional, la minería KDD y Power BI, la gerencia dispone de una herramienta unificada para interrogar el comportamiento municipal, evaluar simulaciones de capacidad y justificar decisiones presupuestarias con respaldo empírico.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 7
    # ----------------------------------------------------
    add_heading(doc, "7. Límites metodológicos, supuestos y marco ético-legal", 1, "cap7", 70)
    add_para(doc, "Para garantizar la solidez y transparencia de la entrega ante el tribunal evaluador, esta sección delimita los supuestos técnicos del modelo y enmarca la solución dentro de los estándares legales de gobernanza de datos y ética en inteligencia artificial.")

    add_heading(doc, "Cumplimiento y Marco Ético-Legal de Protección de Datos", 2, "cap7-legal", 71)
    add_para(doc, "El tratamiento de la información de NYC311 se analizó bajo las directrices de la Ley para la Protección de Datos Personales de la República de El Salvador (Decreto Legislativo n.° 144, 2024; referenciada en Lemus et al., 2026c), considerando sus principios fundamentales para el sector público:")
    add_bullets(doc, [
        "Principio de Licitud, Lealtad y Transparencia: Los datos utilizados provienen exclusivamente del portal público NYC Open Data bajo licencia abierta de transparencia gubernamental. No se recolectaron datos privados sin consentimiento.",
        "Principio de Minimización de Datos y Anonimización Espacial: En el modelado dimensional y en los dashboards no se exponen direcciones domiciliarias exactas ni nombres de solicitantes; la información geográfica se agrega a nivel de condado (borough), ciudad y código postal (incident_zip), protegiendo la identidad y privacidad de los ciudadanos.",
        "Principio de No Discriminación y Explicabilidad Algorítmica: El modelo predictivo describe patrones de demoras basados en la tipología del servicio, pero prohíbe taxativamente su uso para penalizar discrecionalmente a colonias o sectores vulnerables. Los modelos no supervisados y supervisados actúan como insumo de diagnóstico, nunca como criterio discriminatorio de inversión.",
        "Supervisión Humana Obligatoria (Human-in-the-Loop): Se establece como regla mandataria que ninguna decisión punitiva hacia el personal de agencias o reasignación de partidas presupuestarias se efectúe de forma autónoma por los algoritmos sin la intervención y criterio experto colegiado.",
    ])

    add_heading(doc, "Matriz de riesgos técnicos y controles recomendados", 2, "cap7-matriz", 72)
    add_table(doc, ["Condición Metodológica", "Riesgo de Interpretación Errónea", "Control y Recomendación Mitigante"], [
        ("Ventana temporal disponible (enero y abril-julio 2026)", "La publicación actual no representa un año completo y sus meses no son contiguos.", "Repetir las cargas ETL incorporando registros anuales completos antes de fijar políticas permanentes."),
        ("Umbral P75 histórico (4,329 min)", "Asumir que 72 horas es una norma universal aplicable a todas las agencias y trámites.", "Fijar umbrales específicos por tipología de reclamo si la agencia cuenta con normativas internas."),
        ("Retención de nulos en duración (63,467 casos actuales)", "Imputar cero a solicitudes abiertas distorsionaría artificialmente a la baja la mediana de atención.", "Conservar NULL y auditar por separado la tasa de resolución como indicador de calidad de gestión."),
        ("Evaluación aleatoria de prueba en el árbol", "El split aleatorio 80/20 no evalúa degradación predictiva a lo largo del tiempo cronológico.", "Ejecutar validación con partición temporal (entrenar en abril-mayo y evaluar en junio-julio)."),
        ("K-Means sobre perfiles y no solicitudes", "Interpretar erróneamente que cada ticket tiene un cluster asignado individualmente.", "Explicar la diferencia entre los 480 perfiles del snapshot F2 y los 481 perfiles de la publicación BI actual; mantener visible 'Sin perfil K-Means'."),
        ("ROI de escenario no observado", "Asumir los porcentajes de retorno financiero como ahorros de caja ya devengados.", "Reportar siempre el ROI como análisis de sensibilidad condicionado a la adopción real de horas."),
    ], [1.7, 2.5, 2.55], font_size=7.7, first_col_bold=True)

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 8
    # ----------------------------------------------------
    add_heading(doc, "8. Conclusiones y recomendaciones estratégicas", 1, "cap8", 80)
    add_para(doc, "La ejecución del proyecto analítico NYC311 para la Fase 3 permite formular las siguientes conclusiones técnicas consolidadas:")
    add_bullets(doc, [
        "1. Integridad total del linaje de datos: Se articuló una cadena de valor que inicia en NYC Open Data, se transforma mediante SSIS bajo los preceptos dimensionales de Kimball, se modela en SQL Server DW_NYC311, se analiza mediante CART y K-Means, y culmina en Power BI y SSAS, conservando el grano de una fila por solicitud. La publicación BI actual verifica 1,312,465 solicitudes sin duplicación.",
        "2. Manejo riguroso de la calidad de datos: Las 63,467 solicitudes actuales sin resolución observada se conservan como NULL, independientes de la métrica de demora alta. Esto evita imputaciones artificiales y mantiene visible la brecha de cierre.",
        "3. Aporte sustantivo de la minería: El árbol conserva sus métricas históricas de prueba (Recall 95.15% y ROC-AUC 0.952) como evidencia del snapshot F2, mientras que la publicación BI actual distingue 481 perfiles frente a los 480 perfiles del snapshot original. En ambos casos, K-Means agrupa perfiles, no solicitudes individuales.",
        "4. Cuadratura y fidelidad visual en Power BI: La vista bi.vw_solicitudes_segmentadas garantiza una relación 1 a 1 sin multiplicación de hechos, incorporando explícitamente las 14,310 solicitudes fuera de perfil para que la gerencia disponga siempre del 100% de la demanda en pantalla.",
        "5. Viabilidad económica condicionada: El modelo financiero fundamentado en Horngren et al. (2012) y Ross et al. (2019) usa CAPEX de US$4,520, OPEX anual de US$4,200 y TCO a 3 años de US$17,120. El ROI base de 162.4% y el payback del mes 14 son escenarios de adopción, no ahorros observados.",
    ])

    add_heading(doc, "Recomendaciones para la implantación futura", 2, "cap8-recom", 81)
    add_bullets(doc, [
        "Priorizar el rediseño de procesos en los 249 perfiles actuales de demora prolongada: establecer mesas técnicas con las dependencias responsables y medir si cambia la mediana observada.",
        "Auditar los protocolos de cierre en los 29 perfiles actuales de rezago crítico: revisar las agencias que concentran casos sin duración y depurar la reportería de estados en el sistema central.",
        "Avanzar hacia una gobernanza Cloud FinOps: En caso de migrar a Microsoft Fabric o Azure, aplicar políticas de auto-pausado, monitoreo de consultas y asignación de costos por agencia para garantizar la sostenibilidad operativa.",
        "Mantener la validación humana en la toma de decisiones: Adoptar las recomendaciones del árbol CART y del panel de control como un instrumento de apoyo y priorización asistida, preservando en todo momento el juicio técnico y ético del servidor público.",
    ])

    doc.add_page_break()

    # ----------------------------------------------------
    # CAPÍTULO 9
    # ----------------------------------------------------
    add_heading(doc, "9. Fuentes consultadas y referencias bibliográficas", 1, "cap9", 90)
    add_para(doc, "Las referencias bibliográficas se presentan organizadas según las normas APA (7.ª edición), integrando las fuentes teóricas, normativas, tecnológicas y los informes previos de la cátedra que sustentan la investigación:")

    referencias_apa = [
        ("Asamblea Legislativa de la República de El Salvador. (2024).", "Ley para la Protección de Datos Personales (Decreto Legislativo n.° 144). Diario Oficial de la República de El Salvador."),
        ("Horngren, C. T., Datar, S. M., & Rajan, M. V. (2012).", "Contabilidad de costos: Un enfoque gerencial (14.ª ed.). Pearson Educación."),
        ("Kimball, R., Reeves, L., Ross, M., & Thornthwaite, W. (1998).", "The data warehouse lifecycle toolkit: Expert methods for designing, developing, and deploying data warehouses. John Wiley & Sons."),
        ("Lemus Mejía, F. J., Bonilla Saz, G. R., Chávez Castillo, E. E., López Ortiz, C. G., & Galdámez Soto, J. J. (2026a).", "Anteproyecto - Fase 1: Data Warehouse y modelo multidimensional de NYC311. Cátedra de Data Warehouse y Minería de Datos (DMD104), Universidad Don Bosco. Repositorio: https://github.com/pgap22/catedra_fase1"),
        ("Lemus Mejía, F. J., Bonilla Saz, G. R., Chávez Castillo, E. E., López Ortiz, C. G., & Galdámez Soto, J. J. (2026b).", "Minería de datos y descubrimiento de conocimiento para NYC311: Informe de Fase 2 con trazabilidad del proceso KDD. Cátedra de Data Warehouse y Minería de Datos (DMD104), Universidad Don Bosco. Repositorio: https://github.com/pgap22/dmd-fase2"),
        ("Lemus Mejía, F. J., Bonilla Saz, G. R., Chávez Castillo, E. E., López Ortiz, C. G., & Galdámez Soto, J. J. (2026c).", "Investigación sobre el ciclo de vida del Data Warehouse, marco CAPEX/OPEX y sostenibilidad FinOps. Cátedra de Data Warehouse y Minería de Datos (DMD104), Universidad Don Bosco."),
        ("Microsoft Learn. (2026a).", "SQL Server Integration Services (SSIS): Documentación oficial y flujos ETL. Microsoft Corporation. https://learn.microsoft.com/sql/integration-services/"),
        ("Microsoft Learn. (2026b).", "Power BI Desktop y Modelo Semántico: Documentación de referencia para DAX, relaciones y optimización VertiPaq. Microsoft Corporation. https://learn.microsoft.com/power-bi/"),
        ("Microsoft. (2026).", "Power BI pricing: Tarifas y planes oficiales para Power BI Pro y Premium por usuario. Microsoft Corporation. Consultado el 25 de octubre de 2026 en: https://www.microsoft.com/power-platform/products/power-bi/pricing"),
        ("NYC Open Data. (2026).", "311 Service Requests from 2020 to Present (dataset erm2-nwe9). Portal Oficial de Datos Abiertos de la Ciudad de Nueva York. https://data.cityofnewyork.us/d/erm2-nwe9"),
        ("Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011).", "Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830."),
        ("Richards, G. (2018).", "Warehouse management: A complete guide to improving efficiency and minimizing costs in the modern warehouse (3rd ed.). Kogan Page."),
        ("Ross, S. A., Westerfield, R. W., & Jordan, B. D. (2019).", "Fundamentals of corporate finance (12th ed.). McGraw-Hill Education."),
        ("Scikit-learn Developers. (2026).", "Decision Trees (CART), K-Means Clustering, and Model Selection (GridSearchCV) documentation. https://scikit-learn.org/stable/"),
        ("Storment, J. R., & Fuller, M. (2020).", "Cloud FinOps: Collaborative, real-time cloud financial management. O'Reilly Media."),
        ("Universidad Don Bosco. (2026).", "Premisa General del Proyecto: Cátedra de Datawarehouse y Minería de Datos (DMD104) - Fase 1, Fase 2 y Fase 3. Escuela de Computación, Facultad de Estudios Tecnológicos."),
    ]

    for autor_anio, detalle in referencias_apa:
        p = doc.add_paragraph(style="Normal")
        set_paragraph_spacing(p, before=1, after=5, line=1.05)
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.75)  # Sangría francesa APA
        r1 = p.add_run(autor_anio + " ")
        set_font(r1, size=9.0, color=BLACK, bold=True)
        r2 = p.add_run(detalle)
        set_font(r2, size=9.0, color=BLACK)

    add_heading(doc, "Nota de reproducibilidad técnica", 2, "cap9-repro", 91)
    add_para(doc, "La validación exhaustiva de los artefactos presentados en este informe puede realizarse directamente en los entornos correspondientes: el proyecto de Data Warehouse y scripts DDL en SQL Server (catedra_fase1), el pipeline KDD en los notebooks reproducibles (dmd-fase2) y el modelo semántico en Power BI Desktop abriendo el archivo oficial NYC311_Fase3_Final.pbix en modo local. La revisión humana final cuenta con la copia en formato PDF (Documento_Fase3.pdf) para verificar la composición editorial y fidelidad visual.", size=9.2, color=GRAY)

    # Configuración de control de viudas y huérfanas en todos los párrafos
    for p in doc.paragraphs:
        if p.style.name == "Normal":
            p.paragraph_format.widow_control = True

    doc.core_properties.title = "Solución analítica integral para NYC311 · Documento final académico Fase 3"
    doc.core_properties.subject = "Data Warehouse, minería de datos KDD y Power BI"
    doc.core_properties.author = "Lemus Mejía, Bonilla Saz, Chávez Castillo, López Ortiz, Galdámez Soto"
    doc.core_properties.keywords = "NYC311, Data Warehouse, Kimball, KDD, K-Means, Decision Tree, Power BI, FinOps, DMD104"

    # Guardar en ambas ubicaciones (en fase-3 y en qa)
    doc.save(OUT_DOCX_QA)
    doc.save(OUT_DOCX_FASE3)
    print(f"DOCX generado con éxito en:\n - {OUT_DOCX_QA}\n - {OUT_DOCX_FASE3}")


if __name__ == "__main__":
    build()
