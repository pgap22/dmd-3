/* ============================================
   LIMPIEZA COMPLETA DEL PROYECTO DW
   ============================================ */

/* Primero FACT por las FK */
DELETE FROM dw.FactSolicitud;

/* Luego dimensiones */
DELETE FROM dw.DimProblema;
DELETE FROM dw.DimGeografia;
DELETE FROM dw.DimAgencia;
DELETE FROM dw.DimEstado;
DELETE FROM dw.DimCanal;
DELETE FROM dw.DimFecha;

/* Reiniciar IDENTITY de dimensiones/fact */
DBCC CHECKIDENT ('dw.FactSolicitud', RESEED, 0);
DBCC CHECKIDENT ('dw.DimProblema', RESEED, 0);
DBCC CHECKIDENT ('dw.DimGeografia', RESEED, 0);
DBCC CHECKIDENT ('dw.DimAgencia', RESEED, 0);
DBCC CHECKIDENT ('dw.DimEstado', RESEED, 0);
DBCC CHECKIDENT ('dw.DimCanal', RESEED, 0);

/* Limpiar STG y RAW */
TRUNCATE TABLE stg.Solicitud;
TRUNCATE TABLE raw.Solicitud;

/* Limpiar auditoría */
DELETE FROM etl.Ejecucion;