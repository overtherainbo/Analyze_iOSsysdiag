import subprocess
import os
import tkinter as tk
from tkinter import filedialog

# tkinter 팝업 창을 열어서 압축 파일 경로를 선택하도록 합니다.
root = tk.Tk()
root.withdraw()  # tkinter 창 숨김
file_path = filedialog.askopenfilename(filetypes=[("Tar.gz 파일", "*.tar.gz")])

if not file_path:
    print("파일 선택이 취소되었습니다.")
else:
    # Case Name 입력 받기
    case_name = input("Case Name을 입력하세요: ")

    # Case Name 폴더 생성
    case_folder = os.path.join(os.getcwd(), case_name)
    os.makedirs(case_folder, exist_ok=True)

    # sysdiagnose_raw 폴더 생성
    sysdiagnose_raw_folder = os.path.join(case_folder, "sysdiagnose_raw")
    os.makedirs(sysdiagnose_raw_folder, exist_ok=True)

    # 7z.exe를 사용하여 gz 압축 해제
    gz_file = file_path
    subprocess.run(["7z.exe", "e", gz_file, "-o" + sysdiagnose_raw_folder])

    # gz 파일명 추출
    gz_filename = os.path.splitext(os.path.basename(gz_file))[0]

    # tar 압축 해제
    tar_file = os.path.join(sysdiagnose_raw_folder, gz_filename)
    subprocess.run(["tar", "xf", tar_file, "-C", sysdiagnose_raw_folder])

    print("압축 해제가 완료되었습니다.")

# tar 파일이 존재하는지 확인 후 삭제
if os.path.exists(tar_file):
    os.remove(tar_file)
    print(f"{tar_file} 파일이 삭제되었습니다.")
else:
    print(f"{tar_file} 파일이 존재하지 않습니다.")