"""Construye el informe PBIR de Fase 3 y el entregable NYC311_Fase3_Final.pbix.

El modelo semántico conserva la partición SQL hacia DW_NYC311.bi.vw_solicitudes_segmentadas
con 1,293,816 filas, 480 perfiles y 14,024 casos fuera de perfil.
Este script actualiza la capa de presentación con definiciones PBIR versionables
optimizadas para usuarios no técnicos (páginas 16:9, títulos en español con unidades,
cifras exactas, página 3 completa e interactiva con evidencia de minería K-Means, CART y valor operativo).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT if (ROOT / "NYC311_Fase3_Codigo.pbip").is_file() else ROOT / "fuente_pbip"
PROJECT = SOURCE_ROOT / "NYC311_Fase3_Codigo.pbip"
REPORT = SOURCE_ROOT / "NYC311_Fase3_Codigo.Report"
MODEL_TABLE = (
    SOURCE_ROOT
    / "NYC311_Fase3_Codigo.SemanticModel"
    / "definition"
    / "tables"
    / "bi vw_solicitudes_segmentadas.tmdl"
)
ENTITY = "bi vw_solicitudes_segmentadas"
VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/visualContainer/2.14.0/schema.json"
)
PAGE_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/page/2.1.0/schema.json"
)


def stable_id(value: str) -> str:
    return hashlib.sha1(f"nyc311-fase3:{value}".encode("utf-8")).hexdigest()[:20]


def literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def source_ref() -> dict:
    return {"SourceRef": {"Entity": ENTITY}}


def measure_field(name: str) -> dict:
    return {
        "field": {"Measure": {"Expression": source_ref(), "Property": name}},
        "queryRef": f"{ENTITY}.{name}",
        "nativeQueryRef": name,
    }


def column_field(name: str, *, active: bool = True) -> dict:
    return {
        "field": {"Column": {"Expression": source_ref(), "Property": name}},
        "queryRef": f"{ENTITY}.{name}",
        "nativeQueryRef": name,
        "active": active,
    }


def projection(role: str, *fields: dict) -> dict:
    return {role: {"projections": list(fields)}}


def title_object(title: str) -> dict:
    return {
        "title": [
            {
                "properties": {
                    "text": literal(f"'{title}'"),
                    "show": literal("true"),
                }
            }
        ]
    }


def text_runs(text: str, size_px: int, color: str, weight: str = "normal") -> list[dict]:
    return [
        {
            "value": text,
            "textStyle": {
                "fontFamily": "Segoe UI",
                "fontSize": f"{size_px}px",
                "color": color,
                "fontWeight": weight,
            },
        }
    ]


def textbox(
    key: str,
    text: str,
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    size_px: int = 16,
    color: str = "#526477",
    weight: str = "normal",
) -> tuple[str, dict]:
    name = stable_id(key)
    paragraphs = []
    for line in text.split("\n"):
        paragraphs.append(
            {
                "textRuns": text_runs(line, size_px, color, weight),
                "horizontalTextAlignment": "left",
            }
        )
    return name, {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "width": width, "height": height, "z": 1000, "tabOrder": 0},
        "visual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
            "visualContainerObjects": {
                "background": [{"properties": {"show": literal("false")}}],
                "border": [{"properties": {"show": literal("false")}}],
            },
        },
    }


def visual(
    key: str,
    visual_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    state: dict,
    *,
    title: str | None = None,
    objects: dict | None = None,
) -> tuple[str, dict]:
    name = stable_id(key)
    visual_config = {
        "visualType": visual_type,
        "query": {"queryState": state},
        "drillFilterOtherVisuals": True,
    }
    if title:
        visual_config["visualContainerObjects"] = title_object(title)
    if objects:
        visual_config["objects"] = objects
    return name, {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0},
        "visual": visual_config,
    }


def card(key: str, x: int, y: int, width: int, height: int, measure: str) -> tuple[str, dict]:
    return visual(
        key,
        "cardVisual",
        x,
        y,
        width,
        height,
        projection("Data", measure_field(measure)),
        objects={
            "value": [
                {
                    "properties": {
                        "fontSize": literal("28D"),
                        "displayUnits": literal("1D"),
                    },
                    "selector": {"id": "default"},
                }
            ],
            "label": [{"properties": {"fontSize": literal("13D")}, "selector": {"id": "default"}}],
        },
    )


def slicer(key: str, x: int, y: int, width: int, field: str, title: str) -> tuple[str, dict]:
    return visual(key, "slicer", x, y, width, 78, projection("Values", column_field(field)), title=title)


def chart(
    key: str,
    visual_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    category: str,
    measure: str,
    title: str,
    *,
    series: str | None = None,
) -> tuple[str, dict]:
    state = projection("Category", column_field(category))
    if series:
        state.update(projection("Series", column_field(series)))
    state.update(projection("Y", measure_field(measure)))
    return visual(key, visual_type, x, y, width, height, state, title=title)


def map_visual(
    key: str,
    x: int,
    y: int,
    width: int,
    height: int,
    location_field: str,
    size_measure: str,
    title: str,
) -> tuple[str, dict]:
    state = {
        "Category": {"projections": [column_field(location_field)]},
        "Size": {"projections": [measure_field(size_measure)]},
    }
    return visual(key, "map", x, y, width, height, state, title=title)


def build_page(page_key: str, display_name: str) -> tuple[dict, list[tuple[str, dict]]]:
    page = {
        "$schema": PAGE_SCHEMA,
        "name": page_key,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
    }
    return page, []


def page_panorama() -> tuple[dict, list[tuple[str, dict]]]:
    page, visuals = build_page(stable_id("page-panorama"), "Panorama ciudadano")
    visuals.extend(
        [
            textbox(
                "p1-title",
                "NYC311 | Panorama de atención ciudadana",
                32, 24, 1500, 44,
                size_px=30, color="#12304A", weight="bold"
            ),
            textbox(
                "p1-subtitle",
                "Volumen, tiempos observados y distribución de solicitudes · Datos oficiales abril–julio 2026 (1,293,816 solicitudes analizadas).",
                34, 72, 1800, 30
            ),
            slicer("p1-borough", 32, 118, 250, "borough", "Distrito (Borough)"),
            slicer("p1-agency", 298, 118, 250, "agency", "Agencia ejecutora"),
            slicer("p1-cluster", 564, 118, 350, "cluster_nombre", "Clúster K-Means (480 perfiles)"),
            slicer("p1-status", 930, 118, 250, "status", "Estado de solicitud"),
            *[
                card("p1-card-requests", 32, 210, 430, 118, "Solicitudes distintas"),
                card("p1-card-median", 482, 210, 430, 118, "Mediana minutos observados"),
                card("p1-card-delay", 932, 210, 430, 118, "Solicitudes con demora alta"),
                card("p1-card-null", 1382, 210, 506, 118, "Solicitudes sin duración"),
            ],
            chart(
                "p1-month",
                "clusteredColumnChart",
                32, 350, 660, 690,
                "mes",
                "Solicitudes distintas",
                "Tendencia mensual de solicitudes · recuento (abril–julio 2026)",
                series="anio",
            ),
            chart(
                "p1-borough-chart",
                "clusteredBarChart",
                712, 350, 580, 690,
                "borough",
                "Solicitudes distintas",
                "Carga de solicitudes por distrito (borough) · recuento",
            ),
            map_visual(
                "p1-map",
                1312, 350, 576, 690,
                "borough",
                "Solicitudes distintas",
                "Distribución geoespacial por distrito (borough) · recuento",
            ),
        ]
    )
    return page, visuals


def page_diagnostico() -> tuple[dict, list[tuple[str, dict]]]:
    page, visuals = build_page(stable_id("page-diagnostico"), "Dónde concentrar capacidad")
    visuals.extend(
        [
            textbox(
                "p2-title",
                "NYC311 | Dónde concentrar capacidad y respuesta operativa",
                32, 24, 1500, 44,
                size_px=30, color="#12304A", weight="bold"
            ),
            textbox(
                "p2-subtitle",
                "Diagnóstico operativo de tiempos de atención por agencia y distrito. Duraciones no observadas (63,079 casos) preservadas sin sesgo analítico.",
                34, 72, 1820, 36
            ),
            slicer("p2-agency", 32, 122, 290, "agency", "Agencia ejecutora"),
            slicer("p2-borough", 338, 122, 290, "borough", "Distrito (Borough)"),
            slicer("p2-cluster", 644, 122, 340, "cluster_nombre", "Clúster K-Means (480 perfiles)"),
            slicer("p2-channel", 1000, 122, 290, "open_data_channel_type", "Canal de entrada"),
            chart(
                "p2-agency-delay",
                "clusteredBarChart",
                32, 220, 900, 390,
                "agency",
                "Mediana minutos observados",
                "Mediana observada por agencia · minutos de resolución",
            ),
            chart(
                "p2-borough-delay",
                "clusteredColumnChart",
                952, 220, 936, 390,
                "borough",
                "Mediana minutos observados",
                "Mediana observada por distrito (borough) · minutos de resolución",
            ),
            chart(
                "p2-channel-vol",
                "clusteredColumnChart",
                32, 630, 900, 360,
                "open_data_channel_type",
                "Solicitudes distintas",
                "Solicitudes por canal de entrada · recuento",
            ),
            chart(
                "p2-status",
                "clusteredBarChart",
                952, 630, 936, 360,
                "status",
                "Solicitudes distintas",
                "Solicitudes por estado operativo · recuento",
            ),
            textbox(
                "p2-note",
                "Regla analítica: La mediana excluye casos sin duración observada (63,079 solicitudes preservadas como NULL). El umbral P75 histórico (4,329 min ≈ 3.0 días) clasifica demora alta pero no constituye un SLA contractual. Utilice el segmentador de clúster para aislar perfiles de rezago crítico.",
                32, 1005, 1856, 55,
                size_px=13
            ),
        ]
    )
    return page, visuals


def page_valor() -> tuple[dict, list[tuple[str, dict]]]:
    page, visuals = build_page(stable_id("page-valor"), "Segmentación y valor operativo")
    visuals.extend(
        [
            textbox(
                "p3-title",
                "NYC311 | Segmentación de Minería e Impacto de Gestión",
                32, 24, 1700, 44,
                size_px=30, color="#12304A", weight="bold"
            ),
            textbox(
                "p3-subtitle",
                "Integración operativa de los 480 perfiles K-Means y reglas del Árbol CART para priorizar capacidad y mejorar el servicio ciudadano.",
                34, 72, 1820, 30,
                size_px=15
            ),
            slicer("p3-cluster", 32, 118, 380, "cluster_nombre", "Clúster K-Means (480 perfiles)"),
            slicer("p3-borough", 432, 118, 280, "borough", "Distrito (Borough)"),
            slicer("p3-agency", 732, 118, 280, "agency", "Agencia ejecutora"),
            *[
                card("p3-card-requests", 32, 210, 430, 118, "Solicitudes distintas"),
                card("p3-card-median", 482, 210, 430, 118, "Mediana minutos observados"),
                card("p3-card-delay", 932, 210, 430, 118, "Solicitudes con demora alta"),
                card("p3-card-outside", 1382, 210, 506, 118, "Solicitudes fuera de perfil"),
            ],
            chart(
                "p3-cluster-vol",
                "clusteredBarChart",
                32, 348, 890, 370,
                "cluster_nombre",
                "Solicitudes distintas",
                "Volumen de solicitudes por Clúster K-Means · recuento",
            ),
            chart(
                "p3-cluster-median",
                "clusteredColumnChart",
                942, 348, 946, 370,
                "cluster_nombre",
                "Mediana minutos observados",
                "Mediana de resolución por Clúster K-Means · minutos observados",
            ),
            textbox(
                "p3-tree-box",
                "PRIORIZACIÓN TEMPRANA (ÁRBOL CART)\n\n• Objetivo operativo: Detectar tempranamente solicitudes con alto riesgo de demora al momento de ingreso.\n• Precisión histórica en prueba: Recall 95.15% (detección de demora alta) | ROC-AUC: 0.952 | F1: 78.37%.\n• Factores de alerta: Agencia ejecutora, tipo de queja, distrito, canal y día/mes de recepción.\n• Matriz de prueba: 58,549 demoras detectadas oportunamente vs. 2,982 falsos negativos.\n• Uso práctico: Semáforo preventivo en mesa de entrada para asignación prioritaria de cuadrillas.",
                32, 738, 590, 310,
                size_px=15, color="#12304A"
            ),
            textbox(
                "p3-kmeans-box",
                "SEGMENTACIÓN DE CASOS (K-MEANS)\n\n• Población modelada: 480 perfiles de alta recurrencia (>= 100 casos) agrupados por agencia, tipo y distrito.\n• Clúster 1 — Resolución ágil: 899,050 casos (69.5%), mediana 129 min (~2.1 h). Flujo estándar continuo.\n• Clúster 2 — Resolución prolongada: 351,275 casos (27.2%), mediana 11,354 min (~7.9 días).\n• Clúster 3 — Rezago crítico: 29,467 casos (2.3%), mediana 20,522 min (~14.2 días), 82.7% sin resolver.\n• Integridad de datos: 14,024 solicitudes (1.08%) fuera de perfil K-Means conservadas explícitamente.",
                642, 738, 590, 310,
                size_px=15, color="#12304A"
            ),
            textbox(
                "p3-roi-box",
                "VALOR OPERATIVO: CAPACIDAD Y SERVICIO\n\n• Ahorro de horas de analistas y supervisores: escenario base de 16 h/semana.\n• Menos contactos repetidos y solicitudes mal priorizadas mediante alerta preventiva.\n• Mejor distribución de cuadrillas y horas extra al localizar rezagos por distrito, agencia y canal.\n• Menor tiempo de resolución y backlog: la métrica se monitorea; no se presenta como causalidad probada.\n• Mayor transparencia y equidad entre boroughs; atención más rápida y mejor acceso ciudadano.\n\nEscenario económico auxiliar: 14,976 USD/año de beneficio estimado; costo conocido a 3 años de 12,120 USD (4,200 iniciales + 2,640 USD/año). El ROI base de 270.7% y el equilibrio aproximado en el mes 10 son supuestos, no una ganancia garantizada.",
                1252, 738, 636, 310,
                size_px=13, color="#12304A"
            ),
        ]
    )
    return page, visuals


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_measure_definitions() -> None:
    text = MODEL_TABLE.read_text(encoding="utf-8")
    marker = "\n\tpartition 'bi vw_solicitudes_segmentadas' = m\n"
    if marker not in text:
        raise RuntimeError("No se encontró la partición de la vista SQL para insertar medidas.")

    prefix = text.split(marker)[0]
    suffix = marker + text.split(marker)[1]

    lines = prefix.splitlines()
    clean_lines = []
    skip = False
    for line in lines:
        if line.strip().startswith("measure "):
            skip = True
            continue
        if skip and (line.strip().startswith("column ") or line.strip().startswith("annotation ")):
            skip = False
        if not skip:
            clean_lines.append(line)

    clean_prefix = "\n".join(clean_lines).rstrip() + "\n"

    measures = """
\tmeasure 'Solicitudes distintas' = DISTINCTCOUNT('bi vw_solicitudes_segmentadas'[codigo_solicitud])
\t\tformatString: #,##0

\tmeasure 'Solicitudes con tiempo' = CALCULATE([Solicitudes distintas], NOT ISBLANK('bi vw_solicitudes_segmentadas'[minutos_resolucion]))
\t\tformatString: #,##0

\tmeasure 'Solicitudes sin duración' = CALCULATE([Solicitudes distintas], ISBLANK('bi vw_solicitudes_segmentadas'[minutos_resolucion]))
\t\tformatString: #,##0

\tmeasure 'Solicitudes con demora alta' = COALESCE(SUM('bi vw_solicitudes_segmentadas'[demora_alta]), 0)
\t\tformatString: #,##0

\tmeasure 'Tasa demora alta' = DIVIDE([Solicitudes con demora alta], [Solicitudes con tiempo])
\t\tformatString: 0.0%

\tmeasure 'Mediana minutos observados' = MEDIAN('bi vw_solicitudes_segmentadas'[minutos_resolucion])
\t\tformatString: #,##0

\tmeasure 'Solicitudes segmentadas' = CALCULATE([Solicitudes distintas], 'bi vw_solicitudes_segmentadas'[es_segmentado] = TRUE)
\t\tformatString: #,##0

\tmeasure 'Solicitudes fuera de perfil' = CALCULATE([Solicitudes distintas], 'bi vw_solicitudes_segmentadas'[es_segmentado] = FALSE)
\t\tformatString: #,##0

\tmeasure 'Porcentaje segmentado' = DIVIDE([Solicitudes segmentadas], [Solicitudes distintas])
\t\tformatString: 0.0%
"""
    MODEL_TABLE.write_text(clean_prefix + measures + suffix, encoding="utf-8")


def write_page(page: dict, visuals: list[tuple[str, dict]]) -> None:
    page_dir = REPORT / "definition" / "pages" / page["name"]
    visuals_dir = page_dir / "visuals"
    page_dir.mkdir(parents=True, exist_ok=True)
    write_json(page_dir / "page.json", page)
    visuals_dir.mkdir(parents=True, exist_ok=True)
    for child in list(visuals_dir.iterdir()):
        if child.is_dir():
            shutil.rmtree(child)
    for name, definition in visuals:
        write_json(visuals_dir / name / "visual.json", definition)


def package_final_pbix() -> Path:
    source_pbix = ROOT / "NYC311_Fase3_Actualizado.pbix"
    if not source_pbix.is_file():
        source_pbix = ROOT / "NYC311_Fase3_Codigo.pbix"
    target_pbix = ROOT / "NYC311_Fase3_Final.pbix"

    report_def_dir = REPORT / "definition"
    files_to_inject: dict[str, bytes] = {}
    for p in report_def_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(REPORT).as_posix()
            files_to_inject[f"Report/{rel}"] = p.read_bytes()

    with zipfile.ZipFile(source_pbix, "r") as src, zipfile.ZipFile(target_pbix, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            filename = item.filename
            if filename.startswith("Report/definition/"):
                continue
            dst.writestr(item, src.read(filename))

        for injected_name, data in sorted(files_to_inject.items()):
            dst.writestr(injected_name, data)

    print(f"PBIX final generado: {target_pbix} ({target_pbix.stat().st_size:,} bytes)")
    return target_pbix


def build() -> None:
    if not PROJECT.is_file() or not REPORT.is_dir() or not MODEL_TABLE.is_file():
        raise FileNotFoundError("El proyecto PBIP exportado por Power BI Desktop no está completo.")

    backup = ROOT.parent.parent / "tmp" / "NYC311_Fase3_Codigo_before_code_build"
    if not backup.exists():
        backup.mkdir(parents=True)
        shutil.copytree(REPORT, backup / REPORT.name)
        shutil.copy2(MODEL_TABLE, backup / MODEL_TABLE.name)

    write_measure_definitions()
    page_builders = [page_panorama, page_diagnostico, page_valor]
    pages = []
    for builder in page_builders:
        page, visuals = builder()
        write_page(page, visuals)
        pages.append(page)

    pages_root = REPORT / "definition" / "pages"
    keep = {p["name"] for p in pages}
    for old_dir in pages_root.iterdir():
        if old_dir.is_dir() and old_dir.name not in keep:
            shutil.rmtree(old_dir)
    write_json(
        pages_root / "pages.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
            "pageOrder": [p["name"] for p in pages],
            "activePageName": pages[0]["name"],
        },
    )
    print(f"PBIR construido: {len(pages)} páginas, {sum(len(builder()[1]) for builder in page_builders)} visuales.")
    print(f"Proyecto: {PROJECT}")

    final_pbix = package_final_pbix()
    print(f"Entrega ejecutable: {final_pbix}")


if __name__ == "__main__":
    build()
