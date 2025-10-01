-- ARS 데이터베이스 생성
USE master;
GO

-- ARS 데이터베이스가 존재하면 삭제
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'ars')
BEGIN
    ALTER DATABASE ars SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE ars;
END
GO

-- ARS 데이터베이스 생성
CREATE DATABASE ars
COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

USE ars;
GO

PRINT 'ARS 데이터베이스 생성 완료';
GO