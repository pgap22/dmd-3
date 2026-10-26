/* Validación reproducible de la integración OLAP. No modifica datos. */
USE DW_NYC311;
GO

SELECT
    (SELECT COUNT_BIG(*) FROM dw.FactSolicitud) AS fact_rows,
    (SELECT COUNT_BIG(DISTINCT codigo_solicitud) FROM dw.FactSolicitud) AS fact_requests,
    (SELECT COUNT_BIG(*) FROM bi.PerfilCluster) AS profiles_rows,
    (SELECT COUNT_BIG(*) FROM bi.vw_fact_solicitud_perfil_cluster) AS bridge_rows,
    (SELECT COUNT_BIG(DISTINCT solicitud_key) FROM bi.vw_fact_solicitud_perfil_cluster) AS bridge_requests;
GO

SELECT
    COALESCE(p.cluster_nombre, N'(clave no encontrada)') AS cluster_nombre,
    COUNT_BIG(*) AS solicitudes
FROM bi.vw_fact_solicitud_perfil_cluster AS f
LEFT JOIN bi.vw_perfil_cluster_olap AS p
    ON p.perfil_cluster_key = f.perfil_cluster_key
GROUP BY COALESCE(p.cluster_nombre, N'(clave no encontrada)')
ORDER BY cluster_nombre;
GO

SELECT
    COUNT_BIG(*) AS filas_con_clave_no_existente
FROM bi.vw_fact_solicitud_perfil_cluster AS f
LEFT JOIN bi.vw_perfil_cluster_olap AS p
    ON p.perfil_cluster_key = f.perfil_cluster_key
WHERE p.perfil_cluster_key IS NULL;
GO

SELECT
    MIN(fc.fecha) AS fecha_min,
    MAX(fc.fecha) AS fecha_max,
    COUNT_BIG(*) AS solicitudes_fuera_de_cualquier_perfil
FROM bi.vw_fact_solicitud_perfil_cluster AS f
INNER JOIN dw.DimFecha AS fc
    ON fc.fecha_key = f.fecha_creacion_key
WHERE f.perfil_cluster_key = 0;
GO
