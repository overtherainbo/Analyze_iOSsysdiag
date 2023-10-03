import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os

# Case Name 입력 받기
case_name = input("Case Name을 입력하세요: ")

# Case Name 폴더 경로
case_folder = os.path.join(os.getcwd(), case_name)

# SQLite 데이터베이스에 연결
conn = sqlite3.connect(os.path.join(case_folder, f"CameraState.db"))
cursor = conn.cursor()

# 데이터 추출 쿼리 작성 및 실행
query = "SELECT Timestamp, Bundle_ID, Camera_Type, State FROM CameraState WHERE Bundle_ID IS NOT NULL ORDER BY Timestamp"
cursor.execute(query)

# 결과 추출
results = cursor.fetchall()
conn.close()

# 데이터 처리
data = pd.DataFrame(results, columns=['Timestamp', 'Bundle_ID', 'Camera_Type', 'State'])

# 그래프 처리 및 저장
timestamps = data['Timestamp']
bundle_ids = data['Bundle_ID']
states = data['State']

plt.figure(figsize=(12, 6))

# 상태에 따라 막대 색상 설정
#colors = ['blue' if state == 'FRONT' else 'red' for state in states]
colors = ['blue' if state == 'FRONT' else 'red' if state == 'BACK' else 'black' for state in data['State']]

# 막대 그래프 그리기
plt.bar(timestamps, [1] * len(timestamps), color=colors)

# Bundle_ID 값을 막대 안에 표시
for x, bundle_id in zip(timestamps, bundle_ids):
    plt.text(x, 0.5, str(bundle_id), rotation=90, ha='center', va='center', fontsize=8, color='white')

plt.xlabel('Timestamp')
plt.ylabel('Camera Type')
plt.title('Camera Type by Timestamp')
plt.xticks(rotation=90)
plt.yticks([])  # y축 눈금 비활성화
plt.tight_layout()

# 그래프 이미지 저장
plt.savefig(os.path.join(case_folder, f'CameraState_graph.png'))

# 데이터를 HTML 파일로 저장
with open(os.path.join(case_folder, f'CameraState_Report.html'), 'w') as file:
    # HTML 헤더 작성
    file.write('<!DOCTYPE html>\n<html>\n<head>\n')
    file.write('<title>Camera State Analysis</title>\n')
    file.write('</head>\n<body>\n')

    # 그래프 이미지 삽입
    file.write('<h2>Camera Type by Timestamp</h2>\n')
    file.write('<img src="CameraState_graph.png" alt="Camera Type Chart">\n')

    # 데이터 표 삽입
    file.write('<h2>Camera Data</h2>\n')
    file.write(data.to_html(index=False))

    # HTML 파일 마무리
    file.write('</body>\n</html>')

# 그래프 표시
plt.show()
