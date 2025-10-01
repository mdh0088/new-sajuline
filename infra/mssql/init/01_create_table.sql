-- tm60_chatlog 테이블 생성
USE ars;
GO

CREATE TABLE dbo.tm60_chatlog (
    idx int IDENTITY(1,1) NOT NULL,
    fdnis varchar(8) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    m_code varchar(3) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    m_name varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    m_nickname varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    starttm varchar(19) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NULL,
    endtm varchar(19) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NULL,
    chatstart varchar(19) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NULL,
    chatend varchar(19) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NULL,
    u_tel varchar(15) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    t_tel varchar(15) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    yyyy char(4) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    mm char(2) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    dd char(2) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    hh char(2) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    fname varchar(17) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    scode char(1) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '1' NOT NULL,
    platform char(1) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '0' NOT NULL,
    u_id varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    chattm int DEFAULT 0 NOT NULL,
    realchattm int DEFAULT 0 NOT NULL,
    usepoint int DEFAULT 0 NOT NULL,
    fee int DEFAULT 0 NOT NULL,
    t_money int DEFAULT 0 NOT NULL,
    t2_money real DEFAULT 0.0 NOT NULL,
    success int DEFAULT 0 NOT NULL,
    u_chk int DEFAULT 0 NOT NULL,
    menu int DEFAULT 0 NOT NULL,
    call_span int DEFAULT 0 NOT NULL,
    calltm int DEFAULT 0 NOT NULL,
    unit_use int DEFAULT 0 NOT NULL,
    unit_sec int DEFAULT 0 NOT NULL,
    unit_fee real DEFAULT 0.0 NOT NULL,
    prate int DEFAULT 0 NOT NULL,
    call_name varchar(70) COLLATE SQL_Latin1_General_CP1_CI_AS DEFAULT '' NOT NULL,
    CONSTRAINT PK__tm60_chatlog__6FF48C97 PRIMARY KEY (idx)
);
GO

PRINT 'tm60_chatlog 테이블 생성 완료';
GO