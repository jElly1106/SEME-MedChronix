import random
from datetime import datetime, timedelta
from flask import Flask, jsonify
from database.models import Patient, PatientEvent, Event, db

app = Flask(__name__)

@app.route('/simulate_patient_event', methods=['GET'])
def simulate_patient_event():
    """
    模拟病人事件数据，每次循环都随机选择患者 ID、事件 ID 和事件时间，并插入到 PatientEvent 表中
    """
    # 假设每次要生成 5 条数据
    num_simulations = 5

    # 用于存储插入的数据
    simulated_data = []

    for _ in range(num_simulations):
        # 1. 随机选择一个患者 ID
        patient_ids = db.session.query(Patient.id).all()  # 获取所有患者的 id
        patient_id = random.choice(patient_ids)[0]  # 随机选择一个患者 ID

        # 2. 随机选择一个事件 ID
        event_ids = db.session.query(Event.id).all()  # 获取所有事件的 id
        event_id = random.choice(event_ids)[0]  # 随机选择一个事件 ID

        # 3. 随机生成一个事件时间
        # 获取当前时间并加上一个小于 2 秒的随机小数
        event_time = datetime.now() + timedelta(seconds=random.uniform(0, 2))

        # 4. 创建 PatientEvent 实例并插入到数据库
        patient_event = PatientEvent(
            patient_id=patient_id,
            event_id=event_id,
            time=event_time
        )
        
        # 将模拟的数据添加到列表中（供后续查看或处理）
        simulated_data.append({
            'patient_id': patient_id,
            'event_id': event_id,
            'event_time': event_time.strftime("%Y-%m-%d %H:%M:%S")
        })

        # 插入 PatientEvent 数据
        db.session.add(patient_event)

    # 提交所有事务
    db.session.commit()

    return jsonify({
        'simulations': num_simulations,
        'message': 'Successfully simulated and inserted patient events',
        'simulated_data': simulated_data
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)


