from sqlalchemy.orm import joinedload
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database.models import PatientEvent, db
import torch
import numpy as np
from collections import defaultdict
from main import app

def preprocess(rule_sum=[[0, 19, 40], [1, 2, 37], [0, 47, 12], 
                         [0, 38, 12], [0, 1, 17], [1, 11, 42], 
                         [0, 37, 10], [0, 48, 4], [0, 24, 18]], time_limit=10):
    # 定义时间范围
    time_limit_in_seconds = time_limit * 3600

    with app.app_context():
        # 准备数据存储容器
        event_seqs = []
        time_seqs = []
        rules = []
        spare = []
        ids = []

        # 获取所有患者ID
        patient_ids = db.session.query(PatientEvent.patient_id).distinct().all()
        patient_ids = [pid[0] for pid in patient_ids]

        # 按患者ID处理数据
        for patient_id in patient_ids:
            # 获取该患者的所有事件，并按时间排序
            events = PatientEvent.query.filter_by(patient_id=patient_id).options(
                joinedload(PatientEvent.patient),
                joinedload(PatientEvent.event)
            ).order_by(PatientEvent.time).all()
            
            if not events or not events[0].patient.in_icu:
                continue  # 跳过没有事件或没有入ICU时间的患者
            
            ids.append(patient_id)
            in_icu_time = events[0].patient.in_icu
            
            # 处理有效事件
            valid_events = []
            valid_times = []
            
            for i, event in enumerate(events):
                seconds_since_icu = (event.time - in_icu_time).total_seconds()
                
                if i == 0:  # 第一条事件直接加入
                    valid_events.append(event.event_id)
                    valid_times.append(seconds_since_icu)
                else:
                    time_diff = seconds_since_icu - valid_times[-1]
                    if time_diff <= time_limit_in_seconds:
                        valid_events.append(event.event_id)
                        valid_times.append(seconds_since_icu)
            # 处理有效事件（现在全部事件都保留）
            valid_events = []
            valid_times = []

            for event in events:
                seconds_since_icu = (event.time - in_icu_time).total_seconds()
                valid_events.append(event.event_id)
                valid_times.append(seconds_since_icu)
            # 处理规则
            patient_rule = []
            diabate_history = events[0].patient.diabete_history
            eh_history = events[0].patient.EH_history
            heart_history = events[0].patient.heart_history
            
            # 检查规则
            for rule in rule_sum:
                event1, event2, event3 = rule
                if event1 != 3:
                    if event1 == 0 and diabate_history == 0:
                        patient_rule.append(0)
                        continue
                    if event1 == 1 and eh_history == 0:
                        patient_rule.append(0)
                        continue
                    if event1 == 2 and heart_history == 0:
                        patient_rule.append(0)
                        continue
                if event1 not in valid_events or event2 not in valid_events:
                    patient_rule.append(0)
                    continue
                if event1 >= len(valid_events) or event2 >= len(valid_events):
                    patient_rule.append(0)
                    continue
                diff = valid_events[event1] - valid_events[event2]
                if diff >= 0:
                    patient_rule.append(1)
                else:
                    patient_rule.append(0)
            
            # 处理序列长度
            pad_length = 100 - len(valid_events)
            spare.append(pad_length)
            if pad_length < 0:
                # 如果事件个数多于500，直接截断
                event_seq = valid_events[:100]
                time_seq = valid_times[:100]
            else:
                # 如果事件个数少于500，补齐
                event_seq = np.pad(valid_events, (0, pad_length), 'constant', constant_values=0)
                time_seq = np.pad(valid_times, (0, pad_length), 'constant', constant_values=0)
            
            event_seqs.append(event_seq)
            time_seqs.append(time_seq)
            rules.append(patient_rule)

        # 转换为Torch Tensor
        event_seqs_tensor = torch.tensor(event_seqs)
        time_seqs_tensor = torch.tensor(time_seqs)
        rules_tensor = torch.tensor(rules)
        ids_tensor = torch.tensor(ids)
        
        return event_seqs_tensor, time_seqs_tensor, rules_tensor, ids_tensor
