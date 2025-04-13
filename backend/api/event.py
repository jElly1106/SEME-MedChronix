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