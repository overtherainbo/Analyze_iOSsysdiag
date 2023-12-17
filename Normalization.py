import sqlite3
import os
import json

# Case Name 입력 받기
case_name = input("Case Name을 입력하세요: ")

# Case Name 폴더 경로
case_folder = os.path.join(os.getcwd(), case_name)

########################
##### Camera State #####
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
output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")

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
output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
output_conn.executemany('INSERT INTO NormalizedLog VALUES (?, ?, ?, ?, "Camera")', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("Camera State 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")

#############################
##### Camera Prewarming #####
# 입력할 UnifiedLog.db
input_db_filename = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")

# 출력할 SQLite 파일 이름
output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    select 
        datetime(Timestamp,'localtime') as Timestamp,
		Message as Bundle_ID,
        "Prewarming" as Message1,
		NULL as Message2,
		"Camera" as Category
    from unifiedlog 
        where Message like "%Prewarming Camera%" ORDER BY Timestamp
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
output_conn.executemany('INSERT INTO NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category) VALUES (?, ?, ?, ?, ?)', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("Camera Prewarming 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")

##############################
##### Device Orientation #####
# 입력할 SQLite 파일 이름
input_db_filename = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")

# 출력할 SQLite 파일 이름
output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    select 
        datetime(Timestamp,'localtime') as TIMESTAMP, 
        Subsystem as Bundle_ID, 
        substr(Message, 49) as Message1,
        "NULL" as Message2,
        "Rotation" as Category
    from unifiedlog 
        where Message like "%orientation from CoreMotion%"
    ORDER BY Timestamp
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
output_conn.executemany('INSERT INTO NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category) VALUES (?, ?, ?, ?, ?)', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("Device Orientation 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")

###########################
##### Face ID Success #####
# 입력할 SQLite 파일 이름
input_db_filename = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")

# 출력할 SQLite 파일 이름
output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    select 
	    datetime(Timestamp,'localtime') as TIMESTAMP,
	    Subsystem as Bundle_ID, 
	    substr(Message,instr(Message,'switchCameraState: ')+19) as Message1,
	    "Success" as Message2,
	    "FaceID" as Category
    from unifiedlog 
    where Message like "%switchCameraState:%" 
		AND Message1 like "%BioCheck (5) -> BioCheckDone (6)%"
    ORDER BY Timestamp
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
output_conn.executemany('INSERT INTO NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category) VALUES (?, ?, ?, ?, ?)', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("Face ID Success 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")

########################
##### Face ID Fail #####
# 입력할 SQLite 파일 이름
input_db_filename = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")

# 출력할 SQLite 파일 이름
output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    select 
	    datetime(Timestamp,'localtime') as TIMESTAMP,
	    Subsystem as Bundle_ID, 
	    substr(Message,instr(Message,'switchCameraState: ')+19) as Message1,
	    "Fail" as Message2,
	    "FaceID" as Category
    from unifiedlog 
    where Message like "%switchCameraState:%" 
		AND Message1 like "%(3) -> Idle (2)%"
		or Message1 like "%(4) -> Idle (2)%"
		or Message1 like "%(5) -> Idle (2)%"
		or Message1 like "%(7) -> Idle (2)%"
    ORDER BY Timestamp
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
output_conn.executemany('INSERT INTO NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category) VALUES (?, ?, ?, ?, ?)', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("Face ID Fail 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")

#############################
##### Screen Brightness #####
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
output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")

# 입력 및 출력 데이터베이스 연결
input_conn = sqlite3.connect(input_db_filename)
output_conn = sqlite3.connect(output_db_filename)

# 쿼리 실행
query = """
    SELECT
    Q1.TIMESTAMP,
    Q2.BUNDLE_ID,
    Q1.Brightness
FROM (
    SELECT
        TIMESTAMP,
        Brightness_ID,
        Brightness
    FROM (
        SELECT
            TIMESTAMP,
            Brightness_ID,
            Brightness,
            LAG(Brightness) OVER (ORDER BY TIMESTAMP) AS Prev_Brightness
        FROM (
            SELECT
                DATETIME(BRIGHTNESS_TIMESTAMP + SYSTEM, 'UNIXEPOCH', 'localtime') AS TIMESTAMP,
                BRIGHTNESS_ID,
                CAST(BRIGHTNESS as INTEGER) as Brightness
            FROM (
                SELECT
                    BRIGHTNESS_ID,
                    BRIGHTNESS_TIMESTAMP,
                    BRIGHTNESS,
                    SYSTEM
                FROM (
                    SELECT
                        PLDISPLAYAGENT_EVENTFORWARD_DISPLAY.TIMESTAMP AS BRIGHTNESS_TIMESTAMP,
                        BRIGHTNESS,
                        PLDISPLAYAGENT_EVENTFORWARD_DISPLAY.ID AS BRIGHTNESS_ID,
                        PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
                        PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
                    FROM
                        PLDISPLAYAGENT_EVENTFORWARD_DISPLAY
                    LEFT JOIN
                        PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
                )
                AS BRIGHTNESS_STATE
                WHERE Brightness != 0
                GROUP BY BRIGHTNESS_ID
            )
        )
    )
    WHERE ABS(Brightness - Prev_Brightness) >= 30 --연속된 밝기 값의 차이가 30이상일때만 출력함
) AS Q1

LEFT JOIN (
    SELECT
        TIMESTAMP,
        BUNDLE_ID,
        NULL AS Brightness
    FROM (
        SELECT
            DATETIME(SCREEN_STATE_TIMESTAMP + SYSTEM, 'UNIXEPOCH', 'localtime') AS TIMESTAMP,
            BUNDLEID AS BUNDLE_ID
        FROM (
            SELECT
                BUNDLEID,
                SCREENSTATE_ID,
                SCREEN_STATE_TIMESTAMP,
                SYSTEM,
                APPROLE,
                DISPLAY,
                LEVEL,
                ORIENTATION,
                SCREENWEIGHT
            FROM (
                SELECT
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.APPROLE AS APPROLE,
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.DISPLAY AS DISPLAY,
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.LEVEL AS LEVEL,
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.ORIENTATION AS ORIENTATION,
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.SCREENWEIGHT AS SCREENWEIGHT,
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.ID AS SCREENSTATE_ID,
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE.TIMESTAMP AS SCREEN_STATE_TIMESTAMP,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM,
                    BUNDLEID
                FROM
                    PLSCREENSTATEAGENT_EVENTFORWARD_SCREENSTATE
                LEFT JOIN
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
            )
            AS SCREENSTATE
            GROUP BY
                SCREENSTATE_ID
        ) 
        ORDER BY TIMESTAMP
    )
) AS Q2 ON Q1.TIMESTAMP = Q2.TIMESTAMP
WHERE Q1.Brightness != 0
ORDER BY Q1.TIMESTAMP
"""
cursor = input_conn.execute(query)

# 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
output_conn.executemany('INSERT INTO NormalizedLog VALUES (?, ?, ?, "NULL", "Brightness")', cursor)

# 변경사항을 커밋하고 연결을 닫음
output_conn.commit()
input_conn.close()
output_conn.close()

print("Screen Brightness 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")


#
# # 입력할 SQLite 파일 이름
# input_db_filename = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")
#
# # 출력할 SQLite 파일 이름
# output_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")
#
# # 입력 및 출력 데이터베이스 연결
# input_conn = sqlite3.connect(input_db_filename)
# output_conn = sqlite3.connect(output_db_filename)
#
# # 쿼리 실행
# query = """
#     select
# 	    datetime(Timestamp,'localtime') as TIMESTAMP,
# 	    Subsystem as Bundle_ID,
# 	    substr(Message,instr(Message,'AP environment for network : ')+29,instr(Message,' : bssCount: ')-83) as Message1,
# 	    "NULL" as Message2,
# 	    "Wi-Fi" as Category
#     from unifiedlog
#     where Message like "%AP environment for network%"
#     ORDER BY Timestamp
# """
# cursor = input_conn.execute(query)
#
# # 출력 데이터베이스에 새로운 테이블 생성 및 결과 복사
# output_conn.execute('CREATE TABLE IF NOT EXISTS NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category)')
# output_conn.executemany('INSERT INTO NormalizedLog (Timestamp, Bundle_ID, Message1, Message2, Category) VALUES (?, ?, ?, ?, ?)', cursor)
#
# # 변경사항을 커밋하고 연결을 닫음
# output_conn.commit()
# input_conn.close()
# output_conn.close()
#
# print("Wi-Fi AP SSID 결과가 NormalizedLog_{case_name}.db 파일에 저장되었습니다.")




##### db to json #####
# Normalization.db SQLite 데이터베이스 연결
input_normalization_db_filename = os.path.join(case_folder, f"NormalizedLog_{case_name}.db")
conn = sqlite3.connect(input_normalization_db_filename)
cursor = conn.cursor()

# 쿼리 작성
query = """SELECT Timestamp AS Date, TIME(Timestamp) AS Time, Category, Bundle_ID, Message1, Message2 
            FROM NormalizedLog
            ORDER BY Timestamp
        """

# 쿼리 실행
cursor.execute(query)

# 쿼리 결과 가져오기
data = cursor.fetchall()

# JSON 파일 경로 설정
json_file_path = os.path.join(case_folder, f"NormalizedLog_{case_name}.json")

# JSON 파일로 저장
json_data = []
for row in data:
    row_dict = {
        "Date": row[0],
        "Time": row[1],
        "Category": row[2],
        "Bundle_ID": row[3],
        "Message1": row[4],
        "Message2": row[5]
    }
    json_data.append(row_dict)

with open(json_file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# 연결 종료
conn.close()
