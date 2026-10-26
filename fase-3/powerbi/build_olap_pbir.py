"""Construye las páginas PBIR del informe Live conectado al cubo SSAS NYC311.

El modelo semántico de este proyecto es el cubo multidimensional CuboFase1 / DW NYC311.
Por eso el reporte usa únicamente medidas y atributos publicados por el cubo; no agrega
DAX local ni presenta agregaciones de tiempo que el cubo no expone como medida calculada.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PBIP = ROOT / "fuente_pbip" / "olap.pbip"
REPORT = ROOT / "fuente_pbip" / "olap.Report"
VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/visualContainer/2.14.0/schema.json"
)
PAGE_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/page/2.1.0/schema.json"
)


def stable_id(value: str) -> str:
    return hashlib.sha1(f"nyc311-olap:{value}".encode("utf-8")).hexdigest()[:20]


def literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def source_ref(entity: str) -> dict:
    return {"SourceRef": {"Entity": entity}}


def measure_field(entity: str, name: str) -> dict:
    return {
        "field": {"Measure": {"Expression": source_ref(entity), "Property": name}},
        "queryRef": f"{entity}.{name}",
        "nativeQueryRef": name,
    }


def column_field(entity: str, name: str) -> dict:
    return {
        "field": {"Column": {"Expression": source_ref(entity), "Property": name}},
        "queryRef": f"{entity}.{name}",
        "nativeQueryRef": name,
        "active": True,
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
    paragraphs = [
        {
            "textRuns": text_runs(line, size_px, color, weight),
            "horizontalTextAlignment": "left",
        }
        for line in text.split("\n")
    ]
    name = stable_id(key)
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
) -> tuple[str, dict]:
    name = stable_id(key)
    visual_config = {
        "visualType": visual_type,
        "query": {"queryState": state},
        "drillFilterOtherVisuals": True,
    }
    if title:
        visual_config["visualContainerObjects"] = title_object(title)
    return name, {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "width": width, "height": height, "z": 0, "tabOrder": 0},
        "visual": visual_config,
    }


def card(
    key: str,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    *,
    measure: str = "Fact Solicitud Count",
) -> tuple[str, dict]:
    return visual(
        key,
        "cardVisual",
        x,
        y,
        width,
        height,
        projection("Data", measure_field("Fact Solicitud", measure)),
        title=title,
    )


def slicer(
    key: str,
    x: int,
    y: int,
    width: int,
    height: int,
    entity: str,
    field: str,
    title: str,
) -> tuple[str, dict]:
    return visual(
        key,
        "slicer",
        x,
        y,
        width,
        height,
        projection("Values", column_field(entity, field)),
        title=title,
    )


def chart(
    key: str,
    visual_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    category_entity: str,
    category: str,
    title: str,
) -> tuple[str, dict]:
    state = projection("Category", column_field(category_entity, category))
    state.update(projection("Y", measure_field("Fact Solicitud", "Fact Solicitud Count")))
    return visual(key, visual_type, x, y, width, height, state, title=title)


def category_hierarchy_chart(
    key: str,
    visual_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    entity: str,
    levels: tuple[str, ...],
    title: str,
) -> tuple[str, dict]:
    """Eje multinivel compatible con el report schema de Desktop Store."""
    state = projection("Category", *(column_field(entity, level) for level in levels))
    state.update(projection("Y", measure_field("Fact Solicitud", "Fact Solicitud Count")))
    return visual(key, visual_type, x, y, width, height, state, title=title)


def page(key: str, display_name: str) -> dict:
    return {
        "$schema": PAGE_SCHEMA,
        "name": key,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_page(page_definition: dict, visuals: list[tuple[str, dict]]) -> None:
    page_dir = REPORT / "definition" / "pages" / page_definition["name"]
    visuals_dir = page_dir / "visuals"
    page_dir.mkdir(parents=True, exist_ok=True)
    write_json(page_dir / "page.json", page_definition)
    if visuals_dir.exists():
        for child in visuals_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    visuals_dir.mkdir(parents=True, exist_ok=True)
    for name, definition in visuals:
        write_json(visuals_dir / name / "visual.json", definition)


def panorama() -> tuple[dict, list[tuple[str, dict]]]:
    p = page(stable_id("page-panorama"), "Panorama del cubo")
    v = [
        textbox(
            "p1-title",
            "NYC311 | Panorama de solicitudes",
            32,
            20,
            1500,
            42,
            size_px=28,
            color="#12304A",
            weight="bold",
        ),
        textbox(
            "p1-subtitle",
            "Conexión Live a SSAS · CuboFase1 / DW NYC311 · jerarquía Año → Trimestre → Mes → Fecha · KPI de cobertura de tiempo observado (meta analítica 95%, no SLA).",
            34,
            64,
            1820,
            26,
            size_px=14,
        ),
        slicer("p1-date", 32, 100, 430, 105, "Fecha Creacion", "Fecha", "Fecha de creación"),
        slicer("p1-borough", 482, 100, 430, 105, "Dim PerfilCluster", "Borough", "Distrito (Borough)"),
        slicer("p1-agency", 932, 100, 430, 105, "Dim Agencia", "Agency Name", "Agencia ejecutora"),
        slicer("p1-cluster", 1382, 100, 506, 105, "Dim PerfilCluster", "Cluster Nombre", "Segmento K-Means"),
        card("p1-total", 32, 225, 280, 130, "Solicitudes · recuento"),
        card(
            "p1-observed",
            332,
            225,
            280,
            130,
            "Con tiempo observado · recuento",
            measure="Solicitudes con tiempo",
        ),
        card(
            "p1-kpi-value",
            632,
            225,
            320,
            130,
            "KPI SSAS · cobertura (0–1)",
            measure="Cobertura de tiempo observado Value",
        ),
        category_hierarchy_chart(
            "p1-date-chart",
            "lineChart",
            32,
            385,
            920,
            625,
            "Fecha Creacion",
            ("Anio", "Trimestre", "Mes", "Fecha"),
            "Solicitudes por tiempo · Año → Trimestre → Mes → Fecha",
        ),
        chart(
            "p1-borough-chart",
            "clusteredBarChart",
            984,
            225,
            904,
            375,
            "Dim PerfilCluster",
            "Borough",
            "Volumen por distrito · recuento",
        ),
        chart(
            "p1-cluster-chart",
            "clusteredColumnChart",
            984,
            625,
            904,
            385,
            "Dim PerfilCluster",
            "Cluster Nombre",
            "Solicitudes por segmento K-Means · recuento",
        ),
    ]
    return p, v


def segmentacion() -> tuple[dict, list[tuple[str, dict]]]:
    p = page(stable_id("page-segmentacion"), "Segmentación K-Means")
    v = [
        textbox(
            "p2-title",
            "NYC311 | Segmentación de perfiles K-Means",
            32,
            20,
            1600,
            42,
            size_px=28,
            color="#12304A",
            weight="bold",
        ),
        textbox(
            "p2-subtitle",
            "El clúster clasifica perfiles agencia + tipo de problema + distrito; la unidad de conteo sigue siendo la solicitud.",
            34,
            64,
            1820,
            26,
            size_px=14,
        ),
        slicer("p2-cluster", 32, 100, 540, 105, "Dim PerfilCluster", "Cluster Nombre", "Segmento K-Means"),
        slicer("p2-borough", 592, 100, 420, 105, "Dim PerfilCluster", "Borough", "Distrito (Borough)"),
        slicer("p2-agency", 1032, 100, 420, 105, "Dim Agencia", "Agency Name", "Agencia ejecutora"),
        slicer("p2-date", 1472, 100, 416, 105, "Fecha Creacion", "Fecha", "Fecha de creación"),
        card("p2-total", 32, 225, 420, 130, "Solicitudes en el contexto actual · recuento"),
        card(
            "p2-kpi-value",
            472,
            225,
            420,
            130,
            "KPI SSAS · cobertura de tiempo",
            measure="Cobertura de tiempo observado Value",
        ),
        textbox(
            "p2-kpi-note",
            "KPI formal del cubo: valor = solicitudes con duración observada / solicitudes totales; meta analítica = 95%.",
            912,
            238,
            976,
            95,
            size_px=15,
            color="#526477",
        ),
        chart(
            "p2-cluster-chart",
            "clusteredBarChart",
            32,
            385,
            908,
            625,
            "Dim PerfilCluster",
            "Cluster Nombre",
            "Volumen por clúster · recuento de solicitudes",
        ),
        chart(
            "p2-agency-chart",
            "clusteredBarChart",
            960,
            385,
            928,
            625,
            "Dim Agencia",
            "Agency Name",
            "Volumen por agencia · recuento de solicitudes",
        ),
    ]
    return p, v


def operacion() -> tuple[dict, list[tuple[str, dict]]]:
    p = page(stable_id("page-operacion"), "Diagnóstico operativo")
    v = [
        textbox(
            "p3-title",
            "NYC311 | Diagnóstico operativo",
            32,
            20,
            1500,
            42,
            size_px=28,
            color="#12304A",
            weight="bold",
        ),
        textbox(
            "p3-subtitle",
            "Vista para localizar concentración de solicitudes por agencia, distrito y segmento, manteniendo la trazabilidad al cubo OLAP.",
            34,
            64,
            1820,
            26,
            size_px=14,
        ),
        slicer("p3-date", 32, 100, 430, 105, "Fecha Creacion", "Fecha", "Fecha de creación"),
        slicer("p3-agency", 482, 100, 430, 105, "Dim Agencia", "Agency Name", "Agencia ejecutora"),
        slicer("p3-borough", 932, 100, 430, 105, "Dim PerfilCluster", "Borough", "Distrito (Borough)"),
        slicer("p3-cluster", 1382, 100, 506, 105, "Dim PerfilCluster", "Cluster Nombre", "Segmento K-Means"),
        chart(
            "p3-agency-chart",
            "clusteredBarChart",
            32,
            245,
            908,
            710,
            "Dim Agencia",
            "Agency Name",
            "Carga por agencia · recuento de solicitudes",
        ),
        chart(
            "p3-profile-chart",
            "clusteredColumnChart",
            960,
            245,
            928,
            710,
            "Dim PerfilCluster",
            "Cluster Nombre",
            "Volumen por clúster K-Means · recuento de solicitudes",
        ),
        textbox(
            "p3-note",
            "Lectura metodológica: el cubo publica aquí el recuento de solicitudes. La duración no se interpreta como mediana ni SLA porque esta conexión Live no expone una medida de mediana. La categoría “Sin perfil K-Means”, si aparece como miembro desconocido, debe conservarse en la lectura del universo.",
            32,
            975,
            1856,
            65,
            size_px=13,
        ),
    ]
    return p, v


def build() -> None:
    if not PBIP.is_file() or not REPORT.is_dir():
        raise FileNotFoundError(f"No se encontró el PBIP Live: {PBIP}")

    builders = [panorama, segmentacion, operacion]
    pages: list[dict] = []
    visual_count = 0
    for builder in builders:
        page_definition, visuals = builder()
        write_page(page_definition, visuals)
        pages.append(page_definition)
        visual_count += len(visuals)

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
    print(f"PBIR OLAP construido: {len(pages)} páginas, {visual_count} visuales")
    print(f"Proyecto: {PBIP}")


if __name__ == "__main__":
    build()
