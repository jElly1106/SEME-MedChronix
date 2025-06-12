""" the router function for the instance of patient-related table. """

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import func,and_
from sqlalchemy.orm import joinedload

from database.models import Patient, PatientEvent, PatientRule,Disease,PatientCluster,PatientPrediction,EventPrediction,PatientCase,Event,db
from common.utils import upload_images
import os
from datetime import datetime
import json
from api.event import get_event_ids_by_category
from common.decorators import admin_required
from common.response import ResponseCode

patient_bp = Blueprint('patient', __name__)
    
@patient_bp.route('/get_patience_event', methods=['GET'])
@jwt_required()
def get_patience_event():
    """Get the patient event information."""
    date = request.get_json()
    event_id = date['event_id']
    patient_event = PatientEvent.query.get(event_id)
    if patient_event:
        return jsonify(patient_event.to_dict())
    else:
        return jsonify({'error': 'Event not found'}), 404

    
@patient_bp.route('/all', methods=['GET'])
#@jwt_required()
def get_all_patients():
    """获取所有病人的完整信息"""
    patients = Patient.query.all()
    result = [patient.to_dict() for patient in patients]
    return jsonify(result), 200

@patient_bp.route('/delete/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    """根据 id 删除病人"""
    patient = Patient.query.get_or_404(patient_id)

    # 删除关联表（事件、规则、聚类等）
    PatientEvent.query.filter_by(patient_id=patient.id).delete()
    PatientRule.query.filter_by(patient_id=patient.id).delete()
    PatientCluster.query.filter_by(patient_id=patient.id).delete()

    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted successfully"}), 200

@patient_bp.route('/update/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    """根据 id 修改病人信息"""
    data = request.get_json()
    patient = Patient.query.get_or_404(patient_id)
    print("!!!!!!!!!!!!!",patient)

    # 更新字段（你也可以写得更智能一些）
    patient.name = data.get('name', patient.name)
    patient.gender = data.get('gender', patient.gender)
    patient.age = data.get('age', patient.age)
    patient.heart_history = data.get('heart_history', patient.heart_history)
    patient.diabete_history = data.get('diabete_history', patient.diabete_history)
    patient.EH_history = data.get('EH_history', patient.EH_history)
    patient.other_history = data.get('other_history', patient.other_history)
    patient.status = data.get('status', patient.status)

    if 'in_icu' in data:
        patient.in_icu = datetime.strptime(data['in_icu'], "%Y-%m-%d %H:%M:%S")
    if 'out_icu' in data:
        patient.out_icu = datetime.strptime(data['out_icu'], "%Y-%m-%d %H:%M:%S")

    db.session.commit()
    return jsonify({"message": "Patient updated successfully"}), 200

@patient_bp.route('/add', methods=['POST'])
@jwt_required()
def add_patient():
    """添加一个新患者"""
    data = request.get_json()

    # 获取对应的疾病（假设传的是疾病名称）
    disease = Disease.query.filter_by(name=data.get('desease')).first()
    if not disease:
        return jsonify({'error': 'Disease not found'}), 404

    # 构造 Patient 对象
    new_patient = Patient(
        name=data.get('name'),
        gender=data.get('gender'),
        age=data.get('age'),
        heart_history=data.get('heart_history'),
        diabete_history=data.get('diabete_history'),
        EH_history=data.get('EH_history'),
        other_history=data.get('other_history'),
        status=data.get('status'),
        in_icu=datetime.strptime(data['in_icu'], "%Y-%m-%d %H:%M:%S") if data.get('in_icu') else None,
        out_icu=datetime.strptime(data['out_icu'], "%Y-%m-%d %H:%M:%S") if data.get('out_icu') else None,
        disease_id=disease.id
    )

    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'Patient added successfully', 'patient_id': new_patient.id}), 201



#2025/3/19 feat


@patient_bp.route('/gender_stats', methods=['GET'])
@jwt_required()
def gender_stats():
    gender_counts = db.session.query(
        Patient.gender,
        func.count(Patient.id).label('count')
    ).group_by(Patient.gender).all()

    result = {gender: count for gender, count in gender_counts if gender is not None}
    return jsonify(result), 200

@patient_bp.route('/age_stats', methods=['GET'])
@jwt_required()
def age_distribution():
    """统计病人表中年龄（按年龄段统计人数）"""
    age_groups = {
        "0-20": (0, 20),
        "21-40": (21, 40),
        "41-60": (41, 60),
        "60+": (61, None)  # 60+ 无上限
    }

    age_stats = {}

    for group, (min_age, max_age) in age_groups.items():
        if max_age:  # 针对 0-60 岁的区间
            count = db.session.query(func.count(Patient.id)).filter(
                Patient.age.between(min_age, max_age)
            ).scalar()
        else:  # 处理 60+ 年龄段
            count = db.session.query(func.count(Patient.id)).filter(
                Patient.age >= min_age
            ).scalar()

        age_stats[group] = count

    return jsonify(age_stats), 200


@patient_bp.route('/details', methods=['GET'])
@jwt_required()
def get_patients_with_events():
    """获取所有病人的姓名、年龄、异常事件序列，异常事件按时间升序排列"""

    # 查询所有患者，并预加载其异常事件
    patients = db.session.query(Patient).options(
        joinedload(Patient.patient_events)  # 预加载患者的异常事件
    ).all()

    result = []

    for patient in patients:
        # 获取该患者的所有异常事件，并按时间升序排序
        events = db.session.query(PatientEvent).filter_by(patient_id=patient.id).order_by(PatientEvent.time.asc()).all()

        # 构建异常事件列表
        event_list = []
        event_codes = []  # 添加事件代码列表，用于前端显示
        
        for event in events:
            # 确保时间格式正确
            formatted_time = None
            if event.time:
                try:
                    formatted_time = datetime.strptime(str(event.time), "%Y-%m-%d %H:%M:%S").isoformat()
                except ValueError:
                    formatted_time = "Invalid Time Format"

            event_list.append({
                "event_id": event.id,
                "time": formatted_time,
                "name": event.event.name if event.event else "未知事件"  # 添加事件名称
            })
            
            # 为前端添加事件代码（取事件名称的前4个字符作为代码）
            if event.event and event.event.name:
                event_code = event.event.name[:4]  # 取前4个字符作为代码
                event_codes.append(event_code)

        # 构建返回的病人信息
        patient_info = {
            "id": patient.id,  # 添加病人ID
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,  # 添加病人性别
            "status": patient.status,  # 添加病人状态（脑卒中类型）
            "in_icu": patient.in_icu.isoformat() if patient.in_icu else None,  # 添加入ICU时间
            "out_icu": patient.out_icu.isoformat() if patient.out_icu else None,  # 添加出ICU时间
            "heart_history": patient.heart_history,  # 添加心脏病史
            "diabete_history": patient.diabete_history,  # 添加糖尿病史
            "EH_history": patient.EH_history,  # 添加高血压史
            "other_history": patient.other_history,  # 添加其他病史
            "events": event_list,
            "event_codes": event_codes,  # 添加事件代码列表
            "avatar": f"https://picsum.photos/seed/patient{patient.id}/200/200"  # 生成随机头像
        }
        
        result.append(patient_info)

    return jsonify(result), 200


@patient_bp.route('/filter', methods=['POST'])
@jwt_required()
def filter_patients():
    """筛选病人，筛选条件包括脑卒中类型、ICU进入时间、ICU离开时间"""
    data = request.get_json()

    # 解析筛选条件
    status_list = data.get("status", [])  # 脑卒中类型（可以是列表）
    in_icu_start = data.get("in_icu_start", None)  # ICU 进入时间下限
    in_icu_end = data.get("in_icu_end", None)  # ICU 进入时间上限
    out_icu_start = data.get("out_icu_start", None)  # ICU 离开时间下限
    out_icu_end = data.get("out_icu_end", None)  # ICU 离开时间上限
    def parse_datetime(dt_str):
        if dt_str:
            try:
                # 尝试解析 ISO 格式
                return datetime.fromisoformat(dt_str.replace('T', ' '))
            except ValueError:
                try:
                    # 尝试解析标准格式
                    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return None
        return None
    # 构建查询条件
    filters = []
    if status_list:
        filters.append(Patient.status.in_(status_list))
    
    in_icu_start_dt = parse_datetime(in_icu_start)
    if in_icu_start_dt:
        filters.append(Patient.in_icu >= in_icu_start_dt)
    
    in_icu_end_dt = parse_datetime(in_icu_end)
    if in_icu_end_dt:
        filters.append(Patient.in_icu <= in_icu_end_dt)
    
    out_icu_start_dt = parse_datetime(out_icu_start)
    if out_icu_start_dt:
        filters.append(Patient.out_icu >= out_icu_start_dt)
    
    out_icu_end_dt = parse_datetime(out_icu_end)
    if out_icu_end_dt:
        filters.append(Patient.out_icu <= out_icu_end_dt)

    # 查询数据库
    patients = db.session.query(Patient).filter(and_(*filters)).all()
    result = [patient.to_dict() for patient in patients]

    ##25/4/1 test
    result = []

    for patient in patients:
        # 获取该患者的所有异常事件，并按时间升序排序
        events = db.session.query(PatientEvent).filter_by(patient_id=patient.id).order_by(PatientEvent.time.asc()).all()

        # 构建异常事件列表
        event_list = []
        event_codes = []  # 添加事件代码列表，用于前端显示
        
        for event in events:
            # 确保时间格式正确
            formatted_time = None
            if event.time:
                try:
                    formatted_time = datetime.strptime(str(event.time), "%Y-%m-%d %H:%M:%S").isoformat()
                except ValueError:
                    formatted_time = "Invalid Time Format"

            event_list.append({
                "event_id": event.id,
                "time": formatted_time,
                "name": event.event.name if event.event else "未知事件"  # 添加事件名称
            })
            
            # 为前端添加事件代码（取事件名称的前4个字符作为代码）
            if event.event and event.event.name:
                event_code = event.event.name[:4]  # 取前4个字符作为代码
                event_codes.append(event_code)

        # 构建返回的病人信息
        patient_info = {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "status": patient.status,
            "events": event_list,
            "event_codes": event_codes,  # 添加事件代码列表
            "avatar": f"https://picsum.photos/seed/patient{patient.id}/200/200"  # 生成随机头像
        }

        result.append(patient_info)
    return jsonify(result), 200



@patient_bp.route('/get_latest_patient_events', methods=['POST'])
def get_latest_patient_events():
    """查询 patient_event 表，获取 patient_id 对应的最新异常事件数值，并按前端需要的格式返回"""
    
    # 获得病人id
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不存在'}), 404
    # print(data)
    
    # 处理patient_ids，支持单个ID或ID列表
    if 'patient_ids' not in data:
        return jsonify({'error': '未提供患者ID'}), 400
        
    patient_ids = data['patient_ids']
    # 如果不是列表，转为列表
    if not isinstance(patient_ids, list):
        patient_ids = [patient_ids]
    
    if not patient_ids:
        return jsonify({'error': '患者ID列表为空'}), 400
    
    # 获取事件ID列表
    event_ids = data.get('event_ids', [])
    if not event_ids:
        # 如果前端没有传入event_ids，则使用get_event_ids_by_category获取
        event_categories, status_code = get_event_ids_by_category()
        if status_code != 200:
            return jsonify({'error': '未找到事件类别'}), 404
        event_categories = event_categories.get_json()
        # 合并所有类别的事件ID
        for ids in event_categories.values():
            event_ids.extend(ids)
    
    # 定义指标ID与名称的映射
    event_id_to_name = {
        1: "sodium",           # 钠
        2: "potassium",        # 钾
        3: "oxygen_saturation", # 血氧饱和度
        4: "blood_pressure",   # 血压
        5: "glucose",          # 血糖
        6: "hematocrit"        # 血细胞比容
    }
    
    # 将结果改为字典格式，键为患者ID
    result = {}
    
    # 查询每个患者的信息
    for patient_id in patient_ids:
        # 获取患者信息
        patient = Patient.query.get(patient_id)
        if not patient:
            continue
        
        # 初始化患者数据
        patient_data = {
            "name": patient.name,
            "data": [0, 0, 0, 0, 0, 0]  # 默认值
        }
        
        # 查询该患者的最新事件数据
        for index, (event_id, indicator_name) in enumerate(event_id_to_name.items()):
            if event_id in event_ids:
                try:
                    # 查询该事件的最新记录
                    latest_event = (
                        db.session.query(PatientEvent)
                        .filter(
                            PatientEvent.patient_id == patient_id,
                            PatientEvent.event_id == event_id
                        )
                        .order_by(PatientEvent.time.desc())
                        .first()
                    )
                    
                    # 如果找到记录，更新数据
                    if latest_event and latest_event.value is not None:
                        patient_data["data"][index] = latest_event.value
                except Exception as e:
                    print(f"查询患者 {patient_id} 的事件 {event_id} 时出错: {str(e)}")
        
        # 将患者数据添加到结果字典中，以患者ID为键
        result[patient_id] = patient_data
    
    # print("返回结果:", result)
    return jsonify(result), 200


@patient_bp.route('/cluster_result', methods=['POST'])
@jwt_required()
def get_patient_cluster_result():
    """
    输入病人ID列表，返回多个时间点上的聚类结果（二维列表）
    """
    data = request.get_json()
    patient_ids = data.get("patient_ids", [])

    if not patient_ids:
        return jsonify({
            "code": ResponseCode.PARAMS_ERROR,
            "message": "No patient IDs provided",
            "data": None
        }), ResponseCode.BAD_REQUEST

    clusters = (
        db.session.query(PatientCluster)
        .filter(PatientCluster.patient_id.in_(patient_ids))
        .order_by(PatientCluster.time.asc())
        .all()
    )

    cluster_by_time = {}
    for cluster in clusters:
        time_key = cluster.time.isoformat() if cluster.time else "unknown_time"
        if time_key not in cluster_by_time:
            cluster_by_time[time_key] = {}
        cluster_by_time[time_key][cluster.patient_id] = cluster.cluster_id

    result = []
    for time_key in sorted(cluster_by_time.keys()):
        cluster_map = cluster_by_time[time_key]
        result.append([cluster_map.get(pid, -1) for pid in patient_ids])

    return jsonify({
        "code": ResponseCode.OK,
        "message": "Success",
        "data": result
    }), ResponseCode.OK


@patient_bp.route('/event_full_info', methods=['POST'])
# @jwt_required()
def get_patient_event_full_info():
    """
    输入病人 ID，返回：
    1. 实际发生的异常事件和时间（patient_event）
    2. 模型预测的目标事件与时间（目前为空）
    3. 模型预测的各种异常事件的概率（目前为空）
    """
    data = request.get_json()
    patient_id = data.get("patient_id")

    if not patient_id:
        return jsonify({
            "code": ResponseCode.PARAMS_ERROR,
            "message": "Missing patient_id",
            "data": None
        }), ResponseCode.BAD_REQUEST

    # 实际事件
    events = (
        db.session.query(PatientEvent)
        .filter_by(patient_id=patient_id)
        .order_by(PatientEvent.time.asc())
        .all()
    )
    # 要将所有时间相同的事件放置在一个字典中
    events_dict = []
    for e in events:
        event_time = e.time.strftime('%Y-%m-%d %H:%M:%S') if e.time else "unknown_time"
        event_types = [e.event.name] if e.event else ["未知事件"]
        
        # 查找是否已经有相同时间的事件
        existing_event = next((item for item in events_dict if item['time'] == event_time), None)
        if existing_event:
            existing_event['event_type'].extend(event_types)
        else:
            events_dict.append({
                'time': event_time,
                'event_type': event_types
            })
    
    # 去重事件类型
    for event in events_dict:
        event['event_type'] = list(set(event['event_type']))
    
    # 模拟空模型预测
    #值查找大于当前时间的事件
    predicted_events = (db.session.query(PatientPrediction)
        .filter(PatientPrediction.patient_id == patient_id)
        # .filter(PatientPrediction.time > datetime.now())
        .order_by(PatientPrediction.time.asc())
        .all()
    )
    predicted_targets = []
    for e in predicted_events:
        event_time = e.time.strftime('%Y-%m-%d %H:%M:%S') if e.time else "unknown_time"
        event_types = [e.event.name] if e.event else ["未知事件"]
        
        # 查找是否已经有相同时间的事件
        existing_event = next((item for item in predicted_targets if item['time'] == event_time), None)
        if existing_event:
            existing_event['event_type'].extend(event_types)
        else:
            predicted_targets.append({
                'time': event_time,
                'event_type': event_types
            })
    # 去重事件类型
    for event in predicted_targets:
        event['event_type'] = list(set(event['event_type']))
    print(predicted_targets)
    return jsonify({
        "code": ResponseCode.OK,
        "message": "Success",
        "data": {
            "actual_events": events_dict,
            "predicted_targets": predicted_targets,
        }
    }), ResponseCode.OK


@patient_bp.route('/data_table/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_data_table(patient_id):
    """
    获取患者的数据表格信息，包括记录时间、事件名、指标值、正常范围值
    """
    try:
        # 验证患者是否存在
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                "code": ResponseCode.NOT_FOUND,
                "message": f"未找到ID为{patient_id}的患者",
                "data": None
            }), ResponseCode.NOT_FOUND
            
        # 查询该患者的所有事件数据，按时间排序，并关联事件表获取事件信息
        patient_events = (
            db.session.query(PatientEvent)
            .filter_by(patient_id=patient_id)
            .join(Event, PatientEvent.event_id == Event.id)
            .order_by(PatientEvent.time.desc())
            .all()
        )
        
        # 整理数据为表格所需格式
        result = []
        for event in patient_events:
            if not event.time:
                continue
                
            # 获取事件信息
            event_info = event.event
            if not event_info:
                continue
                
            # 构建正常范围值字符串
            normal_range = ""
            if event_info.min_value is not None and event_info.max_value is not None:
                normal_range = f"{event_info.min_value} - {event_info.max_value}"
            elif event_info.min_value is not None:
                normal_range = f">= {event_info.min_value}"
            elif event_info.max_value is not None:
                normal_range = f"<= {event_info.max_value}"
                
            # 添加单位信息
            if event_info.unit:
                normal_range += f" {event_info.unit}"
                
            # 构建记录数据
            record = {
                'record_time': event.time.strftime('%Y-%m-%d %H:%M:%S'),
                'event_name': event_info.name,
                'value': event.value,
                'normal_range': normal_range
            }
            
            result.append(record)
        
        return jsonify({
            "code": ResponseCode.OK,
            "message": "获取患者数据表格成功",
            "data": result
        }), ResponseCode.OK
        
    except Exception as e:
        current_app.logger.error(f"获取患者数据表格失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.INTERNAL_SERVER_ERROR,
            "message": f"获取患者数据表格失败: {str(e)}",
            "data": None
        }), ResponseCode.INTERNAL_SERVER_ERROR

@patient_bp.route('/event_probabilities', methods=['POST'])
# @jwt_required()
def get_event_probabilities():
    """
    输入病人 ID，返回模型预测的各种异常事件的概率
    """
    data = request.get_json()
    patient_id = data.get("patient_id")

    if not patient_id:
        return jsonify({
            "code": ResponseCode.PARAMS_ERROR,
            "message": "Missing patient_id",
            "data": None
        }), ResponseCode.BAD_REQUEST

    predicted_events = (
        db.session.query(EventPrediction)
        .filter_by(patient_id=patient_id)
        .order_by(EventPrediction.time.asc())
        .all()
    )
    # 将事件转换为字典格式
    # [
    #     // 时间点1 - 已发生的数据
    #     {
    #       time: "2023-01-01",
    #       events: [
    #         { type: "发热", intensity: 16.5 },
    #         { type: "咳嗽", intensity: 8.2 },
    #         { type: "头痛", intensity: 5.1 },
    #         { type: "呼吸困难", intensity: 3.0 },
    #         { type: "乏力", intensity: 4.5 },
    #       ],
    #       isHistorical: true,
    #     },
    #     // 时间点2
    #     {
    #       time: "2023-01-02",
    #       events: [
    #         { type: "发热", intensity: 15.0 },
    #         { type: "咳嗽", intensity: 9.5 },
    #         { type: "头痛", intensity: 4.8 },
    #         { type: "呼吸困难", intensity: 4.2 },
    #         { type: "乏力", intensity: 6.0 },
    #       ],
    #       isHistorical: False,
    #     }
    # ]
    probabilities = []
    for e in predicted_events:
        event_time = e.time.strftime('%Y-%m-%d %H:%M:%S') if e.time else "unknown_time"
        event_pred = {
            "type": e.event.name if e.event else "未知事件",
            "probability": e.probability
        }
        last_observation_time = (
            db.session.query(func.max(PatientEvent.time))
            .filter_by(patient_id=patient_id)
            .scalar()
        )
        # 查找是否已经有相同时间的事件
        existing_event = next((item for item in probabilities if item['time'] == event_time), None)
        if existing_event:
            # 修复：将单个事件对象添加到events列表中，而不是extend
            existing_event['events'].append(event_pred)
        else:
            probabilities.append({
                'time': event_time,
                'events': [event_pred],
                'isHistorical': True if e.time <= last_observation_time else False  # 判断事件是否已经发生
            })

    return jsonify({
        "code": ResponseCode.OK,
        "message": "Success",
        "data": probabilities
    }), ResponseCode.OK 


@patient_bp.route('/top_predictions', methods=['GET'])
@jwt_required()
def get_top_prediction_patients():
    """
    获取预测事件时间最早的前6位病人信息
    返回病人的姓名、性别、心脏病史、糖尿病史、高血压史和预测时间
    """
    try:
        # 查询预测时间最早的前6位病人
        subquery = (
            db.session.query(
                PatientPrediction.patient_id,
                func.min(PatientPrediction.time).label('earliest_time')
            )
            .group_by(PatientPrediction.patient_id)
            .order_by(func.min(PatientPrediction.time).asc())
            .limit(6)
            .subquery()
        )

        # 联合查询获取病人详细信息
        results = (
            db.session.query(
                Patient.id,
                Patient.name,
                Patient.gender,
                Patient.heart_history,
                Patient.diabete_history,
                Patient.EH_history,
                subquery.c.earliest_time
            )
            .join(subquery, Patient.id == subquery.c.patient_id)
            .all()
        )

        # 格式化返回数据
        patients_data = []
        for result in results:
            patient_info = {
                'id': result[0],
                'name': result[1],
                'gender': result[2],
                'heart_history': result[3],
                'diabete_history': result[4],
                'Eh_history': result[5],
                'prediction_time': result[6].isoformat() if result[6] else None
            }
            patients_data.append(patient_info)

        return jsonify({
            'code': ResponseCode.OK,
            'message': '获取预测病人数据成功',
            'data': patients_data
        }), ResponseCode.OK

    except Exception as e:
        return jsonify({
            'code': ResponseCode.INTERNAL_SERVER_ERROR,
            'message': f'获取预测病人数据失败: {str(e)}',
            'data': None
        }), ResponseCode.INTERNAL_SERVER_ERROR
    
@patient_bp.route('/case_details/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_case_details(patient_id):
    """
    根据病人ID获取病例的详细信息，包括：
    1. 病例编号、就诊时间、就诊地点、医生记录
    2. 病人相关的所有事件名称和数值
    3. 事件数值相较于标准值的评估结果（偏高/正常/偏低）
    
    Args:
        patient_id: 病人ID
    """
    try:
        # 验证病人是否存在
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                "code": ResponseCode.NOT_FOUND,
                "message": f"未找到ID为{patient_id}的病人",
                "data": None
            }), ResponseCode.NOT_FOUND
        
        # 查询该病人的所有病例
        cases = PatientCase.query.filter_by(patient_id=patient_id).all()
        if not cases:
            return jsonify({
                "code": ResponseCode.OK,
                "message": f"该病人暂无病例记录",
                "data": []
            }), ResponseCode.OK
        
        result = []
        
        for case in cases:
            # 获取病例基本信息
            case_info = {
                "id": case.id,
                "case_number": case.case_number,
                "patient_id": case.patient_id,
                "visit_time": case.visit_time.isoformat() if case.visit_time else None,
                "visit_location": case.visit_location,
                "doctor_notes": case.doctor_notes,
                "events": []  # 初始化空的事件列表
            }
            
            # 移除对不存在的case_id字段的引用
            # 改为通过时间范围关联事件
            if case.visit_time:
                from datetime import timedelta
                visit_date = case.visit_time.date()
                
                # 获取与病例就诊日期相同的事件
                patient_events = PatientEvent.query.filter(
                    PatientEvent.patient_id == patient_id,
                    func.date(PatientEvent.time) == visit_date
                ).all()
                
                # 如果没有找到事件，可以扩大时间范围
                if not patient_events:
                    # 扩大到前后三天
                    three_days_before = visit_date - timedelta(days=3)
                    three_days_after = visit_date + timedelta(days=3)
                    
                    patient_events = PatientEvent.query.filter(
                        PatientEvent.patient_id == patient_id,
                        func.date(PatientEvent.time) >= three_days_before,
                        func.date(PatientEvent.time) <= three_days_after
                    ).all()
            else:
                # 如果没有就诊时间，获取该病人的所有事件
                patient_events = PatientEvent.query.filter_by(patient_id=patient_id).all()
            
            # 导入Event模型
            from database.models import Event
            
            for patient_event in patient_events:
                # 获取事件详情
                event = Event.query.get(patient_event.event_id)
                if not event:
                    continue
                
                # 评估事件数值状态
                status = "正常"
                try:
                    if event.max_value is not None and patient_event.value is not None and float(patient_event.value) > float(event.max_value):
                        status = "偏高"
                    elif event.min_value is not None and patient_event.value is not None and float(patient_event.value) < float(event.min_value):
                        status = "偏低"
                except (ValueError, TypeError):
                    # 如果数值转换失败，保持默认状态
                    status = "未知"
                
                # 添加事件信息
                event_info = {
                    "event_id": patient_event.event_id,
                    "event_name": event.name,
                    "value": patient_event.value,
                    "time": patient_event.time.isoformat() if patient_event.time else None,
                    "standard_min": event.min_value,
                    "standard_max": event.max_value,
                    "unit": event.unit,
                    "status": status
                }
                
                case_info["events"].append(event_info)
            
            result.append(case_info)
        
        return jsonify({
            "code": ResponseCode.OK,
            "message": "获取病例详情成功",
            "data": result
        }), ResponseCode.OK
        
    except Exception as e:
        current_app.logger.error(f"获取病例详情失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.INTERNAL_SERVER_ERROR,
            "message": f"获取病例详情失败: {str(e)}",
            "data": None
        }), ResponseCode.INTERNAL_SERVER_ERROR
# 新增病例记录
@patient_bp.route('/case', methods=['POST'])
@jwt_required()
def add_case():
    """
    新增病例记录
    
    请求体格式:
    {
        "patient_id": 1,
        "case_number": "C20240501001",
        "visit_time": "2024-05-01T10:00:00",
        "visit_location": "同济大学嘉定校区卫生所",
        "doctor_notes": "患者主诉头痛、眩晕3天，伴有轻度恶心。",
        "events": [
            {
                "event_id": 1,
                "value": "145/95",
                "time": "2024-05-01T10:15:00"
            },
            {
                "event_id": 2,
                "value": "5.8",
                "time": "2024-05-01T10:20:00"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ["patient_id", "case_number", "visit_time", "visit_location"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": ResponseCode.PARAMS_ERROR,
                    "message": f"缺少必要字段: {field}",
                    "data": None
                }), ResponseCode.BAD_REQUEST
        
        # 验证病人是否存在
        patient = Patient.query.get(data["patient_id"])
        if not patient:
            return jsonify({
                "code": ResponseCode.NOT_FOUND,
                "message": f"未找到ID为{data['patient_id']}的病人",
                "data": None
            }), ResponseCode.NOT_FOUND
        
        # 验证病例编号是否已存在
        existing_case = PatientCase.query.filter_by(case_number=data["case_number"]).first()
        if existing_case:
            return jsonify({
                "code": ResponseCode.CONFLICT,
                "message": f"病例编号{data['case_number']}已存在",
                "data": None
            }), ResponseCode.CONFLICT
        
        # 创建新病例
        new_case = PatientCase(
            patient_id=data["patient_id"],
            case_number=data["case_number"],
            visit_time=datetime.fromisoformat(data["visit_time"]) if data["visit_time"] else None,
            visit_location=data["visit_location"],
            doctor_notes=data.get("doctor_notes", "")
        )
        
        db.session.add(new_case)
        db.session.flush()  # 获取新病例ID
        
        # 处理事件数据
        if "events" in data and isinstance(data["events"], list):
            for event_data in data["events"]:
                # 验证事件是否存在
                from database.models import Event
                event = Event.query.get(event_data["event_id"])
                if not event:
                    continue
                
                # 创建病人事件记录
                new_event = PatientEvent(
                    patient_id=data["patient_id"],
                    event_id=event_data["event_id"],
                    value=event_data["value"],
                    time=datetime.fromisoformat(event_data["time"]) if "time" in event_data else None,
                    case_id=new_case.id  # 关联到新创建的病例
                )
                
                db.session.add(new_event)
        
        db.session.commit()
        
        return jsonify({
            "code": ResponseCode.OK,
            "message": "病例创建成功",
            "data": {
                "case_id": new_case.id,
                "case_number": new_case.case_number
            }
        }), ResponseCode.OK
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建病例失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.INTERNAL_SERVER_ERROR,
            "message": f"创建病例失败: {str(e)}",
            "data": None
        }), ResponseCode.INTERNAL_SERVER_ERROR

# 更新病例记录
@patient_bp.route('/case/<int:case_id>', methods=['PUT'])
@jwt_required()
def update_case(case_id):
    """
    更新病例记录
    
    请求体格式:
    {
        "case_number": "C20240501001",
        "visit_time": "2024-05-01T10:00:00",
        "visit_location": "同济大学嘉定校区卫生所",
        "doctor_notes": "患者主诉头痛、眩晕3天，伴有轻度恶心。血压测量为145/95mmHg，建议监测血压并服用降压药物。"
    }
    """
    try:
        # 验证病例是否存在
        case = PatientCase.query.get(case_id)
        if not case:
            return jsonify({
                "code": ResponseCode.NOT_FOUND,
                "message": f"未找到ID为{case_id}的病例",
                "data": None
            }), ResponseCode.NOT_FOUND
        
        data = request.get_json()
        
        # 更新病例信息
        if "case_number" in data:
            # 检查新病例编号是否与其他病例冲突
            existing_case = PatientCase.query.filter(
                PatientCase.case_number == data["case_number"],
                PatientCase.id != case_id
            ).first()
            
            if existing_case:
                return jsonify({
                    "code": ResponseCode.CONFLICT,
                    "message": f"病例编号{data['case_number']}已被其他病例使用",
                    "data": None
                }), ResponseCode.CONFLICT
            
            case.case_number = data["case_number"]
        
        if "visit_time" in data:
            case.visit_time = datetime.fromisoformat(data["visit_time"]) if data["visit_time"] else None
        
        if "visit_location" in data:
            case.visit_location = data["visit_location"]
        
        if "doctor_notes" in data:
            case.doctor_notes = data["doctor_notes"]
        
        db.session.commit()
        
        return jsonify({
            "code": ResponseCode.OK,
            "message": "病例更新成功",
            "data": {
                "case_id": case.id,
                "case_number": case.case_number
            }
        }), ResponseCode.OK
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新病例失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.INTERNAL_SERVER_ERROR,
            "message": f"更新病例失败: {str(e)}",
            "data": None
        }), ResponseCode.INTERNAL_SERVER_ERROR

# 删除病例记录
@patient_bp.route('/case/<int:case_id>', methods=['DELETE'])
@jwt_required()
def delete_case(case_id):
    """
    删除病例记录
    """
    try:
        # 验证病例是否存在
        case = PatientCase.query.get(case_id)
        if not case:
            return jsonify({
                "code": ResponseCode.NOT_FOUND,
                "message": f"未找到ID为{case_id}的病例",
                "data": None
            }), ResponseCode.NOT_FOUND
        
        # 删除病例
        db.session.delete(case)
        db.session.commit()
        
        return jsonify({
            "code": ResponseCode.OK,
            "message": "病例删除成功",
            "data": None
        }), ResponseCode.OK
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除病例失败: {str(e)}")
        return jsonify({
            "code": ResponseCode.INTERNAL_SERVER_ERROR,
            "message": f"删除病例失败: {str(e)}",
            "data": None
        }), ResponseCode.INTERNAL_SERVER_ERROR
