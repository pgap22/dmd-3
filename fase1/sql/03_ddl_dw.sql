USE DW_NYC311;
GO


CREATE SCHEMA dw;
GO

/* =========================================================
   DIMENSIÓN: AGENCIA
   ========================================================= */
CREATE TABLE dw.DimAgencia (
    agencia_key INT IDENTITY(1,1) PRIMARY KEY,

    agency NVARCHAR(50) NOT NULL,
    agency_name NVARCHAR(250) NULL,

    CONSTRAINT UQ_DimAgencia
        UNIQUE (agency)
);
GO


/* =========================================================
   DIMENSIÓN: ESTADO
   ========================================================= */
CREATE TABLE dw.DimEstado (
    estado_key INT IDENTITY(1,1) PRIMARY KEY,

    status NVARCHAR(100) NOT NULL,

    CONSTRAINT UQ_DimEstado
        UNIQUE (status)
);
GO


/* =========================================================
   DIMENSIÓN: CANAL
   ========================================================= */
CREATE TABLE dw.DimCanal (
    canal_key INT IDENTITY(1,1) PRIMARY KEY,

    open_data_channel_type NVARCHAR(100) NOT NULL,

    CONSTRAINT UQ_DimCanal
        UNIQUE (open_data_channel_type)
);
GO


/* =========================================================
   DIMENSIÓN: PROBLEMA
   ========================================================= */
CREATE TABLE dw.DimProblema (
    problema_key INT IDENTITY(1,1) PRIMARY KEY,

    complaint_type NVARCHAR(250) NOT NULL,
    descriptor NVARCHAR(500) NULL,
    descriptor_2 NVARCHAR(500) NULL
);
GO



/* =========================================================
   DIMENSIÓN: GEOGRAFÍA
   ========================================================= */
CREATE TABLE dw.DimGeografia (
    geografia_key INT IDENTITY(1,1) PRIMARY KEY,

    borough NVARCHAR(100) NULL,
    incident_zip NVARCHAR(20) NULL,
    community_board NVARCHAR(100) NULL,
    council_district INT NULL,
    police_precinct NVARCHAR(50) NULL
);
GO


/* =========================================================
   DIMENSIÓN: FECHA
   Jerarquía OLAP:
   Año → Trimestre → Mes → Día
   ========================================================= */
CREATE TABLE dw.DimFecha (
    fecha_key INT PRIMARY KEY,       -- YYYYMMDD

    fecha DATE NOT NULL,

    anio SMALLINT NOT NULL,
    trimestre TINYINT NOT NULL,

    mes TINYINT NOT NULL,
    nombre_mes NVARCHAR(20) NOT NULL,

    dia TINYINT NOT NULL,
    dia_semana TINYINT NOT NULL,
    nombre_dia NVARCHAR(20) NOT NULL,

    CONSTRAINT UQ_DimFecha
        UNIQUE (fecha)
);
GO


/* =========================================================
   TABLA DE HECHOS: SOLICITUD
   Granularidad:
   1 fila = 1 solicitud 311
   ========================================================= */
CREATE TABLE dw.FactSolicitud (
    solicitud_key BIGINT IDENTITY(1,1) PRIMARY KEY,

    codigo_solicitud BIGINT NOT NULL,

    /* Dimensión tiempo */
    fecha_creacion_key INT NOT NULL,
    fecha_cierre_key INT NULL,

    /* Dimensiones */
    agencia_key INT NOT NULL,
    problema_key INT NOT NULL,
    geografia_key INT NULL,
    estado_key INT NOT NULL,
    canal_key INT NULL,

    /* Medida */
    minutos_resolucion INT NULL,

    /* Coordenada exacta de la solicitud */
    latitude DECIMAL(18,15) NULL,
    longitude DECIMAL(18,15) NULL,

    CONSTRAINT UQ_FactSolicitud
        UNIQUE (codigo_solicitud),

    CONSTRAINT FK_FactSolicitud_FechaCreacion
        FOREIGN KEY (fecha_creacion_key)
        REFERENCES dw.DimFecha(fecha_key),

    CONSTRAINT FK_FactSolicitud_FechaCierre
        FOREIGN KEY (fecha_cierre_key)
        REFERENCES dw.DimFecha(fecha_key),

    CONSTRAINT FK_FactSolicitud_Agencia
        FOREIGN KEY (agencia_key)
        REFERENCES dw.DimAgencia(agencia_key),

    CONSTRAINT FK_FactSolicitud_Problema
        FOREIGN KEY (problema_key)
        REFERENCES dw.DimProblema(problema_key),

    CONSTRAINT FK_FactSolicitud_Geografia
        FOREIGN KEY (geografia_key)
        REFERENCES dw.DimGeografia(geografia_key),

    CONSTRAINT FK_FactSolicitud_Estado
        FOREIGN KEY (estado_key)
        REFERENCES dw.DimEstado(estado_key),

    CONSTRAINT FK_FactSolicitud_Canal
        FOREIGN KEY (canal_key)
        REFERENCES dw.DimCanal(canal_key)
);
GO
