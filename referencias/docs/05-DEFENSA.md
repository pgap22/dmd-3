# Defensa oral final: hasta 25 minutos

El docente exige demostrar **ETL breve + modelo dimensional + minería + dashboard** y responder teoría. No permitir que una demo completa del notebook o una consulta pesada consuma la sesión.

## Cronograma propuesto de 23 minutos + 2 minutos de margen

| Tiempo | Tema | Prueba visual mínima |
|---|---|---|
| 0:00–2:00 | Problema NYC311 y pregunta de decisión | Problema, período, unidad de análisis |
| 2:00–5:00 | Arquitectura F1: fuente→SSIS→DW | Diagrama y 1 consulta de `FactSolicitud` |
| 5:00–7:00 | ETL breve y grano dimensional | SSIS **real**, parámetros y resultado o ejecución corta; alternativa evidencia preguardada **declarada** |
| 7:00–12:00 | F2 árbol + K-Means | Umbral P75, recall vs falsos positivos, K=3, 480 perfiles, cobertura y limitaciones |
| 12:00–19:00 | Demo Power BI F3 | Abrir informe, 3 páginas, cambiar slicers, explicar decisiones, mostrar conexión DW |
| 19:00–21:00 | Costos, beneficios y ROI | Tabla de supuestos, comparación de escenarios, incertidumbre |
| 21:00–23:00 | Conclusiones y límites | 2 recomendaciones, no causalidad, propuestas futuras |
| 23:00–25:00 | Margen de tiempo | No planificar contenido nuevo |

El grupo debe ensayar en su **entorno real**. Comprobar si las preguntas del tribunal van dentro o fuera de los 25 minutos y adaptar el reparto, sin sobrepasar el máximo de exposición.

## Orden de demo que funciona

1. **SQL/SSIS**: mostrar la cadena y una ejecución corta controlada solo si no daña datos ni tarda excesivamente; si es demasiado pesada, presentar la última ejecución real con su registro de fecha y dejar explícito que es evidencia, no demo en vivo.
2. **DW**: esquema estrella, grano 1/ticket, medida duración en minutos, dimensión fecha y claves.
3. **Minería**: notebook con salidas efectivamente ejecutadas (evitar repetir GridSearchCV 54 fits); explicar P75, variables y métricas. Mostrar tabla de perfiles del K-Means.
4. **BI**: acción observable: filtrar agencia/borough, segmentar un clúster y comparar volumen+demora. Explicar tickets fuera del universo segmentado.
5. **Decisión**: a partir de esos resultados, recomendar una revisión operativa con criterios medibles, sin afirmar causalidad.

## Preguntas del docente y respuestas que deben dominar

- **¿Por qué un Datawarehouse y no la tabla original?** Para integrar fuentes, conservar modelo consistente y servir análisis transversal; evidenciar grano, dimensiones y ETL real.
- **¿Qué es el P75?** Umbral interno de demora alta: 4,329 minutos calculados de duraciones observadas abril–julio 2026; no es SLA. Solicitudes sin duración quedan sin etiqueta.
- **¿Qué significa Recall 95.15%?** Proporción de demoras altas verdaderas detectadas en el conjunto de prueba; NO precisión de todas las alertas ni garantía futura. 2,982 falsos negativos reportados allí.
- **¿Por qué excluir `minutos_resolucion` de X?** Porque define la etiqueta y se conoce tras el cierre (fuga de información).
- **¿Por qué K-Means no sobre tickets individuales?** Agrupó perfiles operativos formados por agencia, tipo y borough; 480 elegibles tras filtros. No asigna automáticamente todos los tickets.
- **¿Qué significa Silhouette 0.421?** Separación moderada: clusters útiles para investigar, no fronteras perfectas.
- **¿Por qué algunos tickets no tienen clúster?** No pertenecen a un perfil elegible bajo los criterios F2; comprobar conteo actual y dar razón basada en datos.
- **¿Cuáles son las limitaciones temporales?** Solo abril–julio 2026 y partición aleatoria train/test; sin validación temporal, sin prueba causal.
- **¿Es clasificación histórica o predicción operativa?** Distinguir verdad histórica del campo `demora_alta` de `score` que exista realmente. Nunca confundir las dos.
- **¿ROI real?** Si no se implantó en producción, es una **estimación por escenarios**; decir claramente método, supuestos y sensibilidad.
- **¿Power BI se conecta al DW?** Mostrar origen de datos/consulta y actualizar o evidenciar última carga; un CSV aislado no lo prueba.
- **¿Por qué Import frente a DirectQuery?** Import favorece latencia/estabilidad de demo; DirectQuery puede ofrecer datos actuales a costa de consultar la fuente. Exponer el modo real.

## Plan B legítimo

Si falla la red/SQL Server o Power BI Desktop, llevar **capturas de una ejecución real fechada**, PDF exportado real de páginas, notebook ejecutado y DDL/consulta visibles. Explicar honestamente qué funcionó antes y qué falla ahora; **un PDF no sustituye el dashboard interactivo** de la rúbrica. Tener siempre el archivo PBIX/PBIP en la máquina correcta y credenciales verificadas antes del ensayo.

## Evitar el discurso hecho por IA

Cada expositor domina 1–2 decisiones técnicas de las que participó. No memorizar frases genéricas. La conclusión debe enlazar **métrica → riesgo/limitación → acción operativa**. Si el docente pide un dato no medido: "No lo medimos; lo estimaríamos así..." en vez de inventarlo.
