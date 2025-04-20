# 后端接口，调core里面的函数，返回结果，（排队机制）
from database.models import PatientEvent
from sqlalchemy.orm import joinedload
import pandas as pd
from collections import defaultdict
import pickle
import subprocess
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

predict_bp = Blueprint('predict', __name__)

def query_and_prepare_data(test_pkl,patient_id):
    patient_events = PatientEvent.query.options(
        joinedload(PatientEvent.patient),  # 获取 Patient 表的数据
        joinedload(PatientEvent.event)     # 获取 Event 表的数据
    ).filter(PatientEvent.patient_id == patient_id).all()
    
    # 将结果转化为字典格式并返回
    result = []
    result = []
    for patient_event in patient_events:
        # 整理每一条数据
        result.append({
            'id': patient_event.patient.id,  # patient 表的 id
            't': patient_event.time,         # patient_event 表的 time
            'event_type': patient_event.event.id,  # event 表的 id
            'k': patient_event.event.name,        # event 表的 name
            'heart_history': patient_event.patient.heart_history,  # patient 表的 heart_history
            'diabate_history': patient_event.patient.diabate_history,  # patient 表的 diabate_history
            'EH_history': patient_event.patient.EH_history,  # patient 表的 EH_history
        })

    # 将结果转换为 pandas DataFrame
    df = pd.DataFrame(result)

    # 按 patient id 和 time 排序
    df.sort_values(by=['id', 't'], inplace=True)

    # 计算 delta_t：对于每一行，当前行的 t 减去上一行的 t，第一行 delta_t 等于 t
    df['delta_t'] = df.groupby('id')['t'].diff().fillna(df['t'])
    groups = defaultdict(list)

    # 按 id 分组并整理数据
    for _, row in df.iterrows():
        record = {
            'time_since_last_event': float(row['delta_t']),
            'time_since_start': float(row['t']),
            'type_event': int(row['event_type']),
            'diabetes': int(row['diabate_history']),
            'heart': int(row['heart_history']),
            'EH': int(row['EH_history']),
            'k':str(row['k'])
        }
        groups[row['id']].append(record)

    # 将按 id 分组后的结果转为列表形式
    all_groups = list(groups.values())

    # 构造字典，每个字典中包含 dim_process 和对应数据
    tes_dict = {'dim_process': 18, 'test': all_groups}

    # 保存为 pickle 文件
    with open(test_pkl, 'wb') as f:
        pickle.dump(tes_dict, f)

    print(f"Test 数据已保存到 {test_pkl}")
    

def run_command_with_args():
    # 定义命令行及其参数
    command = ["python", "train_nhp.py", "--config_dir", "config.yaml", "--experiment_id", "AttNHP_train", "--rules", "[[3,(1,20,41)],[3,(0,2,38)],[3,(1,48,13)],[2,(39,13)],[2,(1,18)],[3,(0,11,43)],[3,(1,38,10)],[3,(1,12,4)],[3,(1,25,19)]]"]

    # 使用 subprocess.run 调用命令并等待其完成
    result = subprocess.run(command, capture_output=True, text=True)
    
    
    # 如果命令返回了一个非零的退出状态，抛出异常
    if result.returncode != 0:
        raise Exception(f"Command failed with exit code {result.returncode}")
    
@predict_bp.route('/get_predict_time', methods=['GET'])
@jwt_required()
def get_predict_time():
    """Get the patient information."""
    date = request.get_json()
    patience_id = date['patience_id']
    query_and_prepare_data("data/test.pkl",patience_id)
    run_command_with_args()
    
@predict_bp.route('/get_cluster_result', methods=['GET'])
def get_chart_data():
    """获取图表所需的患者事件数据和聚类数据"""
    try:
        # 获取请求中的患者ID参数
        patient_ids_param = request.args.get('patient_id', '')
        print('patient_ids_param',patient_ids_param)
        # 如果没有提供患者ID，返回错误
        if not patient_ids_param:
            return jsonify({
                "success": False,
                "message": "未提供患者ID参数"
            }), 400
            
        # 解析患者ID列表
        try:
            patient_ids = [int(pid.strip()) for pid in patient_ids_param.split(',') if pid.strip()]
        except ValueError:
            return jsonify({
                "success": False,
                "message": "患者ID格式不正确"
            }), 400
            
        # 如果患者ID列表为空，返回错误
        if not patient_ids:
            return jsonify({
                "success": False,
                "message": "患者ID列表为空"
            }), 400
            
        # 从数据库获取患者事件数据
        from database.models import PatientEvent, Event, Patient, PatientCluster
        from sqlalchemy.orm import joinedload
        from datetime import datetime
        
        patient_events = PatientEvent.query.options(
            joinedload(PatientEvent.patient),
            joinedload(PatientEvent.event)
        ).filter(PatientEvent.patient_id.in_(patient_ids)).all()
        
        # 按患者ID分组事件数据
        patient_events_dict = {}
        for pe in patient_events:
            patient_id = f"P{pe.patient_id}"  # 格式化为 P1, P2 等
            
            # 计算小时数（假设time是datetime对象）
            hour = 0
            if pe.time:
                if isinstance(pe.time, datetime) and pe.patient.in_icu and isinstance(pe.patient.in_icu, datetime):
                    # 计算从ICU入院时间开始的小时数
                    delta = pe.time - pe.patient.in_icu
                    hour = int(delta.total_seconds() / 3600)  # 转换为小时
                else:
                    # 如果没有入ICU时间或时间格式不正确，使用事件时间的小时部分
                    try:
                        hour = pe.time.hour if hasattr(pe.time, 'hour') else 0
                    except:
                        hour = 0
                
            # 创建事件对象
            event_obj = {
                "hour": hour,
                "value": pe.value if pe.value else 10,  # 如果没有值，使用默认值10
                "name": pe.event.name if pe.event else "未知事件"
            }
            
            # 将事件添加到对应患者的列表中
            if patient_id not in patient_events_dict:
                patient_events_dict[patient_id] = {
                    "patientId": patient_id,
                    "events": []
                }
            patient_events_dict[patient_id]["events"].append(event_obj)
        
        # 转换为列表格式
        patientEventData = list(patient_events_dict.values())
        
        # 从数据库获取聚类数据
        patient_clusters = PatientCluster.query.options(
            joinedload(PatientCluster.patient)
        ).filter(PatientCluster.patient_id.in_(patient_ids)).order_by(PatientCluster.time).all()
        # 按时间分组聚类数据
        cluster_time_dict = {}
        for pc in patient_clusters:
            hour = pc.time 
            # 格式化患者ID
            patient_id = f"p{pc.patient_id}".lower()  # 格式化为 p1, p2 等，小写
            
            # 将患者添加到对应时间和聚类的列表中
            if hour not in cluster_time_dict:
                cluster_time_dict[hour] = {"hour": hour, "cluster": []}
            
            # 查找该小时内是否已有该聚类ID
            cluster_found = False
            for cluster_list in cluster_time_dict[hour]["cluster"]:
                # 检查当前聚类列表中是否有相同cluster_id的患者组
                if len(cluster_list) > 0:
                    # 获取第一个患者的聚类ID
                    first_patient_id = int(cluster_list[0][1:]) if cluster_list[0][1:].isdigit() else 0
                    first_patient_cluster = PatientCluster.query.filter_by(
                        patient_id=first_patient_id,
                        time=pc.time
                    ).first()
                    
                    # 如果找到了聚类ID相同的组，将当前患者添加到该组
                    if first_patient_cluster and first_patient_cluster.cluster_id == pc.cluster_id:
                        cluster_list.append(patient_id)
                        cluster_found = True
                        break
            
            # 如果没有找到匹配的聚类，创建新的聚类组
            if not cluster_found:
                cluster_time_dict[hour]["cluster"].append([patient_id])
        
        # 转换为列表格式
        clusterData = list(cluster_time_dict.values())
        
        # 按小时排序
        clusterData.sort(key=lambda x: x["hour"])
        
        # 如果没有数据，使用模拟数据
        if not patientEventData:
            current_app.logger.warning("未找到患者事件数据，使用模拟数据")
            patientEventData = [
                {
                    "patientId": f"P{pid}",
                    "events": [
                        { "hour": 1, "value": 10, "name": "心率过快" },
                        { "hour": 3, "value": 15, "name": "血压偏高" },
                        { "hour": 6, "value": 18, "name": "发热" }
                    ]
                } for pid in patient_ids
            ]
            
        if not clusterData:
            current_app.logger.warning("未找到聚类数据，使用模拟数据")
            clusterData = [
                {
                    "hour": 0,
                    "cluster": [[f"p{pid}" for pid in patient_ids]]
                },
                {
                    "hour": 4,
                    "cluster": [
                        [f"p{pid}" for pid in patient_ids[:len(patient_ids)//2]],
                        [f"p{pid}" for pid in patient_ids[len(patient_ids)//2:]]
                    ]
                },
                {
                    "hour": 8,
                    "cluster": [
                        [f"p{pid}" for pid in patient_ids[:len(patient_ids)//3]],
                        [f"p{pid}" for pid in patient_ids[len(patient_ids)//3:2*len(patient_ids)//3]],
                        [f"p{pid}" for pid in patient_ids[2*len(patient_ids)//3:]]
                    ]
                }
            ]
        # print(clusterData)
        return jsonify({
            "success": True,
            "patientEventData": patientEventData,
            "clusterData": clusterData
        })
    except Exception as e:
        current_app.logger.error(f"获取图表数据失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取图表数据失败: {str(e)}"
        }), 500