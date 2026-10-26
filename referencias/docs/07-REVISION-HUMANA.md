# Revisión humana de la Fase 3 (sin convertir Codex en juez)

Esto es una **lista corta para personas**, no un generador de notas/evals/ci pipelines. Los pesos son **de la rúbrica docente de Fase 3**.

| Peso | Evidencia que las personas deberían revisar | Señal de falla |
|---:|---|---|
| 25% | Dashboard real, comprensible y estético; KPIs definidos, gráficos adecuados, filtros y drill-down que funcionan | PDF/capturas únicamente; 10 gráficos inconexos; slicers sin efecto |
| 20% | Integración verificable desde `DW_NYC311`, con resultados F2 realmente reproducidos y vinculados; universo fuera de cluster visible | CSVs inventados; 480 perfiles tratados como tickets; joins multiplican solicitudes |
| 15% | Tabla de costos iniciales y recurrentes, supuestos de licencias/tarifas, escenarios de beneficio, ROI o beneficio justificable | cifras monetarias inventadas, tarifas sin fuente, confundir métricas ML con ahorro |
| 30% | Exposición ≤25 min, demo DW/ETL/minería/Power BI, respuestas sólidas sobre P75, KMeans, recall, limitaciones | teoría superficial, demo que no abre, términos mal usados |
| 10% | Memoria F1+F2+F3 fluida, redactada, con evidencia, figuras legibles y fuentes | unión literal de informes, inconsistencia de totales o mala maquetación |

## Revisión práctica en equipo

1. **Datos:** un integrante compara dos consultas SQL con dos tarjetas de Power BI bajo el mismo filtro; confirma total y denominadores.
2. **UX:** un integrante que no creó el tablero encuentra dónde hay más volumen, qué grupo presenta rezago y por qué importa en **menos de dos minutos**.
3. **Integración:** alguien selecciona un clúster y pregunta cuáles solicitudes no fueron segmentadas. El informe debe poder responder honestamente.
4. **Memoria:** lectura en PDF real de una página con tabla, una con diagrama y la sección ROI. No bastan revisión de ortografía y un script.
5. **Defensa:** ensayo cronometrado con la misma máquina, SQL Server y Power BI; anotar 3 fallos humanos y corregirlos.

## Handoff breve que sí debe escribir Codex

```text
ENTREGADO: ruta y formato real de cada archivo.
COMPROBADO: operación exacta ejecutada y resultado observado (sin etiquetas genéricas).
PENDIENTE HUMANO: qué abrir, comprobar visualmente y decidir.
BLOQUEADORES: recursos inaccesibles, credenciales, falta de Desktop, resultados no reproducidos.
```

No crear dashboard de QA, semáforos, cobertura de instrucciones, agentes jueces ni plan infinito de autocorrecciones. **Una comprobación con datos reales y la lectura humana pesan más.**
