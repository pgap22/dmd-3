# Power BI — NYC311 Fase 3

## Archivo que se abre

`NYC311_Fase3_Final.pbix` es el único PBIX que se presenta. El informe está compuesto por tres páginas 16:9:

1. **Panorama ciudadano:** volumen, tiempos observados, demora alta y solicitudes sin duración.
2. **Dónde concentrar capacidad:** medianas observadas, agencias, boroughs, canales y estados.
3. **Segmentación y valor operativo:** perfiles K-Means, priorización CART, solicitudes fuera de perfil y acciones de capacidad.

## Integración comprobable

El modelo consume SQL Server `DW_NYC311` mediante `bi.vw_solicitudes_segmentadas`. La vista conserva una fila por solicitud, integra los perfiles por `agency + complaint_type + borough` y mantiene `Sin perfil K-Means` para las 14,310 solicitudes que no pertenecen a los 481 perfiles elegibles.

El universo completo disponible es de 1,312,465 solicitudes, con registros entre enero y julio de 2026 (enero y abril–julio). Las 63,467 solicitudes sin duración observada permanecen como `NULL`; no se imputan a cero ni se interpretan como demora normal.

## Fuente editable

`fuente_pbip/` contiene el proyecto PBIP con la definición PBIR del informe y el modelo TMDL. `build_nyc311_pbir.py`, `medidas.dax`, `modelo_semantico.md`, `sql/` y `mineria/` documentan cómo se construyó y cómo se puede revisar.

## Defensa

Abrir el PBIX, volver a la vista global y probar el filtro de `BRONX`; el reporte de validación registra el resultado esperado de la interacción. La verificación de filtros requiere Power BI Desktop y el servidor SQL del entorno de ejecución. Los costos y el ROI son escenarios estimados, no evidencia de ahorro realizado.
