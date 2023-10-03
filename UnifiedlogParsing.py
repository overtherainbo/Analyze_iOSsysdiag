import os
import subprocess

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
