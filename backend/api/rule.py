from flask import Flask, jsonify, Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from database.models import Rule, Event,Precondition,PatientRule,db
from flask_jwt_extended import jwt_required, get_jwt_identity

rule_bp = Blueprint('rule', __name__)

@rule_bp.route('/get_rules', methods=['GET'])
@jwt_required()
def get_rules():
    """Get the list of rules with formatted content."""
    rules = Rule.query.all()
    event_map = {event.id: event.name for event in Event.query.all()}  # 事件 ID -> 事件名称映射
    # 获取 Prediction 表的映射（前置条件 ID -> 前置条件名称）
    precondition_map = {precondition.id: precondition.description for precondition in Precondition.query.all()}

    rules_list = []
    for rule in rules:
        event1_name = event_map.get(rule.event_id1, "未知事件")
        event2_name = event_map.get(rule.event_id2, None) if rule.event_id2 else None
        precondition_name = precondition_map.get(rule.precondition, None) if rule.precondition else None

        # 生成前端显示的规则内容
        if not precondition_name and event1_name and not event2_name:
            rule_content = f"{event1_name} before {rule.time_delta}"
        elif not precondition_name and event1_name and event2_name:
            # 双事件规则，根据time_delta调整显示
            if rule.time_delta > 0:
                rule_content = f"{event1_name} before {event2_name}"
            elif rule.time_delta < 0:
                rule_content = f"{event1_name} after {event2_name}"
            else:  # time_delta == 0
                rule_content = f"{event1_name} equal {event2_name}"
        elif precondition_name and event1_name and event2_name:
            # 带前置条件的规则，根据time_delta调整显示
            if rule.time_delta > 0:
                rule_content = f"if {precondition_name}, {event1_name} before {event2_name}"
            elif rule.time_delta < 0:
                rule_content = f"if {precondition_name}, {event1_name} after {event2_name}"
            else:  # time_delta == 0
                rule_content = f"if {precondition_name}, {event1_name} equal {event2_name}"
        else:
            rule_content = "规则格式错误"

        rules_list.append({
            "id": rule.id,
            "content": rule_content
        })

    return jsonify(rules_list)

@rule_bp.route('/delete_rule/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    """根据规则编号删除规则"""
    rule = Rule.query.get(rule_id)
    
    if not rule:
        return jsonify({"error": "规则不存在"}), 404  # 规则不存在

    db.session.delete(rule)
    db.session.commit()
    
    return jsonify({"message": "规则删除成功", "rule_id": rule_id}), 200

@rule_bp.route('/add_rule', methods=['POST'])
@jwt_required()
def add_rule():
    """添加新规则"""
    data = request.get_json()

    # 1. 提取必填字段
    disease_id = 1
    name = data.get('name')
    weight = data.get('weight')
    category = data.get('category')
    event_id1 = data.get('event_id1')

    # 2. 提取可选字段（可为 None）
    event_id2 = data.get('event_id2')
    precondition = data.get('precondition')
    time_delta = data.get('time_delta')

    # 3. 校验必填字段是否为空
    if disease_id is None:
        return jsonify({"error": "disease_id 不能为空"}), 400
    if not name:  # 字符串为空也算没填
        return jsonify({"error": "name 不能为空"}), 400
    if weight is None:
        return jsonify({"error": "weight 不能为空"}), 400
    if category is None:
        return jsonify({"error": "category 不能为空"}), 400
    if event_id1 is None:
        return jsonify({"error": "event_id1 不能为空"}), 400

    # 4. 创建 Rule 对象
    new_rule = Rule(
        disease_id=disease_id,
        name=name,
        weight=weight,
        category=category,
        event_id1=event_id1,
        event_id2=event_id2,         # 可空
        precondition=precondition,   # 可空
        time_delta=time_delta        # 可空
    )

    # 5. 插入数据库
    db.session.add(new_rule)
    db.session.commit()

    return jsonify({
        "message": "规则添加成功",
        "rule_id": new_rule.id
    }), 201

@rule_bp.route('/get_rules_by_property', methods=['GET'])
@jwt_required()
def get_rules_by_property():
    """根据属性名称获取所有包含该属性的规则列表"""
    property_name = request.args.get('property_name')  # 获取查询参数
    if not property_name:
        return jsonify({"error": "必须提供 property_name 参数"}), 400

    # 获取所有与该属性相关的事件
    events = Event.query.filter(Event.name.like(f"%{property_name}%")).all()
    if not events:
        return jsonify({"error": "未找到任何与该属性相关的事件"}), 404

    # 获取所有相关事件 ID
    event_ids = [event.id for event in events]

    # 查询所有包含这些事件的规则
    rules = Rule.query.filter(
        (Rule.event_id1.in_(event_ids)) | (Rule.event_id2.in_(event_ids))
    ).all()
    
    rules_list = []
    for rule in rules:
        # 生成前端显示的规则内容
        rule_content=rule.name

        rules_list.append({
            "id": rule.id,
            "content": rule_content
        })

    return jsonify(rules_list), 200
    """根据属性名称获取所有包含该属性的规则列表"""
    property_name = request.args.get('property_name')  # 获取查询参数
    if not property_name:
        return jsonify({"error": "必须提供 property_name 参数"}), 400

    # 获取所有与该属性相关的事件
    events = Event.query.filter(Event.name.like(f"%{property_name}%")).all()
    if not events:
        return jsonify({"error": "未找到任何与该属性相关的事件"}), 404

    # 获取所有相关事件 ID
    event_ids = [event.id for event in events]

    # 查询所有包含这些事件的规则
    rules = Rule.query.filter(
        (Rule.event_id1.in_(event_ids)) | (Rule.event_id2.in_(event_ids)) | (Rule.precondition.in_(event_ids))
    ).all()

    # 事件 ID -> 事件名称映射
    event_map = {e.id: e.name for e in Event.query.all()}
    precondition_map = {precondition.id: precondition.description for precondition in Precondition.query.all()}

    rules_list = []
    for rule in rules:
        event1_name = event_map.get(rule.event_id1, "未知事件")
        event2_name = event_map.get(rule.event_id2, None) if rule.event_id2 else None
        precondition_name = precondition_map.get(rule.precondition, None) if rule.precondition else None

        # 生成前端显示的规则内容
        if not precondition_name and event1_name and not event2_name:
            rule_content = f"{event1_name} > {rule.time_delta}"
        elif not precondition_name and event1_name and event2_name:
            rule_content = f"{event1_name} - {event2_name} > {rule.time_delta}"
        elif precondition_name and event1_name and event2_name:
            rule_content = f"if {precondition_name}, {event1_name} - {event2_name} > {rule.time_delta}"
        else:
            rule_content = "规则格式错误"

        rules_list.append({
            "id": rule.id,
            "content": rule_content
        })

    return jsonify(rules_list), 200


@rule_bp.route('/get_rules_by_patient', methods=['GET'])
@jwt_required()
def get_rules_by_patient():

    # 从请求中获取参数，处理业务逻辑，返回响应
    patient_id = request.args.get('patient_id', type=int)
    
    if patient_id is None:
        return jsonify({'error': 'Missing patient_id parameter'}), 400
    
    event_map = {event.id: event.name for event in Event.query.all()}  # 事件 ID -> 事件名称映射
    # 获取 Prediction 表的映射（前置条件 ID -> 前置条件名称）
    precondition_map = {precondition.id: precondition.description for precondition in Precondition.query.all()}
    
    patient_rules = PatientRule.query.filter(PatientRule.patient_id == patient_id).all()
    if not patient_rules:
        return jsonify({"error": "未找到任何与该病人相关的规则"}), 404
    
    result = []
    
    for patient_rule in patient_rules:
        rule = patient_rule.rule
        
        event1_name = event_map.get(rule.event_id1, "未知事件")
        event2_name = event_map.get(rule.event_id2, None) if rule.event_id2 else None
        precondition_name = precondition_map.get(rule.precondition, None) if rule.precondition else None
        
        if not precondition_name and event1_name and not event2_name:
            rule_content = f"{event1_name} before {rule.time_delta}"
        elif not precondition_name and event1_name and event2_name:
            # 双事件规则，根据time_delta调整显示
            if rule.time_delta > 0:
                rule_content = f"{event1_name} before {event2_name} ({rule.time_delta})"
            elif rule.time_delta < 0:
                rule_content = f"{event1_name} after {event2_name} ({abs(rule.time_delta)})"
            else:  # time_delta == 0
                rule_content = f"{event1_name} equal {event2_name}"
        elif precondition_name and event1_name and event2_name:
            # 带前置条件的规则，根据time_delta调整显示
            if rule.time_delta > 0:
                rule_content = f"if {precondition_name}, {event1_name} before {event2_name} ({rule.time_delta})"
            elif rule.time_delta < 0:
                rule_content = f"if {precondition_name}, {event1_name} after {event2_name} ({abs(rule.time_delta)})"
            else:  # time_delta == 0
                rule_content = f"if {precondition_name}, {event1_name} equal {event2_name}"
        else:
            rule_content = "规则格式错误"
        
        result.append({
            'rule_content': rule_content
        })
    
    return jsonify(result), 200