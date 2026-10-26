# Alcance y plan de construcción de la Fase 3

## La ruta crítica (hacer, no debatir)

### Corte A — integrar datos y hallazgos

1. Confirmar `DW_NYC311`, schemas y conteo por fechas. Si servidor no accesible, preparar SQL de vistas e instrucciones de ejecución, **sin fingir resultado**.
2. Crear `bi` (o similar) con vista base de solicitudes y dimensiones, **sin cambiar grano**.
3. Reproducir del notebook F2 solo lo indispensable para exportar la **tabla de perfiles con clúster** (480 filas esperadas según snapshot, comprobar), con datos y metadatos de versión; importar/cargar al SQL Server como tabla derivada del DW. Relacionarla **por la terna completa** `agency, complaint_type, borough`, resolviendo semántica de `NULL` y colación.
4. Dejar documentados casos sin perfil y evitar joins 1:N. Comparar conteo DW vs vista BI y población cubierta por clúster.
5. Definir si se integrarán además puntuaciones del árbol por ticket o únicamente interpretación/indicadores históricos. **No etiquetar un score no calculado.**

**Salida:** SQL, export/perfiles realmente generados, diccionario y una consulta de comprobación breve.

### Corte B — modelo Power BI funcional

1. Preferir **Import** desde SQL Server para demo académica estable y rápida; DirectQuery es válido si la conexión/performance lo justifican. **No llamar “vivo” al modo Import**.
2. Crear modelo semántico sin relaciones ambiguas: fecha/agencia/problema/geografía/estado/canal → solicitudes, clúster como dimensión correcta o atributo enriquecido mediante join SQL controlado.
3. Medidas explícitas en DAX y formatos correctos (tickets, %, minutos/horas, mediana). Interacciones reales de filtros.
4. Guardar un proyecto real (`.pbip`, PBIR/TMDL) o `.pbix` verdadero. Un fichero generado manualmente no es un PBIX válido.

**Salida:** archivo Power BI abrible; visuales visibles y valores derivados de DW.

### Corte C — dashboard que permita decidir

Diseñar **2–3 páginas máximas**; primera ejecutiva, segunda diagnóstico, tercera minería/segmentación. Más páginas solo si responden decisiones distintas. Integrar al menos un segmentador de clúster con aclaración de cobertura. Construir iterativamente en Power BI, abrir y observar. Evitar visuales decorativos.

**Salida:** navegación simple, jerarquía y demo de filtros/drill-down reales.

### Corte D — memoria técnica y costos

Redactar **un documento nuevo y coherente**, no unir F1+F2 mediante copy/paste. Cubrir arquitectura, extracción/ETL, DW, KDD, integración BI, hallazgos, costos, beneficios, ROI, riesgos y límites. Utilizar evidencia y gráficas originales. Ver `docs/04-COSTOS-Y-MEMORIA.md`.

**Salida:** DOCX/PDF auténticos cuando existan herramientas locales; fuentes editables, tablas y visuales legibles.

### Corte E — defensa y ensayo

Producir PPTX/PDF editables cuando el entorno lo permita, guion cronometrado <=25 min y demo operativa de ETL + DW + minería + dashboard. Preparar respuesta precisa a preguntas de P75, leakage, KMeans, incertidumbre y ROI. Ver `docs/05-DEFENSA.md`.

**Salida:** archivos de presentación, mapa de demo y plan de contingencia.

## Prioridades si falta tiempo

**P0 (no negociable):** integración auténtica DW + resultados minería, Power BI interactivo, explicación creíble y defensa.

**P1:** memoria técnica cuidada, costos/ROI defendibles, navegación y mapa si hay coordenadas útiles.

**P2:** visualizaciones extras, scoring prospectivo, diseño de marca avanzado. **No hacer P2 antes de P0/P1**.

## Estructura orientativa de trabajo generado (crear al producirlo)

```text
entrega/
├── BI/           # archivo(s) PBIP+PBIR+TMDL o PBIX realmente válidos
├── sql/          # vistas BI y mapeos sin alterar el ETL original
├── mineria/      # export de perfiles y proceso reproducible
├── memoria/      # fuente editable + PDF
├── defensa/      # PPTX, guion, apoyo para demostración
└── evidencias/   # capturas REALES, conteos y notas breves
```

**Evitar:** frameworks QA, fake datasets, carpetas `evals`, puntajes autogenerados, 30 versiones finales, fuentes LFS gigantes duplicadas, experimentos nuevos por curiosidad.

## Hitos relativos a la premisa

Con entrega entre **2 y 7 nov 2026**, la integración y el dashboard deben preceder a la redacción/consolidación; la defensa requiere un ensayo con la misma máquina y conexión prevista para el acto. El cronograma real del equipo prevalece.
