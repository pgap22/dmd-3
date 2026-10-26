# Modelo semántico de Fase 3

## Tabla de consumo

`bi.vw_solicitudes_segmentadas` tiene grano de una fila por `codigo_solicitud` y combina:

- datos de la vista `mining.vw_dataset_fase2`;
- atributos de solicitud y coordenadas;
- `cluster_id_original` y `cluster_nombre_modelado` cuando existe perfil;
- `cluster_nombre = Sin perfil K-Means` para los no elegibles;
- `es_segmentado` para distinguir cobertura.

## Campos que deben ser visibles

| Campo | Uso | Unidad o semántica |
|---|---|---|
| `codigo_solicitud` | conteo distinto | identificador de solicitud |
| `minutos_resolucion` | mediana y filtros | minutos observados; NULL no es cero |
| `demora_alta` | tasa histórica | 1 si supera P75=4,329; NULL sin duración |
| `cluster_nombre` | segmentador | tres grupos F2 o `Sin perfil K-Means` |
| `es_segmentado` | cobertura | bit 1/0 |
| `modelo_version` | trazabilidad | versión y ventana del modelo |
| `mes`, `anio` | tendencia | periodo abril–julio 2026 |

No crear relaciones muchos-a-muchos por `agency`, `complaint_type` o `borough` en forma independiente. Para la demo académica se puede consumir la vista desnormalizada como una tabla única, documentando que conserva el linaje del DW.
