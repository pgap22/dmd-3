"""Construye el informe PBIR de Fase 3 y el entregable NYC311_Fase3_Final.pbix.

El modelo semántico consume SQL Server DW_NYC311.bi.vw_solicitudes_segmentadas.
Este script implementa mejoras reales y trazables en la capa de presentación y modelo:
- Selector de fechas basado en la fecha del modelo sin filtro fijo abril-julio en la página demo.
- Segmentadores con mayor altura (105px) y distribución completa en ancho 16:9.
- Jerarquía de fecha usable (Año -> Mes) y columnas de fecha/mes formateadas.
- KPIs y gráficos responsivos dinámicamente a rangos temporales y dimensiones.
- Corrección de tarjetas vacías/0 mediante COALESCE, tipos de proyección limpios y codificación UTF-8 estricta.
- Mantiene Power BI nativo, proporción 16:9 (1920x1080) y 3 páginas ejecutivas.
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
    # cardVisual nativo con proyeccion directa y medidas protegidas con COALESCE
    return visual(
        key,
        "cardVisual",
        x,
        y,
        width,
        height,
        projection("Data", measure_field(measure)),
    )


def slicer(
    key: str,
    x: int,
    y: int,
    width: int,
    height: int,
    field: str,
    title: str,
    *,
    objects: dict | None = None,
) -> tuple[str, dict]:
    return visual(
        key,
        "slicer",
        x,
        y,
        width,
        height,
        projection("Values", column_field(field)),
        title=title,
        objects=objects,
    )


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
                32, 20, 1500, 40,
                size_px=28, color="#12304A", weight="bold"
            ),
            textbox(
                "p1-subtitle",
                "Volumen, tiempos observados y distribución de solicitudes · Análisis interactivo por período y dimensiones operativas.",
                34, 62, 1800, 26,
                size_px=14, color="#526477"
            ),
            # Barra de segmentadores con 105px de alto y espacio ampliado
            slicer("p1-fecha", 32, 95, 345, 105, "fecha", "Período (Fecha)"),
            slicer("p1-borough", 397, 95, 345, 105, "borough", "Distrito (Borough)"),
            slicer("p1-agency", 762, 95, 345, 105, "agency", "Agencia ejecutora"),
            slicer("p1-cluster", 1127, 95, 400, 105, "cluster_nombre", "Clúster K-Means (481 perfiles)"),
            slicer("p1-status", 1547, 95, 341, 105, "status", "Estado de solicitud"),
            # Fila de 4 KPIs
            card("p1-card-requests", 32, 215, 449, 115, "Solicitudes distintas"),
            card("p1-card-median", 501, 215, 449, 115, "Mediana minutos observados"),
            card("p1-card-delay", 970, 215, 449, 115, "Solicitudes con demora alta"),
            card("p1-card-null", 1439, 215, 449, 115, "Solicitudes sin duración"),
            # Visuales principales (sin filtro fijo hardcodeado en títulos)
            chart(
                "p1-month",
                "clusteredColumnChart",
                32, 345, 640, 700,
                "nombre_mes",
                "Solicitudes distintas",
                "Tendencia mensual de solicitudes · recuento",
                series="anio",
            ),
            chart(
                "p1-borough-chart",
                "clusteredBarChart",
                692, 345, 590, 700,
                "borough",
                "Solicitudes distintas",
                "Carga de solicitudes por distrito (borough) · recuento",
            ),
            map_visual(
                "p1-map",
                1302, 345, 586, 700,
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
                32, 20, 1500, 40,
                size_px=28, color="#12304A", weight="bold"
            ),
            textbox(
                "p2-subtitle",
                "Diagnóstico operativo de tiempos de atención por agencia y distrito. Duraciones no observadas preservadas sin sesgo analítico.",
                34, 62, 1820, 26,
                size_px=14, color="#526477"
            ),
            # Barra de segmentadores con 105px de alto
            slicer("p2-fecha", 32, 95, 345, 105, "fecha", "Período (Fecha)"),
            slicer("p2-agency", 397, 95, 345, 105, "agency", "Agencia ejecutora"),
            slicer("p2-borough", 762, 95, 345, 105, "borough", "Distrito (Borough)"),
            slicer("p2-cluster", 1127, 95, 400, 105, "cluster_nombre", "Clúster K-Means (481 perfiles)"),
            slicer("p2-channel", 1547, 95, 341, 105, "open_data_channel_type", "Canal de entrada"),
            # Gráficos fila superior (y=215, height=375)
            chart(
                "p2-agency-delay",
                "clusteredBarChart",
                32, 215, 908, 375,
                "agency",
                "Mediana minutos observados",
                "Mediana observada por agencia · minutos de resolución",
            ),
            chart(
                "p2-borough-delay",
                "clusteredColumnChart",
                960, 215, 928, 375,
                "borough",
                "Mediana minutos observados",
                "Mediana observada por distrito (borough) · minutos de resolución",
            ),
            # Gráficos fila inferior (y=605, height=375)
            chart(
                "p2-channel-vol",
                "clusteredColumnChart",
                32, 605, 908, 375,
                "open_data_channel_type",
                "Solicitudes distintas",
                "Solicitudes por canal de entrada · recuento",
            ),
            chart(
                "p2-status",
                "clusteredBarChart",
                960, 605, 928, 375,
                "status",
                "Solicitudes distintas",
                "Solicitudes por estado operativo · recuento",
            ),
            textbox(
                "p2-note",
                "Regla analítica: La mediana excluye casos sin duración observada (preservadas como NULL). El umbral P75 histórico (4,329 min ≈ 3.0 días) clasifica demora alta pero no constituye un SLA contractual. Utilice el segmentador de clúster para aislar perfiles de rezago crítico.",
                32, 995, 1856, 55,
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
                32, 20, 1700, 40,
                size_px=28, color="#12304A", weight="bold"
            ),
            textbox(
                "p3-subtitle",
                "Integración operativa de los 481 perfiles K-Means y reglas del Árbol CART para priorizar capacidad y mejorar el servicio ciudadano.",
                34, 62, 1820, 26,
                size_px=14, color="#526477"
            ),
            # Barra de segmentadores con 105px de alto
            slicer("p3-fecha", 32, 95, 345, 105, "fecha", "Período (Fecha)"),
            slicer("p3-cluster", 397, 95, 420, 105, "cluster_nombre", "Clúster K-Means (481 perfiles)"),
            slicer("p3-borough", 837, 95, 330, 105, "borough", "Distrito (Borough)"),
            slicer("p3-agency", 1187, 95, 330, 105, "agency", "Agencia ejecutora"),
            slicer("p3-channel", 1537, 95, 351, 105, "open_data_channel_type", "Canal de entrada"),
            # Fila de 4 KPIs
            card("p3-card-requests", 32, 215, 449, 115, "Solicitudes distintas"),
            card("p3-card-median", 501, 215, 449, 115, "Mediana minutos observados"),
            card("p3-card-delay", 970, 215, 449, 115, "Solicitudes con demora alta"),
            card("p3-card-outside", 1439, 215, 449, 115, "Solicitudes fuera de perfil"),
            # Gráficos fila media (y=345, height=365)
            chart(
                "p3-cluster-vol",
                "clusteredBarChart",
                32, 345, 908, 365,
                "cluster_nombre",
                "Solicitudes distintas",
                "Volumen de solicitudes por Clúster K-Means · recuento",
            ),
            chart(
                "p3-cluster-median",
                "clusteredColumnChart",
                960, 345, 928, 365,
                "cluster_nombre",
                "Mediana minutos observados",
                "Mediana de resolución por Clúster K-Means · minutos observados",
            ),
            # Cajas de impacto y evidencia metodológica (y=725, height=325)
            textbox(
                "p3-tree-box",
                "PRIORIZACIÓN TEMPRANA (ÁRBOL CART)\n\n• Objetivo operativo: Detectar tempranamente solicitudes con alto riesgo de demora al momento de ingreso.\n• Referencia del experimento F2 original (prueba abril–julio 2026): Recall 95.15% | ROC-AUC: 0.952 | F1: 78.37%.\n• Factores de alerta: Agencia ejecutora, tipo de queja, distrito, canal y día/mes de recepción.\n• Matriz de prueba histórica: 58,549 demoras detectadas oportunamente vs. 2,982 falsos negativos.\n• Uso práctico: Semáforo preventivo en mesa de entrada para asignación prioritaria de cuadrillas; no es una predicción dinámica del slicer.",
                32, 725, 590, 325,
                size_px=14, color="#12304A"
            ),
            textbox(
                "p3-kmeans-box",
                "SEGMENTACIÓN DE CASOS (K-MEANS)\n\n• Población modelada: 481 perfiles de alta recurrencia (>= 100 casos) agrupados por agencia, tipo y distrito, sobre el rango disponible enero–julio de 2026.\n• Clúster 1 — Resolución ágil: 910,529 casos (69.4%), mediana 129 min (~2.2 h). Flujo estándar continuo.\n• Clúster 2 — Resolución prolongada: 358,005 casos (27.3%), mediana 11,241 min (~7.8 días).\n• Clúster 3 — Rezago crítico: 29,621 casos (2.3%), mediana 21,277 min (~14.8 días), 81.7% sin duración observada.\n• Integridad de datos: 14,310 solicitudes (1.09%) fuera de perfil K-Means conservadas explícitamente.",
                642, 725, 590, 325,
                size_px=14, color="#12304A"
            ),
            textbox(
                "p3-roi-box",
                "VALOR OPERATIVO: CAPACIDAD Y SERVICIO\n\n• Ahorro de horas de analistas y supervisores: escenario base de 16 h/semana.\n• Menos contactos repetidos y solicitudes mal priorizadas mediante alerta preventiva.\n• Mejor distribución de cuadrillas y horas extra al localizar rezagos por distrito, agencia y canal.\n• Menor tiempo de resolución y backlog: la métrica se monitorea; no se presenta como causalidad probada.\n• Mayor transparencia y equidad entre boroughs; atención más rápida y mejor acceso ciudadano.\n\nEscenario económico auxiliar: 14,976 USD/año de beneficio estimado; costo conocido a 3 años de 12,120 USD (4,200 iniciales + 2,640 USD/año). El ROI base de 270.7% y el equilibrio aproximado en el mes 10 son supuestos, no una ganancia garantizada.",
                1252, 725, 636, 325,
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

    # Normalizar columnas no aditivas para que no sumen anio/mes/codigo por defecto
    for col_to_fix in ["codigo_solicitud", "anio", "mes", "dia_semana", "demora_alta", "cluster_id_original"]:
        old_block = f"\tcolumn {col_to_fix}\n\t\tdataType: int64\n\t\tformatString: 0\n\t\tlineageTag:"
        # replace summarizeBy: sum inside this block
        # We can do line-based replacement safely
        pass

    lines = prefix.splitlines()
    clean_lines = []
    skip = False
    in_target_column = False

    for line in lines:
        stripped = line.strip()
        # Omitir medidas o columnas calculadas previas que seran reinyectadas
        if stripped.startswith("measure "):
            skip = True
            continue
        if stripped.startswith("column fecha =") or stripped.startswith("column nombre_mes ="):
            skip = True
            continue
        if stripped.startswith("hierarchy 'Jerarquía de fechas'") or stripped.startswith("hierarchy 'Jerarquia de fechas'"):
            skip = True
            continue
        if skip and (stripped.startswith("column ") or stripped.startswith("annotation ") or stripped.startswith("hierarchy ")):
            # Check if this new column/hierarchy is also one to skip
            if stripped.startswith("column fecha =") or stripped.startswith("column nombre_mes =") or stripped.startswith("hierarchy "):
                continue
            skip = False

        if not skip:
            # Corregir summarizeBy: sum a summarizeBy: none en columnas no aditivas
            if any(stripped == f"column {c}" for c in ["codigo_solicitud", "anio", "mes", "dia_semana", "demora_alta", "cluster_id_original"]):
                in_target_column = True
            elif stripped.startswith("column "):
                in_target_column = False

            if in_target_column and stripped == "summarizeBy: sum":
                clean_lines.append(line.replace("summarizeBy: sum", "summarizeBy: none"))
            else:
                clean_lines.append(line)

    clean_prefix = "\n".join(clean_lines).rstrip() + "\n"

    calculated_components = """
\tcolumn fecha = DATE('bi vw_solicitudes_segmentadas'[anio], 'bi vw_solicitudes_segmentadas'[mes], 1)
\t\tdataType: dateTime
\t\tformatString: yyyy-mm
\t\tlineageTag: a38b8123-579c-48b4-82ab-001122334455
\t\tsummarizeBy: none

\t\tannotation SummarizationSetBy = Automatic

\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn nombre_mes = FORMAT(DATE('bi vw_solicitudes_segmentadas'[anio], 'bi vw_solicitudes_segmentadas'[mes], 1), "MMMM")
\t\tdataType: string
\t\tlineageTag: 5c3d2e4f-6a7b-8c9d-0e1f-2a3b4c5d6e7f
\t\tsummarizeBy: none
\t\tsortByColumn: mes

\t\tannotation SummarizationSetBy = Automatic

\thierarchy 'Jerarquía de fechas'
\t\tlineageTag: 6d4e3f5a-7b8c-9d0e-1f2a-3b4c5d6e7f8a

\t\tlevel Año
\t\t\tlineageTag: 7e5f4a6b-8c9d-0e1f-2a3b-4c5d6e7f8a9b
\t\t\tcolumn: anio

\t\tlevel Mes
\t\t\tlineageTag: 8f6a5b7c-9d0e-1f2a-3b4c-5d6e7f8a9b0c
\t\t\tcolumn: nombre_mes

\tmeasure 'Solicitudes distintas' = COALESCE(DISTINCTCOUNT('bi vw_solicitudes_segmentadas'[codigo_solicitud]), 0)
\t\tformatString: #,##0

\tmeasure 'Solicitudes con tiempo' = COALESCE(CALCULATE([Solicitudes distintas], NOT ISBLANK('bi vw_solicitudes_segmentadas'[minutos_resolucion])), 0)
\t\tformatString: #,##0

\tmeasure 'Solicitudes sin duración' = COALESCE(CALCULATE([Solicitudes distintas], ISBLANK('bi vw_solicitudes_segmentadas'[minutos_resolucion])), 0)
\t\tformatString: #,##0

\tmeasure 'Solicitudes con demora alta' = COALESCE(CALCULATE([Solicitudes distintas], 'bi vw_solicitudes_segmentadas'[demora_alta] = 1), 0)
\t\tformatString: #,##0

\tmeasure 'Tasa demora alta' = DIVIDE([Solicitudes con demora alta], [Solicitudes con tiempo], 0.0)
\t\tformatString: 0.0%

\tmeasure 'Mediana minutos observados' = MEDIAN('bi vw_solicitudes_segmentadas'[minutos_resolucion])
\t\tformatString: #,##0

\tmeasure 'Solicitudes segmentadas' = COALESCE(CALCULATE([Solicitudes distintas], 'bi vw_solicitudes_segmentadas'[es_segmentado] = TRUE), 0)
\t\tformatString: #,##0

\tmeasure 'Solicitudes fuera de perfil' = COALESCE(CALCULATE([Solicitudes distintas], 'bi vw_solicitudes_segmentadas'[es_segmentado] = FALSE), 0)
\t\tformatString: #,##0

\tmeasure 'Porcentaje segmentado' = DIVIDE([Solicitudes segmentadas], [Solicitudes distintas], 0.0)
\t\tformatString: 0.0%
"""
    MODEL_TABLE.write_text(clean_prefix + calculated_components + suffix, encoding="utf-8")
    print(f"Modelo TMDL actualizado con fecha calculada, jerarquía y medidas DAX robustas: {MODEL_TABLE}")


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
    candidates = [
        ROOT / "NYC311_Fase3_Actualizado.pbix",
        ROOT / "NYC311_Fase3_Final.pbix",
        ROOT / "NYC311_Fase3_Codigo.pbix",
        ROOT.parent.parent.parent / "entrega" / "BI" / "NYC311_Fase3_Actualizado.pbix",
        ROOT.parent.parent.parent / "entrega" / "BI" / "NYC311_Fase3_Final.pbix",
    ]
    source_pbix = None
    for c in candidates:
        if c.is_file():
            source_pbix = c
            break

    if not source_pbix:
        raise FileNotFoundError("No se encontró ningún archivo PBIX base con DataModel para empaquetar.")

    target_pbix = ROOT / "NYC311_Fase3_Final.pbix"
    tmp_target = ROOT / "NYC311_Fase3_Final.tmp.pbix"

    report_def_dir = REPORT / "definition"
    files_to_inject: dict[str, bytes] = {}
    for p in report_def_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(REPORT).as_posix()
            files_to_inject[f"Report/{rel}"] = p.read_bytes()

    with zipfile.ZipFile(source_pbix, "r") as src, zipfile.ZipFile(tmp_target, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            filename = item.filename
            if filename.startswith("Report/definition/"):
                continue
            dst.writestr(item, src.read(filename))

        for injected_name, data in sorted(files_to_inject.items()):
            dst.writestr(injected_name, data)

    if target_pbix.is_file():
        target_pbix.unlink()
    tmp_target.rename(target_pbix)

    print(f"PBIX final generado: {target_pbix} ({target_pbix.stat().st_size:,} bytes)")

    # Sincronizar tambien a entrega/BI si existe
    entrega_pbix = ROOT.parent.parent.parent / "entrega" / "BI" / "NYC311_Fase3_Final.pbix"
    if entrega_pbix.parent.is_dir():
        shutil.copy2(target_pbix, entrega_pbix)
        print(f"Copia sincronizada en entrega: {entrega_pbix}")

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
