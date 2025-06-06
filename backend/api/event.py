from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func,or_
from database.models import Event,PatientEvent,db


event_bp = Blueprint('event_bp', __name__)

@event_bp.route('/get_all_events', methods=['GET'])
@jwt_required()
def get_all_events():
    """获取所有异常事件（仅返回 id 和 name）"""
    events = Event.query.with_entities(Event.id, Event.name).all()
    return jsonify([{"id": event.id, "name": event.name} for event in events])

@event_bp.route('/get_num_of_events', methods=['GET'])
@jwt_required()
def get_num_of_events():
    """获得异常事件发生频次（包含未发生的事件）"""

    event_counts = (
        db.session.query(
            Event.id.label("event_id"),
            Event.name.label("event_name"),
            func.count(PatientEvent.event_id).label("count")
        )
        .outerjoin(PatientEvent, Event.id == PatientEvent.event_id)
        .group_by(Event.id, Event.name)
        .order_by(Event.id)
        .all()
    )

    # 组织 JSON 数据
    result = [
        {"event_id": event.event_id, "event_name": event.event_name, "count": event.count}
        for event in event_counts
    ]

    return jsonify(result), 200


@event_bp.route('/get_events_by_patientsIDList', methods=['POST'])
@jwt_required()
def get_events_by_patientsIDList():
    """统计选定病人的异常事件发生频次，返回最多 8 个异常事件名称"""
    # 获取请求中的病人 ID 列表
    data = request.get_json()
    patient_ids = data.get("patient_ids", [])

    # 400 请求参数错误
    if not patient_ids:
        return jsonify({"error": "Missing patient_ids parameter"}), 400
        
    # 查询异常事件发生频次
    event_counts = (
        db.session.query(
            Event.id.label("event_id"),
            Event.name.label("event_name"),
            func.count(PatientEvent.event_id).label("count")
        )
        .join(Event, Event.id == PatientEvent.event_id)
        .filter(PatientEvent.patient_id.in_(patient_ids))
        .group_by(PatientEvent.event_id, Event.name)
        .order_by(func.count(PatientEvent.event_id).desc())
        .limit(8)
        .all()
    )

    # 组织 JSON 返回事件名称
    result = [
        {"event_id": event.event_id, "event_name": event.event_name, "count": event.count}
        for event in event_counts
    ]
    return jsonify(result), 200
    

@event_bp.route('/get_event_ids_by_category', methods=['GET'])
@jwt_required()
def get_event_ids_by_category():
    """获取包含钠、钾、血氧饱和度、动脉血压、血糖、血细胞比容的事件 ID，并按类别返回"""
        
    # 定义各类别的关键词
    categories = {
        "sodium": ["钠"],
        "potassium": ["钾"],
        "oxygen_saturation": ["血氧饱和度"],
        "arterial_pressure": ["动脉血压"],
        "blood_sugar": ["血糖"],
        "hematocrit": ["血细胞比容"]
    }

    # 初始化结果字典
    result = {key: [] for key in categories}

    # 查询 Event 表，筛选名称包含指定关键词的事件
    for category, keywords in categories.items():
        query = (
            db.session.query(Event.id)
            .filter(or_(*[Event.name.contains(keyword) for keyword in keywords]))
            .all()
        )
        result[category] = [row.id for row in query]

    return jsonify(result), 200


@event_bp.route('/add_patient_event', methods=['POST'])
@jwt_required()
def add_patient_event():
    """为病人添加一条异常事件记录"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        if not data or 'patient_id' not in data or 'event_id' not in data:
            return jsonify({"error": "缺少必要参数，需要patient_id和event_id"}), 400
        
        patient_id = data.get('patient_id')
        event_id = data.get('event_id')
        timestamp = data.get('timestamp')  # 可选参数
        value = data.get('value')  # 可选参数
        
        # 检查事件是否存在
        event = Event.query.get(event_id)
        if not event:
            return jsonify({"error": f"事件ID {event_id} 不存在"}), 404
        
        # 创建新的PatientEvent记录
        new_patient_event = PatientEvent(
            patient_id=patient_id,
            event_id=event_id,
            timestamp=timestamp,
            value=value
        )
        
        # 添加到数据库并提交
        db.session.add(new_patient_event)
        db.session.commit()
        
        return jsonify({
            "message": "事件记录添加成功",
            "patient_event_id": new_patient_event.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"添加事件记录失败: {str(e)}"}), 500

# 添加批量添加接口
@event_bp.route('/add_patient_events_batch', methods=['POST'])
@jwt_required()
def add_patient_events_batch():
    """批量为多个病人添加异常事件记录"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        if not data or 'events' not in data or not isinstance(data['events'], list):
            return jsonify({"error": "缺少必要参数，需要events数组"}), 400
        
        events = data['events']
        added_count = 0
        errors = []
        
        for event_data in events:
            # 验证每条记录的必要参数
            if 'patient_id' not in event_data or 'event_id' not in event_data:
                errors.append(f"记录缺少必要参数: {event_data}")
                continue
            
            # 检查事件是否存在
            event = Event.query.get(event_data['event_id'])
            if not event:
                errors.append(f"事件ID {event_data['event_id']} 不存在")
                continue
            
            # 创建新的PatientEvent记录
            new_patient_event = PatientEvent(
                patient_id=event_data['patient_id'],
                event_id=event_data['event_id'],
                timestamp=event_data.get('timestamp'),
                value=event_data.get('value')
            )
            
            # 添加到数据库
            db.session.add(new_patient_event)
            added_count += 1
        
        # 提交所有更改
        db.session.commit()
        
        result = {
            "message": f"成功添加 {added_count} 条事件记录",
            "added_count": added_count
        }
        
        if errors:
            result["errors"] = errors
        
        return jsonify(result), 201 if added_count > 0 else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"批量添加事件记录失败: {str(e)}"}), 500