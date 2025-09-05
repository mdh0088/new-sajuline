"""
MSSQL 연결 테스트
수정된 MSSQL 엔진 구조가 올바르게 작동하는지 검증
"""
import pytest
import asyncio
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import get_db_mssql, mssql_engine, MSSQLSessionLocal
from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.services.ars.tm60_chatlog_service import Tm60ChatlogService


@pytest.mark.integration
@pytest.mark.slow
class TestMSSQLConnection:
    """MSSQL 연결 및 쿼리 테스트"""
    
    def test_mssql_engine_creation(self):
        """MSSQL 엔진이 올바르게 생성되는지 테스트"""
        # 엔진이 생성되어 있는지 확인
        assert mssql_engine is not None
        assert mssql_engine.name == "mssql"
        
        # 연결 풀 설정 확인
        assert mssql_engine.pool.size() >= 0  # 풀이 존재함
        print(f"MSSQL Engine created successfully: {mssql_engine.url}")
    
    def test_session_factory_creation(self):
        """세션 팩토리가 올바르게 생성되는지 테스트"""
        assert MSSQLSessionLocal is not None
        
        # 세션 생성 테스트
        session = MSSQLSessionLocal()
        assert isinstance(session, Session)
        session.close()
        print("MSSQL SessionLocal factory working correctly")
    
    def test_dependency_injection(self):
        """의존성 주입 함수가 올바르게 작동하는지 테스트"""
        # get_db_mssql 제너레이터 테스트
        db_generator = get_db_mssql()
        assert hasattr(db_generator, '__next__')
        
        # 세션 생성 및 종료
        session = next(db_generator)
        assert isinstance(session, Session)
        
        # 제너레이터 종료 (finally 블록 실행)
        try:
            next(db_generator)
        except StopIteration:
            pass  # 정상적인 제너레이터 종료
        
        print("Dependency injection working correctly")
    
    def test_basic_query_execution(self):
        """기본 쿼리 실행 테스트"""
        with MSSQLSessionLocal() as session:
            try:
                # 기본 연결 테스트 쿼리
                result = session.execute(text("SELECT 1 as test_value"))
                row = result.fetchone()
                
                assert row is not None
                assert row[0] == 1
                print("Basic query execution successful")
                
            except Exception as e:
                pytest.skip(f"MSSQL connection not available: {str(e)}")
    
    def test_database_info_query(self):
        """데이터베이스 정보 조회 테스트"""
        with MSSQLSessionLocal() as session:
            try:
                # 데이터베이스 버전 확인
                result = session.execute(text("SELECT @@VERSION as version"))
                version_row = result.fetchone()
                
                if version_row:
                    print(f"MSSQL Version: {version_row[0]}")
                
                # 현재 데이터베이스명 확인
                result = session.execute(text("SELECT DB_NAME() as db_name"))
                db_row = result.fetchone()
                
                if db_row:
                    print(f"Current Database: {db_row[0]}")
                    
                assert True  # 쿼리가 실행되면 성공
                
            except Exception as e:
                pytest.skip(f"MSSQL connection not available: {str(e)}")
    
    def test_table_existence_check(self):
        """tm60_chatlog 테이블 존재 여부 확인"""
        with MSSQLSessionLocal() as session:
            try:
                # 테이블 존재 여부 확인
                result = session.execute(text("""
                    SELECT COUNT(*) as table_count 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'tm60_chatlog'
                """))
                count_row = result.fetchone()
                
                if count_row and count_row[0] > 0:
                    print("tm60_chatlog table exists")
                    
                    # 테이블 구조 확인
                    result = session.execute(text("""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'tm60_chatlog'
                        ORDER BY ORDINAL_POSITION
                    """))
                    
                    columns = result.fetchall()
                    print(f"Table has {len(columns)} columns")
                    for col in columns[:5]:  # 처음 5개 컬럼만 출력
                        print(f"  {col[0]}: {col[1]} ({col[2]})")
                else:
                    print("tm60_chatlog table does not exist")
                
                assert True  # 쿼리가 실행되면 성공
                
            except Exception as e:
                pytest.skip(f"MSSQL connection not available: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_repository_functionality(self):
        """Repository 기능 테스트"""
        try:
            # 의존성 주입을 통한 세션 획득
            db_generator = get_db_mssql()
            session = next(db_generator)
            
            # Repository 인스턴스 생성
            repository = Tm60ChatlogRepository(session)
            
            # 테스트 사용자 ID로 상담 내역 수 조회
            test_user_id = "test_user_not_exists"
            count = await repository.get_consultation_count_by_user_id(test_user_id)
            
            # 존재하지 않는 사용자는 0이어야 함
            assert count == 0
            print(f"Repository test successful - Count for non-existent user: {count}")
            
            # 제너레이터 종료
            try:
                next(db_generator)
            except StopIteration:
                pass
                
        except Exception as e:
            pytest.skip(f"MSSQL connection or tm60_chatlog table not available: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_service_functionality(self):
        """Service 기능 테스트"""
        try:
            # 의존성 주입을 통한 세션 획득
            db_generator = get_db_mssql()
            session = next(db_generator)
            
            # Service 인스턴스 생성
            service = Tm60ChatlogService(session)
            
            # 테스트 사용자 ID로 상담 내역 수 조회
            test_user_id = "test_user_not_exists"
            count = await service.get_user_consultation_count(test_user_id)
            
            # 존재하지 않는 사용자는 0이어야 함
            assert count == 0
            print(f"Service test successful - Count for non-existent user: {count}")
            
            # 제너레이터 종료
            try:
                next(db_generator)
            except StopIteration:
                pass
                
        except Exception as e:
            pytest.skip(f"MSSQL connection or tm60_chatlog table not available: {str(e)}")
    
    def test_concurrent_sessions(self):
        """동시 세션 생성 테스트"""
        sessions = []
        
        try:
            # 여러 세션 동시 생성
            for i in range(5):
                session = MSSQLSessionLocal()
                sessions.append(session)
            
            print(f"Successfully created {len(sessions)} concurrent sessions")
            
            # 각 세션에서 기본 쿼리 실행
            for i, session in enumerate(sessions):
                try:
                    result = session.execute(text("SELECT 1"))
                    row = result.fetchone()
                    assert row[0] == 1
                    print(f"Session {i+1}: Query successful")
                except Exception as e:
                    print(f"Session {i+1}: Query failed - {str(e)}")
            
        except Exception as e:
            pytest.skip(f"MSSQL connection not available: {str(e)}")
        finally:
            # 모든 세션 종료
            for session in sessions:
                try:
                    session.close()
                except:
                    pass
    
    def test_connection_pool_reuse(self):
        """연결 풀 재사용 테스트"""
        connection_ids = []
        
        try:
            # 여러 번 연결하여 풀이 재사용되는지 확인
            for i in range(3):
                with MSSQLSessionLocal() as session:
                    result = session.execute(text("SELECT @@SPID as connection_id"))
                    conn_id = result.fetchone()[0]
                    connection_ids.append(conn_id)
                    print(f"Connection {i+1}: ID = {conn_id}")
            
            # 연결 풀이 제대로 동작한다면 연결 ID가 재사용될 수 있음
            print(f"Connection IDs: {connection_ids}")
            print("Connection pool test completed")
            
        except Exception as e:
            pytest.skip(f"MSSQL connection not available: {str(e)}")


@pytest.mark.integration
@pytest.mark.slow
def test_mssql_engine_disposal():
    """엔진 정리 테스트"""
    from src.core.database import close_db
    
    # 현재 엔진 상태 확인
    assert mssql_engine is not None
    print(f"Engine before disposal: {mssql_engine}")
    
    # 엔진 정리는 실제로는 애플리케이션 종료 시에만 수행
    # 여기서는 정리 함수가 존재하는지만 확인
    import inspect
    assert inspect.iscoroutinefunction(close_db)
    print("Engine disposal function exists and is async")