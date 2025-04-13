""" the router function for the instance of patient-related table. """

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import func,and_
from sqlalchemy.orm import joinedload

from database.models import Patient, PatientEvent, PatientRule,Disease,PatientCluster,db
from common.utils import upload_images
import os
from datetime import datetime
import json
from common.decorators import admin_required
from api.event import get_event_ids_by_category

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/get_patience_info', methods=['GET'])
@jwt_required()
def get_patience_info():
    """Get the patient information."""
    date = request.get_json()
    patience_id = date['patience_id']
    patient = Patient.query.get(patience_id)
    if patient:
        return jsonify(patient.to_dict())
    else:
        return jsonify({'error': 'Patience not found'}), 404
    
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
    
@patient_bp.route('/get_patience_rule', methods=['GET'])
@jwt_required()
def get_patience_rule():
    """Get the patient rule information."""
    date = request.get_json()
    rule_id = date['rule_id']
    patient_rule = PatientRule.query.get(rule_id)
    if patient_rule:
        return jsonify(patient_rule.to_dict())
    else:
        return jsonify({'error': 'Rule not found'}), 404
    
@patient_bp.route('/add_patience', methods=['POST'])
@jwt_required()
def add_patience():
    """Add a new patient."""
    data = request.get_json()
    desease_id = Disease.query.filter_by(name=data['desease']).first()
    if not desease_id:
        return jsonify({'error': 'Desease not found'}), 404
    patient = Patient(
        name = data['name'],
        gender = data['gender'],
        age = data['age'],
        heart_history = data['heart_history'],
        diabete_history = data['diabete_history'],
        EH_history = data['EH_history'],
        other_history = data['other_history'],
        status = data['status'],
        in_icu = datetime.strptime(data['in_icu'], '%Y-%m-%d %H:%M:%S'),
        out_icu = datetime.strptime(data['out_icu'], '%Y-%m-%d %H:%M:%S'),
        desease_id = desease_id.id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )
    db = current_app.config['db']
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient added successfully'}), 201

@patient_bp.route('/get_all_patients',methods=['GET'])
@jwt_required()
def get_all_patients():
    "Get all patients info"
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients])



@patient_bp.route('/update_patience', methods=['POST'])
@jwt_required()
def update_patience():
    """Update the patient information."""
    data = request.get_json()
    patient = Patient.query.get(data['id'])
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    desease_id = Disease.query.filter_by(name=data['desease']).first()
    if not desease_id:
        return jsonify({'error': 'Desease not found'}), 404
    patient.name = data['name']
    patient.gender = data['gender']
    patient.age = data['age']
    patient.heart_history = data['heart_history']
    patient.diabete_history = data['diabete_history']
    patient.EH_history = data['EH_history']
    patient.other_history = data['other_history']
    patient.status = data['status']
    patient.in_icu = datetime.strptime(data['in_icu'], '%Y-%m-%d %H:%M:%S')
    patient.out_icu = datetime.strptime(data['out_icu'], '%Y-%m-%d %H:%M:%S')
    patient.desease_id = desease_id.id
    patient.updated_at = datetime.now()
    db = current_app.config['db']
    db.session.commit()
    return jsonify({'message': 'Patient updated successfully'}), 200


@patient_bp.route('/delete_patience', methods=['POST'])
@jwt_required()
def delete_patience():
    """Delete the patient."""
    data = request.get_json()
    patient = Patient.query.get(data['id'])
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    db = current_app.config['db']
    # 先删除相关的规则和事件记录
    PatientEvent.query.filter_by(patient_id=patient.id).delete()
    PatientRule.query.filter_by(patient_id=patient.id).delete()
    PatientCluster.query.filter_by(patient_id=patient.id).delete()
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'}), 200











@patient_bp.route('/get_latest_patient_events', methods=['GET'])
@jwt_required()
def get_latest_patient_events():
    """查询 patient_event 表，获取 patient_id 对应的最新异常事件数值"""
    
    # 获得病人id
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Patient not found'}), 404
    patient_id = data['patient_id']
    
    # 事件类别及对应 event_id 列表
    event_categories ,status_code = get_event_ids_by_category()
    if status_code != 200:
        return jsonify({'error': 'Event not found'}), 404
    
    # 解析查询结果
    event_categories = event_categories.get_json()

    result = {}

    for category, event_ids in event_categories.items():
        # 查询该类别中 event_id 列表对应的最新事件
        subquery = (
            db.session.query(
                func.max(PatientEvent.time).label("latest_time")
            )
            .filter(PatientEvent.patient_id == patient_id, PatientEvent.event_id.in_(event_ids))
            .scalar_subquery()
        )

        latest_event = (
            db.session.query(
                PatientEvent.event_id,
                PatientEvent.value,
                PatientEvent.time
            )
            .filter(PatientEvent.patient_id == patient_id, PatientEvent.time == subquery)
            .order_by(PatientEvent.time.desc())
            .first()
        )

        # 组织返回数据
        result[category] = {
            "event_id": latest_event.event_id,
            "value": latest_event.value,
            "time": latest_event.time
        } if latest_event else {}

    return jsonify(result), 200




