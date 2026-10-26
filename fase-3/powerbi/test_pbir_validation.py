"""Suite de validación automatizada para el PBIP/PBIR/TMDL y PBIX final de NYC311 Fase 3."""

import json
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
report_dir = root / "fuente_pbip" / "NYC311_Fase3_Codigo.Report"
model_table = (
    root
    / "fuente_pbip"
    / "NYC311_Fase3_Codigo.SemanticModel"
    / "definition"
    / "tables"
    / "bi vw_solicitudes_segmentadas.tmdl"
)
final_pbix = root / "NYC311_Fase3_Final.pbix"

errors = []

# 1. Check TMDL
print("=== 1. VALIDANDO TMDL ===")
tmdl_text = model_table.read_text(encoding="utf-8")
if "\ufffd" in tmdl_text:
    errors.append("TMDL contiene caracteres corruptos (\ufffd)")

required_tmdl = [
    "column fecha = DATE(",
    "column nombre_mes = FORMAT(",
    "hierarchy 'Jerarquía de fechas'",
    "measure 'Solicitudes distintas' = COALESCE(DISTINCTCOUNT(",
    "measure 'Solicitudes con tiempo' = COALESCE(CALCULATE(",
    "measure 'Solicitudes sin duración' = COALESCE(CALCULATE(",
    "measure 'Solicitudes con demora alta' = COALESCE(CALCULATE(",
    "measure 'Tasa demora alta' = DIVIDE(",
    "measure 'Mediana minutos observados' = MEDIAN(",
    "measure 'Solicitudes segmentadas' = COALESCE(CALCULATE(",
    "measure 'Solicitudes fuera de perfil' = COALESCE(CALCULATE(",
    "measure 'Porcentaje segmentado' = DIVIDE(",
]
for req in required_tmdl:
    if req not in tmdl_text:
        errors.append(f"TMDL falta definicion: {req}")
    else:
        print(f"  [OK] Encontrado: {req[:45]}...")

# 2. Check PBIR Report JSONs
print("\n=== 2. VALIDANDO JSON / PBIR ===")
pages_json = report_dir / "definition" / "pages" / "pages.json"
with open(pages_json, "r", encoding="utf-8") as f:
    pages_meta = json.load(f)

page_order = pages_meta.get("pageOrder", [])
print(f"  Total paginas configuradas: {len(page_order)}")
if len(page_order) != 3:
    errors.append(f"Se esperaban 3 paginas, encontradas: {len(page_order)}")

visual_count = 0
for pid in page_order:
    pfile = report_dir / "definition" / "pages" / pid / "page.json"
    with open(pfile, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    pname = pdata.get("displayName")
    width = pdata.get("width")
    height = pdata.get("height")
    print(f"  Pagina: {pname} ({width}x{height}, {pdata.get('displayOption')})")

    if width != 1920 or height != 1080:
        errors.append(f"Pagina {pname} no cumple relacion 16:9 (1920x1080): {width}x{height}")

    vdir = report_dir / "definition" / "pages" / pid / "visuals"
    page_visuals = list(vdir.iterdir())
    visual_count += len(page_visuals)
    has_date_slicer = False

    for vpath in page_visuals:
        vfile = vpath / "visual.json"
        with open(vfile, "r", encoding="utf-8") as f:
            raw_v = f.read()
            if "\ufffd" in raw_v:
                errors.append(f"Caracter corrupto en {vfile}")
            vobj = json.loads(raw_v)
            vtype = vobj.get("visual", {}).get("visualType")
            pos = vobj.get("position", {})
            # Bounds check
            x = pos.get("x", 0)
            y = pos.get("y", 0)
            w = pos.get("width", 0)
            h = pos.get("height", 0)
            if x + w > 1920:
                errors.append(f"Visual excede ancho 1920: {vpath.name} en {pname} (x+w={x+w})")
            if y + h > 1080:
                errors.append(f"Visual excede alto 1080: {vpath.name} en {pname} (y+h={y+h})")
            # Check date slicer
            if vtype == "slicer":
                col = (
                    vobj.get("visual", {})
                    .get("query", {})
                    .get("queryState", {})
                    .get("Values", {})
                    .get("projections", [{}])[0]
                    .get("field", {})
                    .get("Column", {})
                    .get("Property")
                )
                if col == "fecha":
                    has_date_slicer = True
                    if h < 100:
                        errors.append(f"Slicer de fecha en {pname} tiene altura insuficiente: {h}px")
            # Check cards
            if vtype == "cardVisual":
                measure_prop = (
                    vobj.get("visual", {})
                    .get("query", {})
                    .get("queryState", {})
                    .get("Data", {})
                    .get("projections", [{}])[0]
                    .get("field", {})
                    .get("Measure", {})
                    .get("Property")
                )
                # Verify measure exists in TMDL
                if f"measure '{measure_prop}'" not in tmdl_text:
                    errors.append(f"Tarjeta referencia medida inexistente en TMDL: '{measure_prop}'")

    print(f"    Visuales: {len(page_visuals)}, Slicer de fecha verificado: {has_date_slicer}")
    if not has_date_slicer:
        errors.append(f"Pagina {pname} no tiene segmentador de fecha")

print(f"  Total visuales en el informe PBIR: {visual_count}")

# 3. Check Final PBIX
print("\n=== 3. VALIDANDO PBIX ===")
print(f"  Ruta: {final_pbix}")
print(f"  Tamano: {final_pbix.stat().st_size:,} bytes")
if final_pbix.stat().st_size < 30_000_000:
    errors.append("PBIX es demasiado pequeno (posible perdida de DataModel)")

with zipfile.ZipFile(final_pbix, "r") as z:
    infolist = z.infolist()
    filenames = [item.filename for item in infolist]
    print(f"  Archivos en paquete PBIX: {len(filenames)}")
    if "DataModel" not in filenames:
        errors.append("DataModel no encontrado en PBIX")
    if "Report/definition/pages/pages.json" not in filenames:
        errors.append("Report/definition no inyectado en PBIX")
    # Check for corrupt characters in injected json
    for item in infolist:
        if item.filename.endswith(".json"):
            content = z.read(item.filename).decode("utf-8", errors="replace")
            if "\ufffd" in content:
                errors.append(f"PBIX contiene caracter corrupto en {item.filename}")

print("\n=== RESUMEN DE COMPROBACIÓN ===")
if errors:
    print(f"[FALLO] Se encontraron {len(errors)} errores:")
    for e in errors:
        print("  -", e)
    raise SystemExit(1)
else:
    print("[EXITO] TODAS LAS VALIDACIONES PASARON PERFECTAMENTE (0 errores).")
