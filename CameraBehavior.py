import sqlite3
import os

# Case Name 입력 받기
case_name = input("Case Name을 입력하세요: ")

# Case Name 폴더 경로
case_folder = os.path.join(os.getcwd(), case_name)

# 입력할 UnifiedLog.db
input_db_filename = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")

# 출력할 SQLite 파일 이름
output_db_filename = os.path.join(case_folder, f"CameraState.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    select 
        datetime(Timestamp,'localtime') as Timestamp, 
        Message 
    from unifiedlog where Message like "%Prewarming Camera%" ORDER BY Timestamp
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS CameraState (Timestamp, Bundle_ID, State, Camera_Type)')
output_conn.executemany('INSERT INTO CameraState (Timestamp, Bundle_ID) VALUES (?, ?)', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("쿼리 결과가 새로운 데이터베이스 파일에 저장되었습니다.")
