import sqlite3
import os

# Case Name 입력 받기
case_name = input("Case Name을 입력하세요: ")

# Case Name 폴더 경로
case_folder = os.path.join(os.getcwd(), case_name)

# Case Name 폴더에서 powerlog_*.PLSQL 파일을 찾아 input_db_filename 에 저장
input_db_filename = None
for root, dirs, files in os.walk(case_folder):
    for file in files:
        if file.startswith("powerlog_") and file.endswith(".PLSQL"):
            input_db_filename = os.path.join(root, file)
            break  # 파일을 찾았으면 루프를 종료
    if input_db_filename:
        break  # 파일을 찾았으면 루프를 종료

# 파일을 찾지 못한 경우 에러 메시지 출력
if input_db_filename is None:
    print("경고: 'powerlog_'로 시작하고 확장자가 '.PLSQL'인 파일을 찾을 수 없습니다.")
    # 프로그램 종료 또는 다른 조치를 취할 수 있습니다.

# 출력할 SQLite 파일 이름
output_db_filename = os.path.join(case_folder, f"CameraState.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    SELECT
      DATETIME(CAMERA_TIMESTAMP + SYSTEM, 'unixepoch', 'localtime') AS TIMESTAMP,
      BUNDLEID AS BUNDLE_ID,
      CASE CAMERA_TYPE
         WHEN "2" THEN "FRONT"
         WHEN "0" THEN "BACK"
      END AS CAMERA_TYPE,
	  CASE STATE
         WHEN "0" THEN "OFF"
         WHEN "1" THEN "ON"
      END AS STATE	  
   FROM
      (
      SELECT
         BUNDLEID,
         CAMERA_ID,
         CAMERA_TIMESTAMP,
         TIME_OFFSET_TIMESTAMP,
         MAX(TIME_OFFSET_ID) AS max_id,
         SYSTEM,
         CAMERA_TYPE,
         STATE
      FROM
         (
         SELECT
            PLCAMERAAGENT_EVENTFORWARD_CAMERA.TIMESTAMP AS CAMERA_TIMESTAMP,
            PLCAMERAAGENT_EVENTFORWARD_CAMERA.BUNDLEID,
            PLCAMERAAGENT_EVENTFORWARD_CAMERA.CAMERATYPE AS "CAMERA_TYPE",
            PLCAMERAAGENT_EVENTFORWARD_CAMERA.STATE,
            PLCAMERAAGENT_EVENTFORWARD_CAMERA.ID AS "CAMERA_ID",
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
         FROM
            PLCAMERAAGENT_EVENTFORWARD_CAMERA 
         LEFT JOIN
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET  
            )
            AS CAMERASTATE 
         GROUP BY
            CAMERA_ID 
      ) ORDER BY TIMESTAMP
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS CameraState (Timestamp, Bundle_ID, State, Camera_Type)')
output_conn.executemany('INSERT INTO CameraState VALUES (?, ?, ?, ?)', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("쿼리 결과가 새로운 데이터베이스 파일에 저장되었습니다.")
