USE DW_NYC311;
GO

CREATE SCHEMA stg;
GO

CREATE TABLE stg.Solicitud
(
    unique_key BIGINT NOT NULL,

    created_date DATETIME2(0) NOT NULL,
    closed_date DATETIME2(0) NULL,
    resolution_action_updated_date DATETIME2(0) NULL,
    due_date DATETIME2(0) NULL,

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

    council_district INT NULL,
    police_precinct INT NULL,

    latitude DECIMAL(10,7) NULL,
    longitude DECIMAL(10,7) NULL,
    bbl BIGINT NULL,

    open_data_channel_type NVARCHAR(100) NULL,

    run_id UNIQUEIDENTIFIER NOT NULL,

    CONSTRAINT PK_stg_Solicitud
        PRIMARY KEY (unique_key)
);
GO

ALTER TABLE stg.Solicitud
ALTER COLUMN police_precinct NVARCHAR(50) NULL;
GO

ALTER TABLE stg.Solicitud
ALTER COLUMN latitude DECIMAL(18,15) NULL;
GO


ALTER TABLE stg.Solicitud
ALTER COLUMN longitude DECIMAL(18,15) NULL;