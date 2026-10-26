/* ============================================
   BASE DE DATOS
   ============================================ */

CREATE DATABASE DW_NYC311;
GO

USE DW_NYC311;
GO


/* ============================================
   SCHEMAS
   ============================================ */

CREATE SCHEMA raw;
GO

CREATE SCHEMA etl;
GO


/* ============================================
   RAW
   Buffer temporal de la extracción actual
   ============================================ */

CREATE TABLE raw.Solicitud
(
    raw_id BIGINT IDENTITY(1,1) PRIMARY KEY,

    run_id UNIQUEIDENTIFIER NOT NULL,
    extracted_at DATETIME2(0) NOT NULL,

    unique_key NVARCHAR(50) NULL,

    created_date NVARCHAR(50) NULL,
    closed_date NVARCHAR(50) NULL,
    resolution_action_updated_date NVARCHAR(50) NULL,
    due_date NVARCHAR(50) NULL,

    agency NVARCHAR(50) NULL,
    agency_name NVARCHAR(250) NULL,

    complaint_type NVARCHAR(250) NULL,
    descriptor NVARCHAR(500) NULL,
    descriptor_2 NVARCHAR(500) NULL,
    location_type NVARCHAR(250) NULL,

    status NVARCHAR(100) NULL,
    resolution_description NVARCHAR(MAX) NULL,

    borough NVARCHAR(100) NULL,
    incident_zip NVARCHAR(20) NULL,
    incident_address NVARCHAR(500) NULL,
    community_board NVARCHAR(100) NULL,
    council_district NVARCHAR(50) NULL,
    police_precinct NVARCHAR(50) NULL,

    latitude NVARCHAR(50) NULL,
    longitude NVARCHAR(50) NULL,
    bbl NVARCHAR(50) NULL,

    open_data_channel_type NVARCHAR(100) NULL
);
GO


/* ============================================
   AUDITORÍA DE EJECUCIONES ETL
   ============================================ */

CREATE TABLE etl.Ejecucion
(
    run_id UNIQUEIDENTIFIER PRIMARY KEY,

    inicio DATETIME2(0) NOT NULL,
    fin DATETIME2(0) NULL,

    filas_extraidas INT NOT NULL DEFAULT 0,
    filas_validas INT NOT NULL DEFAULT 0,
    filas_rechazadas INT NOT NULL DEFAULT 0,

    estado NVARCHAR(20) NOT NULL,

    detalle NVARCHAR(1000) NULL,

    CONSTRAINT CK_Ejecucion_Estado
        CHECK (estado IN ('RUNNING', 'SUCCESS', 'FAILED'))
);
GO


ALTER TABLE raw.Solicitud
ADD CONSTRAINT DF_raw_Solicitud_extracted_at
DEFAULT SYSDATETIME() FOR extracted_at;