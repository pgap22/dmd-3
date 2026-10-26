# Guion de defensa oral — Fase 3 NYC311

Duración total máxima: **25 minutos** (23 minutos de exposición estructurada + 2 minutos de margen / preguntas del tribunal).
Diapositivas de apoyo: `fase-3/Presentacion_Fase3_NYC311.pptx` (13 diapositivas ejecutivas, formato pitch).
Informe interactivo: `fase-3/powerbi/NYC311_Fase3_Final.pbix`.
Documento académico: `fase-3/Documento_Fase3.docx` (y `Documento_Fase3.pdf`).

---

## Cronograma de intervención (23 min + 2 min margen)

| Tiempo | Diapositivas | Tema / Fases | Evidencia y contenido clave a defender |
|---|---|---|---|
| **0:00–2:00** | Slide 1–2 | Portada y Problema de Decisión | Contexto NYC311; universo BI actual de 1,312,465 solicitudes disponibles entre enero y julio (enero y abril–julio); 63,467 sin duración tratadas como NULL; umbral histórico P75 = 4,329 min (~72.2 h). |
| **2:00–5:00** | Slide 3–4 | Fase 1: Arquitectura DW y Metodología Kimball | Integridad de grano (1 fila = 1 solicitud); no multiplicación en JOINs; Ciclo de Vida Dimensional de Ralph Kimball (1998) en 10 etapas; esquema estrella con `dw.FactSolicitud` y dimensiones conformadas en SQL Server `DW_NYC311`. |
| **5:00–7:00** | Slide 4–5 | ETL con SSIS y Cubo OLAP | Ingesta de API SODA (erm2-nwe9) por SSIS (`Package.dtsx`); separación de capas raw/stg/dw; validaciones cronológicas; cubo OLAP en SSAS (`cubo_olap/CuboFase1.dwproj`) con dimensión analítica `Dim PerfilCluster`. |
| **7:00–11:00** | Slide 6–7 | Fase 2: Minería de Datos (KDD) | Proceso KDD con Scikit-learn (Pedregosa et al., 2011). Árbol CART: variables sin fuga, Recall 95.15%, F1 78.37%, ROC-AUC 0.952 en test del snapshot F2. K-Means: 480 perfiles en F2 original y 481 en la publicación BI actual, siempre sobre `agencia+tipo+borough`. |
| **11:00–18:00** | Slide 8–10 | Fase 3: Demostración en vivo de Power BI | Abrir `powerbi/NYC311_Fase3_Final.pbix` en Power BI Desktop. Recorrer las 3 páginas 16:9; demostrar slicers y aislamiento de solicitudes `Sin perfil K-Means` (14,310), sin presentar un drilldown territorial no comprobado como cifra fija. |
| **18:00–20:30** | Slide 11 | Costos, Viabilidad y FinOps | Marco CAPEX/OPEX (Horngren et al., 2012): CAPEX US$4,520 + OPEX anual US$4,200 (TCO 3 años = US$17,120). Marco Ross et al. (2019): beneficio por horas de reportería evitadas (tarifa US$18/h), ROI escenario base 162.4% (payback mes 14). Es un escenario, no ahorro observado. |
| **20:30–23:00** | Slides 12–13 | Cierre, límites y respaldo | Tres decisiones defendibles; gobernanza, no causalidad, cobertura actual y supervisión humana. La diapositiva 13 queda como respaldo bibliográfico. |
| **23:00–25:00** | — | Margen y Preguntas del Tribunal | Ronda de preguntas técnicas del docente / tribunal evaluador. |

---

## Procedimiento exacto de la demostración en vivo (Power BI Desktop)

1. **Apertura de la herramienta:**
   - Abrir el archivo `fase-3/powerbi/NYC311_Fase3_Final.pbix` en Power BI Desktop.
   - Mostrar la vista de modelo semántico: verificar que la fuente de datos es la vista SQL `bi.vw_solicitudes_segmentadas` operando en modo **Import** (motor VertiPaq).
2. **Página 1 — Panorama de atención ciudadana:**
   - Señalar la tarjeta principal: **1,312,465 solicitudes distintas** (medida `DISTINCTCOUNT(codigo_solicitud)`).
   - Señalar la mediana global observada: **330 minutos** (recalcar que excluye automáticamente valores nulos).
   - Mostrar la proporción de demora alta (25.1% sobre casos con tiempo) y solicitudes sin duración (63,467 solicitudes, 4.83%).
   - Observar la tendencia mensual del rango disponible: enero y abril a julio de 2026.
3. **Página 2 — Dónde concentrar capacidad:**
   - Realizar drilldown en la matriz territorial seleccionando un borough o agencia y leer los valores que muestre el PBIX actual; no memorizar cifras de una versión anterior.
   - Explicar la distribución por canales: Phone continúa siendo el canal primario, seguido por plataformas Online y Mobile.
4. **Página 3 — Segmentación y valor operativo:**
   - Mostrar el segmentador de Clústeres K-Means:
     * Seleccionar `Resolución prolongada y alta demora`: observar 358,005 solicitudes y mediana observada de 11,241 minutos.
     * Seleccionar `Rezago crítico y alta proporción sin resolver`: observar 29,621 solicitudes y 81.65% sin duración observada.
     * Seleccionar `Sin perfil K-Means`: la tarjeta muestra exactamente **14,310 solicitudes** (1.09% no modelado).
   - Quitar filtros y corroborar que el contador regresa exactamente a **1,312,465 solicitudes**, probando que la integración dimensional conserva el 100% del universo sin duplicar ni perder registros.

---

## Banco de preguntas frecuentes del tribunal y respuestas maestras

### 1. ¿Por qué construyeron un Data Warehouse y no conectaron Power BI directamente a la API o al CSV?
> **Respuesta:** "Para garantizar consistencia histórica, aislamiento transaccional y rendimiento analítico según el ciclo de vida de Ralph Kimball (1998). La API de NYC Open Data tiene límites de tasa y datos transaccionales con anomalías. El DW permite aplicar un proceso ETL formal en SSIS con capas staging, tipado estricto, llaves subrogadas y un esquema estrella atómico que sirve de fuente común tanto para la minería KDD como para Power BI y el cubo OLAP, garantizando que todos los analistas trabajen sobre la misma verdad sin duplicación."

### 2. ¿Qué es exactamente el P75 y por qué lo definieron en 4,329 minutos?
> **Respuesta:** "El P75 es el percentil 75 histórico de la duración observada de 1,230,737 solicitudes con fecha final registrada entre abril y julio de 2026. Equivale a 4,329 minutos (~72.2 horas). No es una promesa contractual ni un SLA; la publicación BI actual conserva ese umbral para mantener comparable la etiqueta."

### 3. ¿Cómo trataron las solicitudes sin fecha de cierre?
> **Respuesta:** "En el rango actual son 63,467 y se conservaron estrictamente como valores `NULL` tanto en `minutos_resolucion` como en `demora_alta`. En el tablero se auditan aparte; no se imputan a cero ni se interpretan como demora normal. El snapshot F2 original tenía 63,079."

### 4. ¿Por qué aplicaron K-Means sobre perfiles y no sobre cada solicitud individual?
> **Respuesta:** "Porque se modelan perfiles operativos por la terna `(agency, complaint_type, borough)`, no tickets individuales. F2 documentó 480 perfiles y la publicación BI actual reejecutada sobre el rango disponible conserva 481; la categoría `Sin perfil K-Means` mantiene visibles los casos no elegibles."

### 5. ¿Qué significa el Recall de 95.15% del árbol de decisión?
> **Respuesta:** "Significa que, en el conjunto de prueba independiente (20% estratificado), el modelo detectó preventivamente a 58,549 de las 61,531 solicitudes que efectivamente terminaron en demora alta. Su precisión fue del 66.63% (2 de cada 3 alertas son demoras reales). Por ende, el árbol funciona como un excelente filtro de priorización temprana o triaje preventivo para revisión humana, pero nunca debe utilizarse como un decisor autónomo sin supervisión."

### 6. ¿Por qué excluyeron variables como duración o estado del entrenamiento del árbol?
> **Respuesta:** "Para prevenir fuga de información (*data leakage*). La duración en minutos define directamente la variable objetivo, y el estado o la fecha de cierre solo se conocen una vez concluido el ciclo de vida del reclamo. Incluirlos habría producido un modelo artificialmente perfecto pero inútil en producción, ya que al momento de ingresar una nueva solicitud ciudadana esos atributos aún no existen."

### 7. ¿El ROI calculado del 162.4% es un ahorro real de dinero para NYC311?
> **Respuesta:** "No. Es un escenario de viabilidad económica formulado bajo la metodología de finanzas corporativas de Ross et al. (2019) y Horngren et al. (2012). No monetizamos la precisión del árbol ni los falsos negativos. El escenario base usa un TCO a 3 años de US$17,120 (CAPEX US$4,520 + OPEX anual US$4,200) y supone horas de reportería liberadas; el punto de equilibrio estimado es el mes 14."

### 8. ¿Qué consideraciones éticas y legales rigen el proyecto?
> **Respuesta:** "Nos basamos en los principios de la Ley para la Protección de Datos Personales (El Salvador, 2024 - Decreto 144) y los estándares de ética en inteligencia artificial. Garantizamos minimización y anonimización espacial (trabajando a nivel de borough y código postal, sin geocódigos domiciliarios exactos), prevenimos la discriminación algorítmica territorial y establecemos el principio obligatorio de *Human-in-the-Loop*: ningún algoritmo puede sancionar personal ni desviar presupuestos sin revisión y criterio humano colegiado."
