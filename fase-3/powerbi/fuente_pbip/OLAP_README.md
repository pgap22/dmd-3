# Informe Power BI Live — NYC311

## Archivo de apertura

Abrir `olap.pbip` con Power BI Desktop. El proyecto usa una conexión Live al cubo multidimensional:

```text
Data Source=(local)
Initial Catalog=CuboFase1
Cube=DW NYC311
```

La instancia local de Analysis Services debe estar disponible y el cubo debe estar procesado.

## Contenido del informe

- **Panorama del cubo:** recuento de solicitudes por fecha, borough y segmento; tres tarjetas visibles para total, tiempo observado y cobertura.
- **Segmentación K-Means:** volumen de solicitudes por los tres clústeres y por agencia.
- **Diagnóstico operativo:** concentración por agencia y comparación de los cuatro miembros publicados por la dimensión de perfiles, incluyendo `Sin perfil K-Means`.

Los segmentadores se basan en `Fecha Creacion`, `Dim Agencia` y `Dim PerfilCluster`. La medida visual base es `Fact Solicitud Count`, con grano de una fila por solicitud en el grupo de medidas `Fact Solicitud`.

El cubo publica además:

- La jerarquía temporal `Año → Trimestre → Mes → Fecha` en `Dim Fecha`. En el PBIP se materializa como un eje multinivel compatible con Desktop Store; al seleccionar el gráfico aparecen los cuatro niveles y el control `Modo detallado`.
- La medida `Solicitudes con tiempo`, que cuenta únicamente filas con `minutos_resolucion` observado.
- El KPI formal de SSAS `Cobertura de tiempo observado`, con valor `Solicitudes con tiempo / Fact Solicitud Count`, meta analítica `95%` y estado tipo semáforo. La meta es un umbral analítico del proyecto, no un SLA contractual.

## Alcance metodológico

Este informe no agrega DAX local ni presenta una suma de minutos como mediana. El cubo conectado en vivo publica el recuento de solicitudes; la duración observada y las métricas específicas de la minería se mantienen en los artefactos SQL/Python de las fases correspondientes.

## Comprobación realizada

El proyecto se compiló y desplegó desde `fase1/cubo_olap` a `localhost / CuboFase1`; la consulta de SSAS devolvió `1.312.465` solicitudes, `1.248.998` con tiempo observado, valor KPI `0,9516429009`, meta `0,95` y estado `1`. En Power BI Desktop el PBIP abrió con `Conexión dinámica: conectada`, mostró las tres tarjetas y el eje multinivel `Anio, Trimestre, Mes, Fecha`; al activar el control de profundidad se leyó `Modo detallado activado`. También se comprobó que seleccionar un clúster cambia los gráficos relacionados. El PBIP es la fuente editable y reproducible; no se genera aquí un PBIX empaquetado que pueda ocultar la conexión al cubo.
