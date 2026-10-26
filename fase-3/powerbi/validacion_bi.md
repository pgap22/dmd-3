# Evidencia de Validación BI — NYC311 Fase 3

**Fecha de comprobación:** 26 de octubre de 2026.  
**Entorno comprobado:** SQL Server `localhost` (`DW_NYC311`), motor VertiPaq Analysis Services (`msmdsrv`), proyecto PBIP/PBIR/TMDL en `fuente_pbip/` y archivo ejecutable de entrega `NYC311_Fase3_Final.pbix`.

---

## 1. Validación en SQL Server (`DW_NYC311`)

| Objeto | Grano | Registros | Validación de Integridad |
|---|---|---:|---|
| `dw.FactSolicitud` | 1 fila / solicitud | 1,312,465 (rango completo disponible) | Universo oficial del DW. |
| `mining.vw_dataset_fase2` | 1 fila / solicitud | 1,312,465 | Coincide 1:1 con el hecho dimensional. |
| `bi.PerfilCluster` | 1 fila / terna elegible | 481 | Perfiles modelados con K-Means (K=3, r42, n_init=10). |
| `bi.vw_solicitudes_segmentadas` | 1 fila / solicitud | 1,312,465 | `LEFT JOIN` nulo-seguro; cero multiplicación de filas. |

### Cobertura de Segmentación
- **Segmentadas (`es_segmentado = 1`):** **1,298,155** solicitudes (98.91%).
  - Clúster 1 (Resolución rápida y baja demora): 910,529 solicitudes (mediana 129 min).
  - Clúster 2 (Resolución prolongada y alta demora): 358,005 solicitudes (mediana 11,241 min).
  - Clúster 3 (Rezago crítico y alta proporción sin resolver): 29,621 solicitudes (mediana 21,277 min).
- **Fuera de perfil (`es_segmentado = 0`):** **14,310** solicitudes (1.09%) etiquetadas como `Sin perfil K-Means`.
- **Suma exacta:** 1,298,155 + 14,310 = **1,312,465**.

---

## 2. Validación de Medidas DAX y Corrección de Tarjetas Vacías/0

Se auditó la causa técnica de tarjetas vacías o en 0 en los artefactos de código:
1. **Falta de manejo de valores nulos:** Medidas como `Solicitudes fuera de perfil` evaluaban a `BLANK()` al filtrar un clúster específico donde no hay casos fuera de perfil. Se encapsularon con `COALESCE(..., 0)` para garantizar un valor numérico certero (`0`) en lugar de `(En blanco)`.
2. **Definición de proyecciones limpias en PBIR:** Se eliminaron definiciones no conformes (`objects.value`/`objects.label`) en el contenedor `cardVisual`, asegurando que el motor de Power BI procese la medida directamente bajo el rol `"Data"`.
3. **Consistencia en nombres con acento:** Se verificó que las cadenas DAX y JSON coincidan exactamente en caracteres Unicode (`Solicitudes sin duración`), eliminando discrepancias de codificación.

| Medida DAX | Expresión / Definición | Valor Evaluado | Nota Metodológica |
|---|---|---:|---|
| **`[Solicitudes distintas]`** | `COALESCE(DISTINCTCOUNT('bi vw_solicitudes_segmentadas'[codigo_solicitud]), 0)` | **1,312,465** | Universo global idéntico al DW. |
| **`[Solicitudes con tiempo]`** | `COALESCE(CALCULATE([Solicitudes distintas], NOT ISBLANK(minutos_resolucion)), 0)` | **1,248,998** | Solicitudes con duración observada. |
| **`[Solicitudes sin duración]`**| `COALESCE(CALCULATE([Solicitudes distintas], ISBLANK(minutos_resolucion)), 0)` | **63,467** | Conservadas en `NULL` (no imputadas a cero). |
| **`[Solicitudes con demora alta]`**| `COALESCE(CALCULATE([Solicitudes distintas], demora_alta = 1), 0)` | **313,360** | Casos observados > umbral histórico fijo de 4,329 min. |
| **`[Tasa demora alta]`** | `DIVIDE([Solicitudes con demora alta], [Solicitudes con tiempo], 0.0)` | **25.1%** | Proporción exacta sobre universo con tiempo. |
| **`[Mediana minutos observados]`** | `MEDIAN('bi vw_solicitudes_segmentadas'[minutos_resolucion])` | **330 min** | Mediana general observada (~5.5 horas). |
| **`[Solicitudes segmentadas]`** | `COALESCE(CALCULATE([Solicitudes distintas], es_segmentado = TRUE), 0)` | **1,298,155** | Casos pertenecientes a los 481 perfiles. |
| **`[Solicitudes fuera de perfil]`** | `COALESCE(CALCULATE([Solicitudes distintas], es_segmentado = FALSE), 0)` | **14,310** | Casos aislados bajo `Sin perfil K-Means`. |
| **`[Porcentaje segmentado]`** | `DIVIDE([Solicitudes segmentadas], [Solicitudes distintas], 0.0)` | **98.91%** | Cobertura real del modelo de perfiles. |

---

## 3. Selector de Fechas, Jerarquía y Segmentadores Ampliados

Se implementaron las siguientes mejoras trazables en el PBIP/PBIR/TMDL:
1. **Selector de fecha del modelo:** Se añadió un segmentador interactivo sobre la columna `fecha` (`DATE(anio, mes, 1)`) en las tres páginas, sin filtros fijos ocultos ni títulos estáticos que restrinjan artificialmente la demo.
2. **Jerarquía temporal usable:** Se creó en el modelo TMDL la jerarquía `'Jerarquía de fechas'` con niveles `Año` y `Mes` (`nombre_mes`), con ordenamiento automático por número de mes (`sortByColumn: mes`).
3. **Ampliación de espacio para segmentadores:** La altura de los segmentadores se incrementó de 78px a **105px**, distribuyendo 5 filtros por página a lo largo de un ancho total de 1,856px (márgenes de 32px), evitando truncamiento vertical u opciones ocultas.
4. **Interactividad dinámica:** Todas las tarjetas KPI, tendencias y gráficos de distribución responden dinámicamente al intervalo de fechas y dimensiones seleccionadas.

---

## 4. Validación de Estructura del PBIX Canónico (`NYC311_Fase3_Final.pbix`)

- **Tamaño del archivo:** 33,863,643 bytes (~33.8 MB).
- **Modelo VertiPaq (`DataModel`):** 33,819,011 bytes (contiene los datos en memoria optimizada).
- **Formato de páginas:** 3 páginas configuradas a **1920 × 1080 (proporción 16:9, FitToPage)**.
- **Conteo de visuales:** **42 visuales activos** (14 en Página 1, 12 en Página 2, 16 en Página 3).
- **Títulos y etiquetas:** En español técnico con unidades explícitas (recuento, minutos de resolución), sin textos de filtro estáticos.

---

## 5. Reporte de Pruebas Locales y Limitaciones

- **Pruebas ejecutadas y superadas:**
  - Script de validación automatizada `test_pbir_validation.py`: 0 errores en sintaxis JSON, límites espaciales (1920x1080), referencias de medidas TMDL e integridad del empaquetado ZIP.
  - Generación de PBIX canónico por código mediante `build_nyc311_pbir.py` validada exitosamente.
- **Limitación de entorno interactivo:**
  - La sesión de ejecución opera como servicio en segundo plano sin sesión de escritorio interactiva de Windows (`WinSta0\Default`). De acuerdo con la regla estricta de `AGENTS.md` (*"no afirmes que abriste Power BI Desktop si no fue posible"*), se registra que la comprobación se realizó sobre los artefactos de código (TMDL, PBIP, PBIR, JSON y PBIX) y consultas SQL al DW local, sin apertura de la interfaz gráfica de Power BI Desktop durante esta intervención.
