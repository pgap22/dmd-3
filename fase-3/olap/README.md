# Integración OLAP de la segmentación K-Means

## Diseño

La minería de Fase 2 clasifica perfiles definidos por `agency + complaint_type + borough`. No se convierte cada solicitud en un perfil nuevo. La tabla `bi.PerfilCluster` conserva la salida de Python y el cubo incorpora la dimensión `Dim PerfilCluster`.

El grupo de medidas `Fact Solicitud` no se une directamente a `bi.PerfilCluster`. Su partición usa `bi.vw_fact_solicitud_perfil_cluster`, una vista 1:1 basada en `dw.FactSolicitud` que agrega `perfil_cluster_key` mediante la clave natural del perfil y la ventana de vigencia del modelo. Si no existe perfil, la clave es `0`, miembro explícito `Sin perfil K-Means`.

Esto conserva el grano del hecho: una solicitud sigue contando una sola vez. La vista usa `OUTER APPLY` para evitar multiplicación si en el futuro hay versiones solapadas del modelo.

## Artefactos

- `fase1/cubo_olap/Dim PerfilCluster.dim`: dimensión SSAS multidimensional.
- `fase1/cubo_olap/DW NYC311.dsv`: incorpora las dos vistas al Data Source View.
- `fase1/cubo_olap/DW NYC311.cube`: relaciona el nuevo atributo con el grupo `Fact Solicitud`.
- `fase1/cubo_olap/DW NYC311.partitions`: procesa el puente 1:1.
- `fase-3/olap/sql/01_perfil_cluster_olap.sql`: despliega vistas e índice de apoyo.
- `fase-3/olap/sql/02_validacion_perfil_cluster_olap.sql`: valida cobertura, cardinalidad y claves.
- `fase-3/olap/mdx/01_validacion_cubo_perfil_cluster.mdx`: consultas MDX para demostrar la dimensión y reconciliar el total.

## Orden de ejecución

1. Ejecutar `01_perfil_cluster_olap.sql` en `DW_NYC311` con la misma cuenta de Windows usada por el proyecto.
2. Abrir `fase1/cubo_olap/CuboFase1.slnx` en Visual Studio/SSDT y comprobar que el DSV reconoce `bi.vw_perfil_cluster_olap` y `bi.vw_fact_solicitud_perfil_cluster`.
3. Construir y desplegar el proyecto SSAS multidimensional.
4. Procesar primero `Dim PerfilCluster` y después el cubo completo. El estado de los XML del proyecto es `Unprocessed` hasta ejecutar este paso en el servidor SSAS.
5. Ejecutar `02_validacion_perfil_cluster_olap.sql` y conservar su salida como evidencia de la defensa.

La validación local del puente reconcilió `FactSolicitud` con 1,312,465 filas y solicitudes distintas. El cubo local `CuboFase1`, instancia `localhost`, también fue desplegado y procesado el 26 de octubre de 2026; MDX devolvió una única categoría `Sin perfil K-Means` con 14,310 solicitudes. Si se despliega en otra máquina, debe repetirse el procesamiento y conservar la salida de `02_validacion_perfil_cluster_olap.sql` junto con las consultas MDX.
