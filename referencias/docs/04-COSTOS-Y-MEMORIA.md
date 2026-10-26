# Memoria técnica final + análisis de costos y viabilidad

## Un documento integrado; no un collage

Redactar como **una sola historia**:

1. **Portada e identificación**: curso, grupo, fecha, docente, tema; datos correctos del equipo.
2. **Resumen ejecutivo (máx. 1 página)**: problema NYC311, solución DW→minería→BI, alcance abril–julio 2026, 2–3 hallazgos comprobados y recomendaciones reales.
3. **Contexto y problema de negocio**: demoras, carga operativa, necesidad de priorizar. No hablar de "clientes" si son solicitudes 311.
4. **Arquitectura y linaje**: fuente NYC Open Data, SQL Server, SSIS, schemas raw/stg/dw, vista mining, Python/scikit-learn, Power BI. Diagrama legible; cada flecha con datos que efectivamente fluyen.
5. **Fase 1**: grano y dimensiones del esquema estrella; ETL (extracción, limpieza, llaves subrogadas, carga), evidencia técnica disponible y limitaciones.
6. **Fase 2**: KDD, construcción de `demora_alta` con P75, criterio 80/20, árbol y su evaluación, perfiles `agency + complaint_type + borough`, selección K=3, Silhouette y cobertura. Evidencia propia.
7. **Fase 3**: diseño de modelo BI, modo Import/DirectQuery efectivamente usado, joins y población fuera del cluster, cada página y decisión soportada; capturas reales del dashboard.
8. **Hallazgos e implicaciones**: 2–4 hallazgos cuantitativos sustentados; decisiones que un operador **podría evaluar** (no afirmar que NYC adoptó el modelo).
9. **Costos, escenarios y retorno**: infraestructura/licencias/desarrollo y mantenimiento anual; beneficio monetario hipotético **o** cualitativo si no hay base monetaria. Fórmulas y límites explícitos.
10. **Riesgos, supuestos y ética**: datos abiertos, sesgo temporal, limitación de nulos, riesgo de clasificar por agencia, no causalidad, costos estimados.
11. **Conclusiones y recomendaciones**: enlazadas al problema y evidencia (sin frases tipo "la transformación digital es fundamental").
12. **Fuentes, anexos y reproducibilidad**: referencias externas, versiones/commits, SQL, capturas con título, accesibilidad de recursos.

## Costos: tabla mínima indispensable

| Bloque | Concepto | Método de estimación | Periodicidad |
|---|---|---|---|
| Infraestructura | SQL Server: servidor/VM/hosting, almacenamiento, respaldos | recurso local/servicio elegido con evidencia de precio; separar costo incremental | mensual/anual |
| Herramientas | Windows/SQL Server/Power BI Desktop/Pro/Fabric si aplica | edición y licencia real; **Desktop puede usarse sin plan de publicación**, verificar condiciones de distribución | único/anual |
| Desarrollo | ingeniería de datos, modelado minería, BI, revisión | horas estimadas × tarifa supuesto o valor oportunidad | inicial |
| Operación | ETL, actualización, supervisión, soporte, formación | horas mensuales × tarifa y/o servicio | mensual/anual |

**No es válido** inventar una cotización de Microsoft, salarios NYC, ahorro de atención o número de empleos. Verificar precios/licencias actuales oficiales y dejar **fecha + enlace**. Aclarar cuándo un servicio es local/gratuito en el prototipo y cuándo generaría costo real al desplegarlo.

## Modelo de viabilidad simple (escenarios, no exactitud falsa)

Elegir horizonte (p. ej. 3 años) y misma moneda/período. Construir 3 escenarios de negocio **con supuestos declarados**, no resultados medidos:

```text
Costo inicial = horas de construcción * tarifa asumida + configuración + equipos incrementales
Costo anual = licencias + infraestructura + mantenimiento + operación
Beneficio anual estimado = horas de análisis evitadas * costo/hora
                       + costos de reprocesos evitados que puedan sustentarse
Beneficio neto (horizonte) = suma beneficios - costo inicial - suma costos recurrentes
ROI simple (horizonte) = beneficio neto / (costo inicial + suma costos recurrentes) * 100
```

Agregar sensibilidad baja/base/alta variando **volumen de tareas ahorradas, adopción y tarifas**, dejando igual metodología. **No monetizar** automáticamente recall, 2,982 falsos negativos ni casos rezagados: son cantidades del experimento, no ahorros económicos causales. Si faltan datos para beneficio monetario, decirlo; reportar **punto de equilibrio en horas ahorradas** y beneficios cualitativos por separado. No presentar un ROI positivo como conclusión empírica.

### Preguntas que un buen ROI debe resistir

- ¿Costo **adicional** del proyecto vs gasto existente o doble conteo?
- ¿Qué variante de Power BI requiere licencia al **compartir**, no solo desarrollar?
- ¿El beneficio está medido o simulado? ¿En qué período y moneda?
- ¿Qué evidencia justificaría la adopción del sistema antes de atribuir ahorro?
- ¿Cómo cambia el resultado si la tasa de adopción es la mitad?

## Word/DOCX: legibilidad y rigor

- Usar estilos de título reales con jerarquía, no negrita manual. Índice automático si tamaño lo amerita.
- Numeración de tablas/figuras, fuente y nota de elaboración. Referencias cruzadas a objetos reales.
- Encabezados de tabla repetidos, anchura útil, cifras con unidad y número de decimales sensato.
- Diagramas nítidos, sin recortes; capturas del dashboard suficientes para leerse en A4/carta.
- Tiempos siempre expresados en minutos/horas explícitos; porcentajes con denominador indicado.
- Citas APA/IEEE según exigencia del curso (no inventar un formato obligatorio no escrito).
- Evitar repeticiones entre capítulos, listas de tecnologías inconexas, aseveraciones infladas o explicaciones vacías.
- **Exportar PDF y revisar visualmente** portada, páginas con tablas, diagramas y bibliografía antes de entregar. Revisión formal final por personas.

## Control de consistencia editorial

Los términos `solicitud`, `duración observada`, `demora alta (P75)`, `perfil`, `clúster`, `score`, `riesgo`, `ROI escenario` tienen una sola definición. No se cambian números, población ni nombres de grupos entre memoria, tablero y slides sin explicación.
