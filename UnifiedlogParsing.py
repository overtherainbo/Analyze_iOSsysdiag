import os
import subprocess
import csv
import sqlite3

# Case Name 입력 받기
case_name = input("Case Name을 입력하세요: ")

# Case Name 폴더 경로
case_folder = os.path.join(os.getcwd(), case_name)

# sysdiagnose_raw 폴더 경로
sysdiagnose_raw_folder = os.path.join(case_folder, "sysdiagnose_raw")

# system_logs.logarchive 폴더를 찾는 함수
def find_system_logs_logarchive(folder):
    for root, dirs, files in os.walk(folder):
        if "system_logs.logarchive" in dirs:
            return os.path.join(root, "system_logs.logarchive")
    return None

# system_logs.logarchive 폴더 찾기
logarchive_path = find_system_logs_logarchive(sysdiagnose_raw_folder)

if logarchive_path:
    print("system_logs.logarchive 폴더 경로:", logarchive_path)
else:
    print("system_logs.logarchive 폴더를 찾을 수 없습니다.")

# output_csv 파일명 설정 (Case Name 폴더 내에 생성)
output_csv = os.path.join(case_folder, f"UnifiedLog_{case_name}.csv")

# unifiedlog_parser.exe 실행 파일 경로 설정
unifiedlog_parser_exe = "unifiedlog_parser.exe"

# unifiedlog_parser.exe 실행 명령어 설정
command = [unifiedlog_parser_exe, "-i", logarchive_path, "-o", output_csv]

# unifiedlog_parser.exe 실행
try:
    subprocess.run(command, check=True)
    print(f"{unifiedlog_parser_exe} 실행이 완료되었습니다.")
except subprocess.CalledProcessError as e:
    print(f"{unifiedlog_parser_exe} 실행 중 오류 발생: {e}")
except FileNotFoundError:
    print(f"{unifiedlog_parser_exe} 파일을 찾을 수 없습니다.")

##########################
# CSV 파일 및 SQLite DB 정보 (Case Name 폴더 내에 생성)
csv_file_path = os.path.join(case_folder, f"UnifiedLog_{case_name}.csv")
db_file_path = os.path.join(case_folder, f"UnifiedLog_{case_name}.db")
table_name = 'unifiedlog'

# 파일 경로 출력
print("csv 파일 경로:", csv_file_path)

# SQLite DB 연결
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# 테이블 생성 (CSV 파일의 첫 번째 행을 테이블의 컬럼으로 사용)
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csv_file:
    # NUL 문자가 포함된 행을 건너뛰기 위한 함수 정의
    def filter_null(data):
        return data.replace('\0', '')

    csv_reader = csv.reader((filter_null(row) for row in csv_file))
    header = next(csv_reader)

    # 중복 컬럼 처리를 위한 세트
    column_names = set()
    unique_columns = []  # 중복되지 않은 컬럼

    for column_name in header:
        # 중복 컬럼 확인
        if column_name not in column_names:
            column_names.add(column_name)
            # Replace empty spaces with underscores
            column_name = column_name.replace(' ', '_')
            unique_columns.append(column_name)

    columns = ','.join(unique_columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});")

# 데이터 삽입
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csv_file:
    csv_reader = csv.reader((filter_null(row) for row in csv_file))
    next(csv_reader)  # 헤더 건너뛰기
    for row in csv_reader:
        placeholders = ','.join(['?'] * len(row))
        cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders});", row)

# 변경 사항 저장 및 연결 종료
conn.commit()
conn.close()

# csv 파일이 존재하는지 확인 후 삭제
if os.path.exists(csv_file_path):
    os.remove(csv_file_path)
    print(f"{csv_file_path} 파일이 삭제되었습니다.")
else:
    print(f"{csv_file_path} 파일이 존재하지 않습니다.")