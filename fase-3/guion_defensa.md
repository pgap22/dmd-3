# Guion de defensa Fase 3

Duración objetivo: 23 minutos de contenido y 2 minutos de margen.

| Tiempo | Tema | Evidencia |
|---|---|---|
| 0:00–2:00 | Problema y pregunta de decisión | Una fila por solicitud, periodo abril–julio 2026 y necesidad operativa. |
| 2:00–5:00 | Arquitectura Fase 1 | NYC Open Data, SSIS, esquema estrella y `dw.FactSolicitud`. |
| 5:00–7:00 | ETL y DW | Mostrar el flujo y declarar si la ejecución es en vivo o evidencia fechada. |
| 7:00–12:00 | Minería Fase 2 | P75 = 4,329 minutos, árbol evaluado en prueba, K=3 y 480 perfiles. |
| 12:00–19:00 | Power BI | Abrir `BI/NYC311_Fase3_Propio.pbix`, mostrar fuente SQL, segmentador y tarjetas. |
| 19:00–21:00 | Costos y viabilidad | Presentar supuestos, escenarios y punto de equilibrio sin inventar cifras. |
| 21:00–23:00 | Conclusiones y límites | Explicar 1,293,816 solicitudes, 1,279,792 segmentadas y 14,024 fuera de perfil. |
| 23:00–25:00 | Margen | Preguntas o recuperación de una demostración lenta. |

## Demostración mínima de Power BI

1. Abrir el PBIX propio desde la carpeta `entrega/BI`.
2. Mostrar que la fuente es `bi.vw_solicitudes_segmentadas` y que el modelo usa Import.
3. Leer la tarjeta de recuento distinto: 1,293,816 solicitudes.
4. Seleccionar `Sin perfil K-Means`: la tarjeta debe mostrar 14,024.
5. Retirar el filtro: la tarjeta debe volver a 1,293,816.
6. Explicar que la tendencia mensual cuenta solicitudes; no suma `codigo_solicitud`.

## Preguntas que deben dominar

- Por qué K-Means se aplicó a 480 perfiles y no a solicitudes individuales.
- Por qué 14,024 solicitudes quedan fuera de perfil.
- Por qué NULL en `minutos_resolucion` no significa demora normal.
- Por qué las métricas del árbol son de prueba y no un pronóstico en producción.
- Qué parte del ROI está medida y qué parte depende de supuestos.
