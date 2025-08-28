CREATE TABLE ars.dbo.tm60_chatlog (
	idx int NOT NULL IDENTITY(1,1),
	fdnis varchar(8) DEFAULT ('') NOT NULL,
	m_code varchar(3) DEFAULT ('') NOT NULL,
	m_name varchar(20) DEFAULT ('') NOT NULL,
	m_nickname varchar(20) DEFAULT ('') NOT NULL,
	starttm varchar(19) DEFAULT ('') NULL,
	endtm varchar(19) DEFAULT ('') NULL,
	chatstart varchar(19) DEFAULT ('') NULL,
	chatend varchar(19) DEFAULT ('') NULL,
	u_tel varchar(15) DEFAULT ('') NOT NULL,
	t_tel varchar(15) DEFAULT ('') NOT NULL,
	yyyy char(4) DEFAULT ('') NOT NULL,
	mm char(2) DEFAULT ('') NOT NULL,
	dd char(2) DEFAULT ('') NOT NULL,
	hh char(2) DEFAULT ('') NOT NULL,
	fname varchar(17) DEFAULT ('') NOT NULL,
	scode char(1) DEFAULT ('1') NOT NULL,
	platform char(1) DEFAULT ('0') NOT NULL,
	u_id varchar(50) DEFAULT ('') NOT NULL,
	chattm int DEFAULT ((0)) NOT NULL,
	realchattm int DEFAULT ((0)) NOT NULL,
	usepoint int DEFAULT ((0)) NOT NULL,
	fee int DEFAULT ((0)) NOT NULL,
	t_money int DEFAULT ((0)) NOT NULL,
	t2_money real DEFAULT ((0.0)) NOT NULL,
	success int DEFAULT ((0)) NOT NULL,
	u_chk int DEFAULT ((0)) NOT NULL,
	menu int DEFAULT ((0)) NOT NULL,
	call_span int DEFAULT ((0)) NOT NULL,
	calltm int DEFAULT ((0)) NOT NULL,
	unit_use int DEFAULT ((0)) NOT NULL,
	unit_sec int DEFAULT ((0)) NOT NULL,
	unit_fee real DEFAULT ((0.0)) NOT NULL,
	prate int DEFAULT ((0)) NOT NULL,
	call_name varchar(70) DEFAULT ('') NOT NULL,
	CONSTRAINT PK__tm60_chatlog__6FF48C97 PRIMARY KEY (idx)
);
CREATE INDEX idx_dd ON ars.dbo.tm60_chatlog (dd);
CREATE INDEX idx_endtm ON ars.dbo.tm60_chatlog (endtm);
CREATE INDEX idx_fdnis ON ars.dbo.tm60_chatlog (fdnis);
CREATE INDEX idx_hh ON ars.dbo.tm60_chatlog (hh);
CREATE INDEX idx_m_code ON ars.dbo.tm60_chatlog (m_code);
CREATE INDEX idx_m_nickname ON ars.dbo.tm60_chatlog (m_nickname);
CREATE INDEX idx_mm ON ars.dbo.tm60_chatlog (mm);
CREATE INDEX idx_platform ON ars.dbo.tm60_chatlog (platform);
CREATE INDEX idx_scode ON ars.dbo.tm60_chatlog (scode);
CREATE INDEX idx_starttm ON ars.dbo.tm60_chatlog (starttm);
CREATE INDEX idx_success ON ars.dbo.tm60_chatlog (success);
CREATE INDEX idx_u_id ON ars.dbo.tm60_chatlog (u_id);
CREATE INDEX idx_yyyy ON ars.dbo.tm60_chatlog (yyyy);


* 상담사 테이블


CREATE TABLE ars.dbo.tm60_member (
	idx int NOT NULL IDENTITY(1,1),
	m_dnis varchar(8) DEFAULT ('') NOT NULL,
	m_code varchar(3) DEFAULT ('') NOT NULL,
	m_name varchar(20) DEFAULT ('') NOT NULL,
	m_nickname varchar(20) DEFAULT ('') NOT NULL,
	m_tel varchar(20) DEFAULT ('') NOT NULL,
	m_tel1 varchar(20) DEFAULT ('') NOT NULL,
	m_tel2 varchar(20) DEFAULT ('') NOT NULL,
	m_mobile varchar(20) DEFAULT ('') NOT NULL,
	m_state char(1) DEFAULT ('1') NOT NULL,
	m_nextstate varchar(5) DEFAULT ('') NOT NULL,
	m_counselling char(1) DEFAULT ('1') NOT NULL,
	m_id varchar(50) DEFAULT ('') NOT NULL,
	m_passwd varchar(4) DEFAULT ('') NOT NULL,
	m_memo varchar(50) DEFAULT ('') NULL,
	last_chat char(14) DEFAULT ('') NOT NULL,
	chat_level char(1) DEFAULT ('1') NOT NULL,
	class char(1) DEFAULT ('0') NOT NULL,
	turn char(1) DEFAULT ('0') NOT NULL,
	bang char(1) DEFAULT ('1') NOT NULL,
	holdoff char(1) DEFAULT ('0') NOT NULL,
	m_bunho varchar(10) DEFAULT ('1') NOT NULL,
	m_writer int DEFAULT ((0)) NOT NULL,
	m_prate int DEFAULT ((100)) NOT NULL,
	m_fdate datetime NULL,
	CONSTRAINT PK__tm60_member__0B679CE2 PRIMARY KEY (idx)
);
CREATE INDEX idx_bang ON ars.dbo.tm60_member (bang);
CREATE INDEX idx_chat_level ON ars.dbo.tm60_member (chat_level);
CREATE INDEX idx_dnis ON ars.dbo.tm60_member (m_dnis);
CREATE INDEX idx_m_bunho ON ars.dbo.tm60_member (m_bunho);
CREATE INDEX idx_m_code ON ars.dbo.tm60_member (m_code);
CREATE INDEX idx_m_counselling ON ars.dbo.tm60_member (m_counselling);
CREATE INDEX idx_m_name ON ars.dbo.tm60_member (m_name);
CREATE INDEX idx_m_nickname ON ars.dbo.tm60_member (m_nickname);
CREATE INDEX idx_m_state ON ars.dbo.tm60_member (m_state);
CREATE INDEX idx_turn ON ars.dbo.tm60_member (turn);

* 유저 테이블


CREATE TABLE ars.dbo.tm60_users (
	idx int NOT NULL IDENTITY(1,1),
	u_id varchar(50) DEFAULT ('') NOT NULL,
	u_tel varchar(18) DEFAULT ('') NOT NULL,
	u_passwd char(4) DEFAULT ('') NOT NULL,
	u_kname varchar(12) DEFAULT ('') NOT NULL,
	u_memcd char(1) DEFAULT ('1') NOT NULL,
	u_login char(1) DEFAULT ('1') NOT NULL,
	u_state char(1) DEFAULT ('0') NOT NULL,
	u_point int DEFAULT ((0)) NOT NULL,
	u_fdate datetime NULL,
	u_rdate datetime NULL,
	regdate datetime NULL,
	u_memo varchar(255) DEFAULT ('') NOT NULL,
	CONSTRAINT PK__tm60_users__2EE5E349 PRIMARY KEY (idx)
);
CREATE INDEX idx_id ON ars.dbo.tm60_users (u_id);
CREATE INDEX idx_tel ON ars.dbo.tm60_users (u_tel);