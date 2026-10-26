/*
    Vista analitica y validaciones para la Fase 2.
    Ejecutar en SQL Server con autenticacion de Windows.
*/

USE DW_NYC311;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'mining')
BEGIN
    EXEC(N'CREATE SCHEMA mining');
END;
GO

CREATE OR ALTER VIEW mining.vw_dataset_fase2
AS
WITH resolution_percentile AS
(
    SELECT DISTINCT
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY f.minutos_resolucion) OVER () AS p75_minutos_resolucion
    FROM dw.FactSolicitud AS f
    WHERE f.minutos_resolucion IS NOT NULL
)
SELECT
    f.codigo_solicitud,
    a.agency,
    p.complaint_type,
    g.borough,
    e.status,
    c.open_data_channel_type,
    fc.anio,
    fc.mes,
    fc.dia_semana,
    f.minutos_resolucion,
    CASE
        WHEN f.minutos_resolucion > rp.p75_minutos_resolucion THEN 1
        WHEN f.minutos_resolucion IS NOT NULL THEN 0
        ELSE NULL
    END AS demora_alta,
    f.latitude,
    f.longitude
FROM dw.FactSolicitud AS f
CROSS JOIN resolution_percentile AS rp
INNER JOIN dw.DimFecha AS fc
    ON f.fecha_creacion_key = fc.fecha_key
INNER JOIN dw.DimAgencia AS a
    ON f.agencia_key = a.agencia_key
INNER JOIN dw.DimProblema AS p
    ON f.problema_key = p.problema_key
LEFT JOIN dw.DimGeografia AS g
    ON f.geografia_key = g.geografia_key
INNER JOIN dw.DimEstado AS e
    ON f.estado_key = e.estado_key
LEFT JOIN dw.DimCanal AS c
    ON f.canal_key = c.canal_key;
GO

/* Conteo de filas del hecho y de la vista. */
SELECT COUNT_BIG(*) AS fact_rows
FROM dw.FactSolicitud;

SELECT COUNT_BIG(*) AS view_rows
FROM mining.vw_dataset_fase2;

/* Validacion de la clasificacion de demora. */
SELECT
    COUNT_BIG(*) AS total,
    SUM(CASE WHEN demora_alta = 1 THEN 1 ELSE 0 END) AS demora_alta,
    SUM(CASE WHEN demora_alta = 0 THEN 1 ELSE 0 END) AS normal,
    SUM(CASE WHEN demora_alta IS NULL THEN 1 ELSE 0 END) AS sin_clasificar
FROM mining.vw_dataset_fase2;

/* Validacion de nulos relevantes. */
SELECT
    SUM(CASE WHEN minutos_resolucion IS NULL THEN 1 ELSE 0 END) AS nulos_minutos,
    SUM(CASE WHEN latitude IS NULL THEN 1 ELSE 0 END) AS nulos_latitude,
    SUM(CASE WHEN longitude IS NULL THEN 1 ELSE 0 END) AS nulos_longitude
FROM mining.vw_dataset_fase2;
