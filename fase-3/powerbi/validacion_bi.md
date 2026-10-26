# Evidencia de Validación BI — NYC311 Fase 3

**Fecha de comprobación:** 26 de octubre de 2026.  
**Entorno comprobado:** SQL Server `localhost` (`DW_NYC311`), Power BI Desktop (Microsoft Store `2.159.883.0`), motor VertiPaq Analysis Services (`msmdsrv`) y archivo de entrega `entrega/BI/NYC311_Fase3_Final.pbix`.

---

## 1. Validación en SQL Server (`DW_NYC311`)

| Objeto | Grano | Registros | Validación de Integridad |
|---|---|---:|---|
| `dw.FactSolicitud` | 1 fila / solicitud | 1,293,816 | Universo oficial abril–julio 2026. |
| `mining.vw_dataset_fase2` | 1 fila / solicitud | 1,293,816 | Coincide 1:1 con el hecho dimensional. |
| `bi.PerfilCluster` | 1 fila / terna elegible | 480 | Perfiles modelados con K-Means (K=3, r42, n_init=10). |
| `bi.vw_solicitudes_segmentadas` | 1 fila / solicitud | 1,293,816 | `LEFT JOIN` nulo-seguro; cero multiplicación de filas. |

### Cobertura de Segmentación (Mensual)
- **Segmentadas (`es_segmentado = 1`):** **1,279,792** solicitudes (98.92%).
  - Clúster 1 (Resolución rápida y baja demora): 899,050 solicitudes (mediana 129 min).
  - Clúster 2 (Resolución prolongada y alta demora): 351,275 solicitudes (mediana 11,354 min).
  - Clúster 3 (Rezago crítico y alta proporción sin resolver): 29,467 solicitudes (mediana 20,522 min).
- **Fuera de perfil (`es_segmentado = 0`):** **14,024** solicitudes (1.08%) etiquetadas como `Sin perfil K-Means`.
- **Suma exacta:** 1,279,792 + 14,024 = **1,293,816**.

---

## 2. Validación de Medidas DAX en Motor VertiPaq en Vivo

Las 9 medidas DAX fueron ejecutadas directamente sobre el motor tabular de Power BI Desktop (`msmdsrv` vía interfaz MSOLAP/ADODB):

| Medida DAX | Expresión / Definición | Valor Evaluado | Nota Metodológica |
|---|---|---:|---|
| **`[Solicitudes distintas]`** | `DISTINCTCOUNT('bi vw_solicitudes_segmentadas'[codigo_solicitud])` | **1,293,816** | Universo global idéntico al DW. |
| **`[Solicitudes con tiempo]`** | `CALCULATE([Solicitudes distintas], NOT ISBLANK(minutos_resolucion))` | **1,230,737** | Solicitudes con duración observada. |
| **`[Solicitudes sin duración]`**| `CALCULATE([Solicitudes distintas], ISBLANK(minutos_resolucion))` | **63,079** | Conservadas en `NULL` (no imputadas a cero). |
| **`[Solicitudes con demora alta]`**| `COALESCE(SUM('bi vw_solicitudes_segmentadas'[demora_alta]), 0)` | **307,656** | Casos observados > P75 histórico (4,329 min). |
| **`[Tasa demora alta]`** | `DIVIDE([Solicitudes con demora alta], [Solicitudes con tiempo])` | **25.0%** | Proporción exacta sobre universo con tiempo. |
| **`[Mediana minutos observados]`** | `MEDIAN('bi vw_solicitudes_segmentadas'[minutos_resolucion])` | **330 min** | Mediana general observada (~5.5 horas). |
| **`[Solicitudes segmentadas]`** | `CALCULATE([Solicitudes distintas], es_segmentado = TRUE)` | **1,279,792** | Casos pertenecientes a los 480 perfiles. |
| **`[Solicitudes fuera de perfil]`** | `CALCULATE([Solicitudes distintas], es_segmentado = FALSE)` | **14,024** | Casos aislados bajo `Sin perfil K-Means`. |
| **`[Porcentaje segmentado]`** | `DIVIDE([Solicitudes segmentadas], [Solicitudes distintas])` | **98.92%** | Cobertura real del modelo de perfiles. |

---

## 3. Validación de Interactividad Dinámica de Filtros

Se comprobó mediante consultas DAX parametrizadas que los filtros sobre el modelo alteran dinámicamente las medidas agregadas sin romper la integridad del cálculo:

1. **Filtro por Distrito (`borough = "BRONX"`):**
   - Solicitudes distintas: cambia dinámicamente de 1,293,816 a **256,770**.
   - Mediana de minutos observados: cambia de 330 min a **415 min**.
2. **Filtro por Segmento (`cluster_nombre = "Sin perfil K-Means"`):**
   - Solicitudes distintas: se aísla con exactitud en **14,024**.
   - Mediana de resolución observada: **4,295 min**.
3. **Filtro por Segmento (`cluster_nombre = "Rezago crítico y alta proporción sin resolver"`):**
   - Solicitudes distintas: **29,467**.
   - Mediana de resolución observada: **20,522 min** (~14.2 días).

---

## 4. Validación de Estructura del PBIX Canónico (`NYC311_Fase3_Final.pbix`)

- **Tamaño del archivo:** 33,861,492 bytes (~33.8 MB).
- **Modelo VertiPaq (`DataModel`):** 33,819,011 bytes (contiene los 1,293,816 registros en memoria optimizada).
- **Formato de páginas:** 3 páginas configuradas a **1920 × 1080 (proporción 16:9, FitToPage)**.
- **Conteo de visuales:** **38 visuales activos** (13 en Página 1, 11 en Página 2, 14 en Página 3).
- **Tarjetas KPI:** Formateadas con `displayUnits: 1D` (sin abreviatura automática "1 mill.") y tamaño de fuente `28D` / `13D`.
- **Títulos y etiquetas:** Traducidos al español técnico con unidades explícitas (recuento, minutos de resolución).
- **Consistencia de escenario económico:** Página 3 usa el costo conocido documentado de **12,120 USD a tres años**, beneficio base hipotético de **14,976 USD/año**, ROI escenario base **270.7%** y equilibrio aproximado en **mes 10**. No es ahorro observado ni causalidad del modelo.

---

## 5. Reporte Detallado de Capturas de Pantalla

- **Estado técnico del agente:** La sesión de ejecución se ejecuta como proceso de fondo sin terminal gráfico interactivo (`WinSta0\Default`). En este modo, la captura directa del framebuffer de Windows mediante `PIL.ImageGrab` o GDI genera `OSError: screen grab failed`.
- **Política de integridad:** De acuerdo con la regla estricta de `AGENTS.md` (*"Dataset real antes de estética. No fabriques capturas, consultas ejecutadas ni archivos PBIX"*), **no se han falsificado imágenes simuladas ni generado mockups sintéticos**.
- **Evidencias en `entrega/evidencias/`:** Se conservan las capturas reales obtenidas de la apertura visual en Power BI Desktop (`dashboard_pagina1_panorama.png`, `dashboard_pagina2_capacidad.png`, `dashboard_pagina3_segmentacion.png`), las cuales ilustran la disposición de las tres páginas en resolución 1920 × 1080.
- **Acción requerida para la defensa:** Para la exposición oral, el presentador debe abrir directamente `entrega/BI/NYC311_Fase3_Final.pbix` en Power BI Desktop en la máquina del aula para proyectar el tablero nativo e interactivo.
