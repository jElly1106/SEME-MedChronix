from datetime import datetime, timedelta
from database.models import Rule, Patient, PatientEvent, PatientRule
from common.extensions import db
from main import app

def check_rules_for_patients():
    """
    根据规则和患者事件判断每个患者满足哪些规则，并将结果写入patient_rule表
    """
    with app.app_context():
        # 清空现有的patient_rule表数据
        PatientRule.query.delete()
        db.session.commit()
        
        # 获取所有患者和规则
        patients = Patient.query.all()
        rules = Rule.query.all()
        
        # 对每个患者进行规则判断
        for patient in patients:
            # 获取患者的所有事件，按时间排序
            patient_events = PatientEvent.query.filter_by(patient_id=patient.id).order_by(PatientEvent.time).all()
            
            # 创建事件字典，方便查找
            event_dict = {}
            for pe in patient_events:
                if pe.event_id not in event_dict:
                    event_dict[pe.event_id] = []
                event_dict[pe.event_id].append(pe)
            # 检查每条规则
            for rule in rules:
                # 检查前置条件
                if rule.category == 3:  # 有前置条件的规则
                    if rule.precondition == 0 and patient.diabete_history != "有":
                        continue  # 不满足糖尿病前置条件
                    if rule.precondition == 1 and patient.heart_history != "有":
                        continue  # 不满足心脏病前置条件
                    if rule.precondition == 2 and patient.EH_history != "有":
                        continue  # 不满足高血压前置条件
                
                # 检查事件1和事件2是否存在
                if rule.event_id1 not in event_dict or (rule.event_id2 and rule.event_id2 not in event_dict):
                    continue
                
                # 根据规则类型检查事件关系
                rule_satisfied = False
                
                if rule.category == 1:  # 单一事件规则
                    rule_satisfied = True
                elif rule.category in [2, 3]:  # 双事件规则
                    # 获取事件1和事件2的所有记录
                    try:
                            # 获取事件1和事件2的所有记录
                        events1 = event_dict[rule.event_id1]
                        events2 = event_dict[rule.event_id2]
                        
                        # 后续代码...
                    except KeyError as e:
                        print(f"KeyError: 规则ID {rule.id} 访问 event_dict[{e}] 失败")
                        continue
                    
                    if rule.time_delta == 0:  # equal关系
                        # 检查是否有事件1和事件2在同一时间点(或接近的时间点)发生
                        for e1 in events1:
                            for e2 in events2:
                                # 允许5分钟的时间误差
                                if abs((e1.time - e2.time).total_seconds()) <= 300:
                                    rule_satisfied = True
                                    break
                            if rule_satisfied:
                                break
                    elif rule.time_delta > 0:  # before关系
                        # 检查是否有事件1在事件2之前发生
                        for e1 in events1:
                            for e2 in events2:
                                if e1.time < e2.time:
                                    rule_satisfied = True
                                    break
                            if rule_satisfied:
                                break
                
                # 如果规则满足，添加到patient_rule表
                if rule_satisfied:
                    patient_rule = PatientRule(
                        patient_id=patient.id,
                        rule_id=rule.id,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(patient_rule)
            
        # 提交所有更改
        db.session.commit()
        print(f"✅ 已完成所有患者的规则判断并更新patient_rule表")

