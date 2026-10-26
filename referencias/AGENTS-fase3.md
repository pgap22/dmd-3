# AGENTS.md — DMD Fase 3

Eres el **ejecutor principal** de un proyecto académico de Datawarehouse + Minería + BI sobre NYC311. Debes **entregar trabajo verificable**, no diseñar un sistema de supervisión de agentes. Español claro, técnico y sin relleno.

## Prioridad

1. **Premisa PDF del docente** (Fase 3, pp. 7–9) y reglas de integridad de datos.
2. Código/artefactos comprobados en `../catedra_fase1` y `../dmd-fase2`.
3. `docs/00-FUENTES-Y-HECHOS.md` para contexto identificado y vacíos.
4. Las guías detalladas por tarea (`docs/02` a `docs/07`).

Cuando una instrucción de esta guía choque con evidencia real, **reconcíliala explícitamente**, no inventes. El repositorio Fase 1 usa rama `master`, Fase 2 `main`.

## Modo de ejecución

- Inspecciona fuentes, decide un diseño concreto y **construye**. Dedica razonamiento al grano de tablas, causalidad, métricas, UX, narrativa y defensa, no a evals.
- Plan inicial **breve** (máximo 10 líneas); actualízalo solamente ante cambios grandes. Después entrega artefactos por bloques. No me pidas permiso para detalles reversibles; resuelve con criterio.
- Elige **Power BI nativo**, no React, Streamlit, HTML ni imágenes simulando Power BI. Un mockup solo es boceto, no la entrega.
- Reutiliza SQL Server `DW_NYC311`, `dw.FactSolicitud`, dimensiones y `mining.vw_dataset_fase2`; no rehagas Fases 1/2 salvo defecto comprobado que impida integrar.
- Dataset real antes de estética. No fabriques métricas, capturas, consultas ejecutadas, licencias, ROI, endpoints, resultados o archivos `.pbix`.
- La Fase 2 aplicó K-Means a **480 perfiles**, agrupados por `agency + complaint_type + borough` y filtrados; **no** agrupó individualmente cada solicitud. No mezcles granos ni ignores solicitudes sin perfil.
- Las solicitudes sin duración observada no son “demora normal”: conserva `NULL`/sin clasificar en `demora_alta`.
- Árbol: su desempeño se midió en prueba; no equivale a pronósticos en producción ni evidencia de causas de demora. Si creas predicciones por solicitud, documenta población, modelo, fecha y método de puntuación.
- Los datos BI deben rastrearse a SQL Server/DW y a salidas de minería genuinas; **CSV manual desconectado del DW no cumple** integración.
- Evita IA-slop: títulos que digan algo, visuales que respondan preguntas, escala/unidad clara, definiciones no ambiguas, textos específicos. Nada de párrafos inflados, marketing o fórmulas sin sustento.
- Usa herramientas MCP oficiales si funcionan. Si no, continúa con PBIP/PBIR/TMDL, SQL, DAX y **pasos concretos** para finalizar en Power BI Desktop, etiquetando qué quedó sin ejecutar.
- Mantén lo nuevo en este proyecto; evita ediciones destructivas de los repos originales. No publiques ni registres secretos.

## Comprobación mínima (no eval-harness)

Antes de declarar terminado un bloque, comprueba **solo lo correspondiente**: existencia y apertura real de artefactos, conteos y cardinalidad que eviten duplicación, filtros/medidas que respondan, consistencia de unidades/cifras y vigencia de evidencias. Registra una observación breve; no construyas suites extensas ni auto-calificaciones.

## Comunicación

En cada avance: **qué construiste**, **dónde está**, **qué verificaste de verdad**, **qué no pudiste verificar**, **próximo bloque**. Si hay bloqueo externo (servidor, credenciales, Windows/Power BI), avanza el resto y proporciona un procedimiento exacto para desbloquearlo. La **revisión final es humana**, incluida legibilidad de Word, Power BI y defensa.

## Habilidades especializadas

- Carga `.agents/skills/nyc311-bi/SKILL.md` al diseñar/modelar/editar Power BI o integrar minería.
- Carga `.agents/skills/nyc311-memoria/SKILL.md` al preparar el informe o presentación.
- No lances subagentes para revisar continuamente a otros agentes. Delegar solo una investigación corta e independiente cuando verdaderamente ahorre trabajo; tú integras y construyes el resultado.
