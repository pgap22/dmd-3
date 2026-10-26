/* Validación puntual de cardinalidad y cobertura. Se consulta por mes para
   evitar una solicitud de memoria excesiva en el SQL Server local. */
USE DW_NYC311;
GO
SET NOCOUNT ON;

SELECT N'base' AS fuente, COUNT_BIG(*) AS filas
FROM dw.FactSolicitud;

SELECT N'mining' AS fuente, COUNT_BIG(*) AS filas
FROM mining.vw_dataset_fase2;

SELECT N'perfiles' AS fuente, COUNT_BIG(*) AS filas
FROM bi.PerfilCluster;

SELECT N'bi_mes_04' AS fuente,
       COUNT_BIG(*) AS filas,
       SUM(CASE WHEN es_segmentado = 1 THEN 1 ELSE 0 END) AS segmentadas,
       SUM(CASE WHEN es_segmentado = 0 THEN 1 ELSE 0 END) AS fuera_de_perfil
FROM bi.vw_solicitudes_segmentadas
WHERE mes = 4
OPTION (MAXDOP 1);

SELECT N'bi_mes_05' AS fuente,
       COUNT_BIG(*) AS filas,
       SUM(CASE WHEN es_segmentado = 1 THEN 1 ELSE 0 END) AS segmentadas,
       SUM(CASE WHEN es_segmentado = 0 THEN 1 ELSE 0 END) AS fuera_de_perfil
FROM bi.vw_solicitudes_segmentadas
WHERE mes = 5
OPTION (MAXDOP 1);

SELECT N'bi_mes_06' AS fuente,
       COUNT_BIG(*) AS filas,
       SUM(CASE WHEN es_segmentado = 1 THEN 1 ELSE 0 END) AS segmentadas,
       SUM(CASE WHEN es_segmentado = 0 THEN 1 ELSE 0 END) AS fuera_de_perfil
FROM bi.vw_solicitudes_segmentadas
WHERE mes = 6
OPTION (MAXDOP 1);

SELECT N'bi_mes_07' AS fuente,
       COUNT_BIG(*) AS filas,
       SUM(CASE WHEN es_segmentado = 1 THEN 1 ELSE 0 END) AS segmentadas,
       SUM(CASE WHEN es_segmentado = 0 THEN 1 ELSE 0 END) AS fuera_de_perfil
FROM bi.vw_solicitudes_segmentadas
WHERE mes = 7
OPTION (MAXDOP 1);
GO
