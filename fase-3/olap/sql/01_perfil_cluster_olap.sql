/*
    Integración OLAP Fase 3 - NYC311
    Base: DW_NYC311

    La minería de Fase 2 clasifica perfiles (agency + complaint_type + borough),
    no solicitudes individuales. Estas vistas conservan el grano de una fila
    por solicitud y usan 0 como miembro explícito "Sin perfil K-Means".
*/

USE DW_NYC311;
GO

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'bi')
BEGIN
    EXEC(N'CREATE SCHEMA bi');
END;
GO

/* Índice de apoyo para la búsqueda natural del perfil durante el procesamiento. */
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'bi.PerfilCluster', N'U')
      AND name = N'IX_PerfilCluster_ClaveVigencia'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PerfilCluster_ClaveVigencia
        ON bi.PerfilCluster (agency, complaint_type, borough, periodo_inicio, periodo_fin)
        INCLUDE (perfil_cluster_key, cluster_id_original, cluster_nombre, modelo_version);
END;
GO

/*
    Fuente de la dimensión. Se agrega el miembro 0 para que el hecho pueda
    conservar solicitudes sin perfil sin convertirlas en error de clave.
*/
CREATE OR ALTER VIEW bi.vw_perfil_cluster_olap
AS
SELECT
    CAST(0 AS int) AS perfil_cluster_key,
    CAST(N'(sin perfil)' AS nvarchar(100)) AS agency,
    CAST(N'(sin perfil)' AS nvarchar(500)) AS complaint_type,
    CAST(N'(sin perfil)' AS nvarchar(200)) AS borough,
    CAST(-1 AS int) AS cluster_id_original,
    CAST(N'Sin perfil K-Means' AS nvarchar(120)) AS cluster_nombre,
    CAST(N'Perfil no clasificado por el modelo F2' AS nvarchar(600)) AS perfil_nombre,
    CAST(N'(no disponible)' AS nvarchar(120)) AS modelo_version
UNION ALL
SELECT
    pc.perfil_cluster_key,
    pc.agency,
    pc.complaint_type,
    COALESCE(pc.borough, N'(sin borough)') AS borough,
    pc.cluster_id_original,
    pc.cluster_nombre,
    CAST(CONCAT(
        pc.agency, N' | ', pc.complaint_type, N' | ',
        COALESCE(pc.borough, N'(sin borough)')
    ) AS nvarchar(600)) AS perfil_nombre,
    pc.modelo_version
FROM bi.PerfilCluster AS pc;
GO

/*
    Hecho lógico que el cubo procesa. OUTER APPLY garantiza como máximo un
    perfil por ticket incluso si en el futuro se conservan versiones de modelo
    con ventanas de vigencia solapadas; se escoge la versión más reciente.
*/
CREATE OR ALTER VIEW bi.vw_fact_solicitud_perfil_cluster
AS
SELECT
    f.solicitud_key,
    f.codigo_solicitud,
    f.fecha_creacion_key,
    f.fecha_cierre_key,
    f.agencia_key,
    f.problema_key,
    f.geografia_key,
    f.estado_key,
    f.canal_key,
    f.minutos_resolucion,
    f.latitude,
    f.longitude,
    CAST(COALESCE(pc_match.perfil_cluster_key, 0) AS int) AS perfil_cluster_key
FROM dw.FactSolicitud AS f
INNER JOIN dw.DimFecha AS fc
    ON f.fecha_creacion_key = fc.fecha_key
INNER JOIN dw.DimAgencia AS a
    ON f.agencia_key = a.agencia_key
INNER JOIN dw.DimProblema AS p
    ON f.problema_key = p.problema_key
LEFT JOIN dw.DimGeografia AS g
    ON f.geografia_key = g.geografia_key
OUTER APPLY
(
    SELECT TOP (1)
        pc.perfil_cluster_key
    FROM bi.PerfilCluster AS pc
    WHERE pc.agency = a.agency
      AND pc.complaint_type = p.complaint_type
      AND (pc.borough = g.borough OR (pc.borough IS NULL AND g.borough IS NULL))
      AND fc.fecha BETWEEN pc.periodo_inicio AND pc.periodo_fin
    ORDER BY pc.periodo_fin DESC, pc.modelo_version DESC, pc.perfil_cluster_key DESC
) AS pc_match;
GO

/* Validación de grano y reconciliación de cobertura antes de procesar SSAS. */
SELECT
    COUNT_BIG(*) AS filas_puente,
    COUNT_BIG(DISTINCT solicitud_key) AS solicitudes_distintas,
    COUNT_BIG(DISTINCT codigo_solicitud) AS codigos_distintos,
    SUM(CASE WHEN perfil_cluster_key = 0 THEN 1 ELSE 0 END) AS sin_perfil,
    SUM(CASE WHEN perfil_cluster_key <> 0 THEN 1 ELSE 0 END) AS con_perfil
FROM bi.vw_fact_solicitud_perfil_cluster;
GO

SELECT TOP (1)
    solicitud_key,
    COUNT_BIG(*) AS filas
FROM bi.vw_fact_solicitud_perfil_cluster
GROUP BY solicitud_key
HAVING COUNT_BIG(*) > 1;
GO
