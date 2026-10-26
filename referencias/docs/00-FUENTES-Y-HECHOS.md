# Contrato de hechos y origen del conocimiento

**Lecturas realizadas al preparar este kit:** premisa PDF subida por el usuario; GitHub `pgap22/catedra_fase1` (rama `master`, commit `a689fef685258197aeecb06509fd34d4b18ab775`) y `pgap22/dmd-fase2` (rama `main`, commit `b91490e01198404fe8413e3178d14447b6b761d6`). **Antes de implementar, Codex debe contrastar el checkout local y actualizar cualquier diferencia**. Un `.pdf/.docx` binario de GitHub no fue leído íntegramente durante esta elaboración: para afirmaciones finas, releer los informes reales localmente. No declarar verificadas páginas no inspeccionadas.

## 1. Lo obligatorio según el docente (Fase 3, premisa pp. 7–9)

- Fase 3: **15%**, entrega estimada **2–7 de noviembre de 2026**, con **defensa oral**.
- **Dashboard interactivo Power BI o Reporting Services**: conectado al DW mediante importación o conexión en vivo; KPIs/tendencias/mapas/slicers adecuados; resultados de minería integrados en el tablero.
- **Memoria técnica consolidada**: resumen ejecutivo, infraestructura/tecnologías, costos de infraestructura/licencias/desarrollo, ventaja competitiva y ROI **estimado**.
- **Defensa de máximo 25 minutos por grupo**: demo breve de ETL, esquema, minería e interacción con Power BI; teoría del proyecto.
- Rúbrica F3 (peso **dentro de la fase**): 25% diseño/usabilidad; 20% integración DW–minería–BI; 15% costos/viabilidad; 30% defensa/dominio; 10% memoria final.

No confundir 15% de nota final de la Fase 3 con los porcentajes internos de su rúbrica.

## 2. Contrato Fase 1 (código SQL público comprobado)

- **SQL Server**, base `DW_NYC311`, schemas `raw`, `stg`, `etl`, `dw`. Origen operativo: NYC311.
- Esquema estrella: `dw.FactSolicitud`: **1 fila = 1 solicitud**; `codigo_solicitud` único; claves hacia dimensiones.
- Dimensiones: `dw.DimFecha`, `dw.DimAgencia`, `dw.DimProblema`, `dw.DimGeografia`, `dw.DimEstado`, `dw.DimCanal`.
- Medida central `minutos_resolucion` puede ser `NULL`; fecha creación y fecha cierre (esta última puede ser `NULL`); latitud/longitud.
- Existe un proyecto **SSIS** (`catedra_fase1/Package.dtsx`), además de DDL en `sql/`.
- **No consta en ese repo un informe F1 autocontenido ni credenciales, servidor accesible o base exportada.** No afirmar que el ETL funciona en la máquina actual sin ejecutarlo.

## 3. Contrato Fase 2 (README, SQL y notebook inspeccionados)

- Fuente de minería: `mining.vw_dataset_fase2`, construida sobre `dw.FactSolicitud` y dimensiones; exportación `tmp/data/resultados.csv` vía **Git LFS** (el archivo versionado en Git es un puntero; contenido real ~139 MB). En la vista `demora_alta` es 1 si duración > P75, 0 si <= P75, y `NULL` si no hay duración.
- Universo presentado: **1,293,816 solicitudes** abril–julio 2026; **63,079** sin tiempo final (según README); umbral **P75=4,329 minutos** calculado del período. El umbral histórico no es estándar externo ni promesa de servicio.
- Árbol optimizado: **Recall 95.15%; F1 78.37%; ROC-AUC 0.952**; **58,549** verdaderos positivos y **2,982** falsos negativos según README, en el **conjunto de prueba**, no en el total de tickets.
- Variables predictoras: `agency`, `complaint_type`, `borough`, `open_data_channel_type`, `mes`, `dia_semana`. Se excluyen duración, estado, ID, año y coordenadas para evitar fuga/sin utilidad en ese experimento.
- K-Means: se agrupa por **`agency + complaint_type + borough`**, se crean perfiles, se filtra volumen >=100 y métricas no nulas, se escala; **912 perfiles iniciales → 487 con volumen mínimo → 480 modelados**, `K=3`, Silhouette aproximadamente **0.421**.
- Grupos descriptivos reportados: **resolución rápida y baja demora** (899,050 solicitudes), **resolución prolongada y alta demora** (351,275), **rezago crítico y alta proporción sin resolver** (29,467). **Suma 1,279,792**, no 1,293,816; diferencia **14,024** solicitudes que no deben desaparecer del BI. Validar las cifras contra ejecución local antes de citarlas como corrientes.
- Notebook existente etiqueta `profiles["cluster_nombre"]`, pero **NO exporta ese mapeo a SQL/CSV ni genera una tabla permanente de predicciones por solicitud** en el código inspeccionado. Se deben construir esos artefactos, respetando exactamente el pipeline/normalización, o informar claramente que se muestran únicamente métricas históricas.

## 4. Preguntas que no se resuelven inventando

- ¿Está accesible SQL Server `DW_NYC311` desde la máquina de Power BI? Descubrir con conexión real.
- ¿Los tickets del DW local coinciden con el CSV F2 y el período? Comparar filtros/conteos antes de asumir.
- ¿Qué fecha se usará como corte del dashboard? Mostrarla explícitamente.
- ¿Qué costos y beneficios existen realmente? Si no hay cotizaciones ni explotación real, hacer **escenarios transparentes**, nunca cifras “observadas”.
- ¿Puede Codex acceder a Power BI Desktop mediante MCP? Verificar tool y apertura; no dar por hecho que las herramientas de modelo pueden editar reportes visuales.

## 5. Jerarquía de evidencia

**A = archivo SQL, notebook o artefacto abierto y leído. B = resultado numérico reportado por Fase 2, reproducible pero no reejecutado aquí. C = supuesto para propuesta F3.** Las tablas o afirmaciones sensibles deben identificar A/B/C en la memoria o en notas metodológicas, sin contaminar las diapositivas con etiquetas innecesarias.
