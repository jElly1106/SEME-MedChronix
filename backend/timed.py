# 放置定时向数据库中导入数据的脚本，模型定时推理脚本，
# scheduler.py
import schedule
import time
import requests
from core.predict import run
from core.cluster_people import run_model
from check_rule import check_rules_for_patients

def job():
    print("定时任务执行中...")
    #response = requests.get('http://127.0.0.1:5001/simulate_patient_event')  # 请求模拟数据 API
    check_rules_for_patients()
    run()
    run_model()

# 每t秒执行一次 my_function
schedule.every(3600).seconds.do(job)

while True:
    schedule.run_pending()  # 检查并执行已安排的任务
    print("等待中...")
    time.sleep(600)  # 每100秒检查一次
