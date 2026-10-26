# Integración DWH → minería → Power BI (lo más importante)

## El modelo no son tres CSVs pegados

Cadena esperada:

```text
NYC Open Data → SSIS (F1) → raw.Solicitud → stg.Solicitud
                         → dw.FactSolicitud (+ dimensiones)
                         → mining.vw_dataset_fase2 → dataset minería (F2)
                         → modelo árbol / perfiles K-Means
                         → persistencia BI con trazabilidad (F3)
                         → Power BI (modelo + reporte)
```

El **origen principal** del dashboard es SQL Server `DW_NYC311`, no un CSV estático desacoplado. Los resultados F2 también deben venir de cálculos **reproducibles** del notebook y estar vinculados al DW.

## Granos y reglas obligatorias

| Objeto | Grano | Acción permitida |
|---|---|---|
| `dw.FactSolicitud` | 1 fila/ticket | Fuente de todas las métricas de casos |
| `dw.DimFecha` | 1 fecha | Filtrar creación; cierre requiere relación diferenciada |
| `mining.vw_dataset_fase2` | 1 fila/ticket **si joins no duplican** | Fuente de entrenamiento/explicación, confirmar conteo |
| `profiles` (notebook F2) | 1 tupla agencia+problema+borough elegible | Fuente de **segmentación de perfiles**, no de todos los tickets |
| `cluster_summary` | 1 fila/clúster | Contexto explicativo, no dimensión para asignar tickets sin puente |
| `score de árbol` (si se implementa) | 1 fila/ticket puntuado, con `model_version` y fecha | Solo si fue calculado realmente, con predictores válidos |

### Sobre los 14,024 casos sin clúster

F2 reportó 1,293,816 solicitudes; los tres grupos suman 1,279,792. **Diferencia esperada: 14,024**; la causa probable es el filtro de perfiles, pero debe **comprobarse**, no afirmarse como hecho causal. Usar categoría visible `Sin perfil K-Means` (no inventar un cuarto clúster) y una nota de universo elegible. Ninguna página con slicer de clúster debe dar a entender cobertura 100%.

### Sobre los porcentajes de la Fase 2

`raw_cluster_summary` calcula medias por **perfil**, no necesariamente tasas ponderadas por número de solicitudes. **No presentar** su `porcentaje_demora` como porcentaje global de tickets del clúster si no se recalcula con numerador/denominador al nivel ticket. Dos métricas legítimas distintas:

1. **Promedio simple entre perfiles**: reproducir exactamente la Fase 2; etiqueta "promedio entre perfiles".
2. **Tasa ponderada por tickets**: número de tickets con demora alta / tickets clasificados dentro del grupo; etiqueta "tasa de tickets"; deja fuera `NULL` del denominador.

Elegir y dejar clara la definición.

## Entidades BI recomendadas

- `bi.vw_solicitudes`: select del hecho + atributos útiles de dimensiones; incluye `codigo_solicitud`, claves de fecha, agencia, tipo de queja, borough, estado, canal, duración, latitud/longitud, `demora_alta` con semántica compatible F2 (idealmente proveniente de `mining.vw_dataset_fase2` o calculada bajo **mismo P75 y corte**). No duplicar IDs.
- `bi.PerfilCluster` (tabla persistida): columnas `agency`, `complaint_type`, `borough`, `cluster_id_original`, `cluster_nombre`, `solicitudes`, `mediana_resolucion`, `porcentaje_demora`, `porcentaje_sin_resolucion`, `modelo_version`, `periodo_inicio`, `periodo_fin`. Una fila por terna elegible.
- `bi.vw_solicitudes_segmentadas`: `LEFT JOIN` desde solicitudes hacia `bi.PerfilCluster` por **las tres categorías completas**, normalizando valores nulos de forma idéntica a Python (evitar colisiones con valores reales), garantizando 1:0/1; exponer `cluster_nombre` con `Sin perfil K-Means` en los no elegibles, pero también un flag `es_segmentado`.
- **Opcional** `bi.ScoreSolicitud`: generado desde el pipeline ya entrenado o recalculado, con fecha de scoring, `prediccion_demora_alta`, `probabilidad_demora_alta` y **versiones**. Debe distinguirse de verdad histórica `demora_alta`.

En un modelo Power BI estilo estrella, no crear relaciones muchos-a-muchos ambiguas por `borough`, `agency` o `complaint_type` por separado. Si se importa `vw_solicitudes_segmentadas` como tabla única para una demo académica, documentar que es una vista **desnormalizada del DW** y conservar el diagrama lógico original.

## Procedimiento de minería → BI

1. Abrir `../dmd-fase2/notebooks/fase2_dmd_nyc311.ipynb` y confirmar diferencias con el ejecutado.
2. Obtener el CSV real mediante **Git LFS**, o extraer otra vez `mining.vw_dataset_fase2` desde el DW. No leer como CSV las 3 líneas del puntero LFS.
3. Reutilizar transformación F2: `groupby` (incluyendo nulos), mínimo de 100 solicitudes, eliminación de perfiles sin mediana/porcentaje de demora, `log1p`, `StandardScaler`, `KMeans(n_clusters=3, random_state=42, n_init=10)`, y **renombrado por orden de mediana**. Si se decide no reajustar, reutilizar un resultado del notebook realmente ejecutado y registrarlo; no mezclar modelos.
4. Exportar la tabla de **480 perfiles** o la cantidad verificada; importarla en SQL Server con `model_version` y ventana de datos. No editar manualmente la asignación.
5. JOIN SQL contra DW y comprobar conteos/unicidad. **Si un join multiplica filas, no avanzar a Power BI.**
6. Construir Power BI desde el DW o vista BI. Las medidas provienen de la fact; la etiqueta cluster proviene de la salida F2. Documentar fechas, transformaciones y población excluida.

## 4 comprobaciones puntuales (no framework)

- `COUNT(DISTINCT codigo_solicitud) = COUNT(*)` en vista final y debe coincidir con el número original al mismo filtro temporal.
- `bi.PerfilCluster` sin duplicados por tupla; si hay nulos usar igualdad nulo-segura y respetar normalizaciones/collations.
- Cobertura `es_segmentado` + `no segmentado` = total de tickets; segmentación de F2 reproducida solo para el snapshot correspondiente.
- Cambio de slicer de clúster altera **los mismos KPIs**; la suma de grupos más no segmentados reconcilia el total sin duplicar.

El equipo realizará revisión humana de resultados con SQL y pantallas abiertas; los scripts breves anteriores son **sanidad de datos**, no una suite de evaluaciones.

## Tiempos y límites que no deben confundirse

- `minutos_resolucion` es tiempo observado, no tiempo pronosticado. `NULL` no equivale a 0.
- P75=4,329 minutos es una regla histórica calculada sobre el período F2; si los datos crecen, decidir explícitamente si se **congela el umbral F2** o se recalcula para un nuevo período. No comparar etiquetas diferentes sin aviso.
- "Sin resolución registrada" no siempre equivale a reclamo "abierto" según estado; distinguir ambos campos.
- Las predicciones futuras deben evitar fugas temporales y no incluir datos posteriores al momento de predicción. Los resultados reportados en F2 provienen de una partición aleatoria 80/20, **no constituyen prueba de generalización temporal**.
- La clasificación por tipo de queja/agencia es **asociación predictiva**, no prueba de causalidad.
