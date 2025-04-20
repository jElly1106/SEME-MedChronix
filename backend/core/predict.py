import sys
import os

from sqlalchemy import event

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import PatientCluster, PatientEvent,EventPrediction,db,Patient,PatientPrediction
from sqlalchemy.orm import joinedload
import pandas as pd
from collections import defaultdict
import pickle
import subprocess
from main import app
import math
from datetime import datetime, timedelta
import numpy as np
import re
#from cluster_people import run_model
event_map_49 = {
    '收缩压偏高': 0, '舒张压偏低': 1, 
    '呼吸频率偏高': 2, '血氧饱和度偏低': 3, '心率偏高': 4, 
    '呼吸频率偏低': 5, '平均动脉压偏低': 6, '血红蛋白偏低': 7, 
    '血糖偏高': 8, '凝血酶原时间偏高': 9, 'INR偏高': 10, '白细胞计数偏高': 11, 
    '高度昏迷': 12, '动脉血氧分压偏高': 13, '红细胞压积偏低': 14, 
    '动脉血二氧化碳分压偏高': 15, '动脉血二氧化碳分压偏低': 16, 'PTT偏高': 17, 
    '氯离子偏高': 18, '肌酐偏高': 19, '钠离子偏高': 20, 
    '收缩压偏低': 21, '舒张压偏高': 22, 
    '平均动脉压偏高': 23, '碳酸氢盐偏低': 24, '白细胞计数偏低': 25, 
    '动脉血氧分压偏低': 26, '血尿素氮偏高': 27, '碳酸氢盐偏高': 28, '阴离子间隙偏低': 29, 
    '血小板计数偏低': 30, '动脉碱剩余偏高': 31, '氯离子偏低': 32, 
    '体温偏高': 33, '钾离子偏低': 34, '血小板计数偏高': 35, 
    '心率偏低': 36, '阴离子间隙偏高': 37, '钾离子偏高': 38, '钠离子偏低': 39, 
    '肌酐偏低': 40, '血尿素氮偏低': 41, 'PTT偏低': 42, '体温偏低': 43, 
    '凝血酶原时间偏低': 44, '血糖偏低': 45, '血红蛋白偏高': 46, '红细胞压积偏高': 47, 
    'INR偏低': 48
}
 
event_map_13 = {
    '体温偏高': 0, '心率偏低': 1,
    '血氧饱和度偏低': 2, '高度昏迷': 3,
    '呼吸频率偏高': 4, '平均动脉压偏低': 5
}

# 创建反向映射（从id到name）
reverse_map_49 = {v: k for k, v in event_map_49.items()}
def reverse_map_event_id(event_id_13):
    """将13个事件的ID映射回49个事件的ID"""
    # 创建13到49的映射
    for event_name, id_13 in event_map_13.items():
        if id_13 == event_id_13:
            # 找到对应的事件名称后，查找在49事件映射中的ID
            return event_map_49[event_name]
    return None
def map_event_id(event_id):
    """将49个事件的ID映射到13个事件的ID"""
    if event_id not in reverse_map_49:
        return None
    event_name = reverse_map_49[event_id]
    return event_map_13.get(event_name, None)
def query_and_prepare_data(test_pkl):
    # 优化1: 分批次查询数据，避免一次性加载全部数据
    batch_size = 1000
    offset = 0
    all_results = []
    
    # 优化2: 预先获取所有患者的入ICU时间，避免重复查询
    patients_dict = {}
    patients = Patient.query.all()
    for patient in patients:
        if patient.in_icu:
            patients_dict[patient.id] = patient
    
    while True:
        # 分批查询数据
        batch = PatientEvent.query.options(
            joinedload(PatientEvent.event)
        ).order_by(PatientEvent.patient_id, PatientEvent.time).offset(offset).limit(batch_size).all()
        
        if not batch:
            break
            
        # 优化3: 批量处理数据
        batch_results = []
        
        for patient_event in batch:
            patient_id = patient_event.patient_id
            if patient_id not in patients_dict:
                continue
                
            in_icu_time = patients_dict[patient_id].in_icu
            event_time = patient_event.time
            hours_since_icu = (event_time - in_icu_time).total_seconds() / 3600
            
            # 优化4: 直接使用映射字典，避免函数调用开销
            event_id = patient_event.event.id
            mapped_event_type = event_map_13.get(patient_event.event.name)
            
            if mapped_event_type is not None:
                batch_results.append({
                    'id': patient_id,
                    't': hours_since_icu,
                    'event_type': mapped_event_type,
                    'k': patient_event.event.name,
                    'heart_history': 1 if patients_dict[patient_id].heart_history == "有" else 0,
                    'diabate_history': 1 if patients_dict[patient_id].diabete_history == "有" else 0,
                    'EH_history': 1 if patients_dict[patient_id].EH_history == "有" else 0,
                })
        
        all_results.extend(batch_results)
        offset += batch_size
    
    # 优化5: 使用字典直接构建分组数据，避免DataFrame操作
    groups = defaultdict(list)
    last_time = {}  # 记录每个患者的上一个事件时间
    
    # 按ID排序
    all_results.sort(key=lambda x: (x['id'], x['t']))
    
    for record in all_results:
        patient_id = record['id']
        current_time = record['t']
        
        # 计算时间差
        if patient_id in last_time:
            delta_t = current_time - last_time[patient_id]
        else:
            delta_t = current_time
            
        last_time[patient_id] = current_time
        
        # 构建记录
        event_record = {
            'id': patient_id,
            'time_since_last_event': float(delta_t),
            'time_since_start': float(current_time),
            'type_event': int(record['event_type']),
            'diabetes': int(record['diabate_history']),
            'heart': int(record['heart_history']),
            'EH': int(record['EH_history']),
            'k': str(record['k'])
        }
        groups[patient_id].append(event_record)
    '''
    max_group_size=       
    new_groups = defaultdict(list)
    for key in groups:
        if len(groups[key]) > max_group_size:
            # 截取最后 100 个时间点
            new_group = groups[key][-max_group_size:]
            # 记得将原始的最后 100 个时间点也加入到 new_groups
            new_groups[key] = new_group
        else:
            new_groups[key] = groups[key]
    '''
    # 将按 id 分组后的结果转为列表形式
    all_groups = list(groups.values())
    
    # 构造输出字典
    test_dict = {'dim_process': 15, 'test': all_groups}
    
    # 确保目录存在
    os.makedirs(os.path.dirname(test_pkl), exist_ok=True)
    
    # 保存为pickle文件
    with open(test_pkl, 'wb') as f:
        pickle.dump(test_dict, f)
    
    print(f"Test 数据已保存到 {test_pkl}")

def run_command_with_args(test_path, test_data_path, test_model_path):
    import numpy as np
    my_env = os.environ.copy()
    my_env["CUDA_VISIBLE_DEVICES"] = ""
    my_env["PYTHONIOENCODING"] = "utf-8"
    # 定义命令行及其参数
    command = ["python", test_path, "-d", test_data_path, "-ps", "./", "-bs", "1", "-d_model", "128", "-teDim", "64", "-sd", "1111", "-layer", "3", "-rules", "[[1,(0)]]", "-pretrained_model_path", test_model_path]
    # 使用 subprocess.run 调用命令并等待其完成
    result = subprocess.run(
        command, 
        capture_output=True, 
        text=True, 
        encoding='utf-8',
        env=my_env
    )
    
    if result.returncode != 0:
        print("错误输出:", result.stderr)
        raise Exception(f"Command failed with exit code {result.returncode}")
    
    # 保存原始输出到文件，方便调试
    with open(os.path.join(test_data_path, "output.txt"), "w", encoding="utf-8") as f:
        f.write(result.stdout)
    
    # 初始化变量 - 改为列表以累积多个batch的结果
    all_intensity_matrices = []
    all_predicted_events = []
    all_time_sequences = []
    all_event_sequences = []
    all_patient_ids = []
    
    # 使用正则表达式提取数据块
    stdout_content = result.stdout
    
    # 提取强度矩阵块
    intensity_blocks = re.findall(r"INTENSITY_MATRIX\s*(.*?)(?=PREDICTED_EVENTS|\Z)", stdout_content, re.DOTALL)
    for block in intensity_blocks:
        try:
            # 提取所有数字（包括科学计数法）
            numbers = re.findall(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?", block)
            if not numbers:
                continue
                
            # 确定矩阵结构 - 从输出格式看是三维矩阵 [batch_size, seq_len, event_types]
            # 从输出中可以看到每行有15个元素（事件类型数量）
            elements_per_row = 15
            
            print(f"提取到 {len(numbers)} 个数值，每行 {elements_per_row} 个元素")
            
            # 将所有数字转换为浮点数
            float_numbers = [float(num) for num in numbers]
            
            # 重构矩阵 - 每行15个元素
            rows = []
            for i in range(0, len(float_numbers), elements_per_row):
                if i + elements_per_row <= len(float_numbers):
                    rows.append(float_numbers[i:i+elements_per_row])
                else:
                    # 如果最后一行不完整，填充到15个元素
                    row = float_numbers[i:]
                    row.extend([0.0] * (elements_per_row - len(row)))
                    rows.append(row)
            
            # 添加到强度矩阵列表
            all_intensity_matrices.append(rows)
            print(f"解析出 {len(rows)} 行数据")
            
        except Exception as e:
            print(f"解析强度矩阵时出错: {str(e)}")
    
    # 提取预测事件块
    predicted_blocks = re.findall(r"PREDICTED_EVENTS\s*(.*?)(?=TIME_SEQUENCE|\Z)", stdout_content, re.DOTALL)
    for block in predicted_blocks:
        try:
            # 提取所有数字
            numbers = re.findall(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?|\d+", block)
            if not numbers:
                continue
                
            # 假设这是一个一维数组
            events = [int(float(num)) for num in numbers]
            all_predicted_events.append([events])  # 添加一个额外的维度以匹配预期格式
        except Exception as e:
            print(f"解析预测事件时出错: {str(e)}")
    
    # 提取时间序列块
    time_blocks = re.findall(r"TIME_SEQUENCE\s*(.*?)(?=EVENT_SEQUENCE|\Z)", stdout_content, re.DOTALL)
    for block in time_blocks:
        try:
            # 提取所有数字
            numbers = re.findall(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?|\d+", block)
            if not numbers:
                continue
                
            # 假设这是一个一维数组
            times = [float(num) for num in numbers]
            all_time_sequences.append([times])  # 添加一个额外的维度以匹配预期格式
        except Exception as e:
            print(f"解析时间序列时出错: {str(e)}")
    
    # 提取事件序列块
    event_blocks = re.findall(r"EVENT_SEQUENCE\s*(.*?)(?=PATIENT_IDS|\Z)", stdout_content, re.DOTALL)
    for block in event_blocks:
        try:
            # 提取所有数字
            numbers = re.findall(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?|\d+", block)
            if not numbers:
                continue
                
            # 假设这是一个一维数组
            events = [int(float(num)) for num in numbers]
            all_event_sequences.append([events])  # 添加一个额外的维度以匹配预期格式
        except Exception as e:
            print(f"解析事件序列时出错: {str(e)}")
    
    # 提取患者ID块
    patient_blocks = re.findall(r"PATIENT_IDS\s*(.*?)(?=INTENSITY_MATRIX|\Z)", stdout_content, re.DOTALL)
    for block in patient_blocks:
        try:
            # 提取所有数字
            numbers = re.findall(r"\d+", block)
            if not numbers:
                continue
                
            # 假设这是一个一维数组
            ids = [int(num) for num in numbers]
            all_patient_ids.append(ids)
        except Exception as e:
            print(f"解析患者ID时出错: {str(e)}")
    
    # 如果没有成功解析患者ID，则从test.pkl中获取
    if not all_patient_ids:
        print("未从输出中解析到患者ID，尝试从test.pkl中获取")
        with open(os.path.join(test_data_path, "test.pkl"), 'rb') as f:
            test_data = pickle.load(f)
        all_patient_ids = [[group[0]['id']] for group in test_data['test']]
    # print("\n数组形状信息:")
    # print(f"all_intensity_matrices: {len(all_intensity_matrices)} 个批次")
    # if all_intensity_matrices:
    #     print(f"  - 第一个批次: {len(all_intensity_matrices[0])} 行 x {len(all_intensity_matrices[0][0]) if all_intensity_matrices[0] else 0} 列")
    
    # print(f"all_time_sequences: {len(all_time_sequences)} 个批次")
    # if all_time_sequences:
    #     print(f"  - 第一个批次: {len(all_time_sequences[0])} 个序列，第一个序列长度: {len(all_time_sequences[0][0]) if all_time_sequences[0] else 0}")
    
    # print(f"all_event_sequences: {len(all_event_sequences)} 个批次")
    # print(all_event_sequences)
    # if all_event_sequences:
    #     print(f"  - 第一个批次: {len(all_event_sequences[0])} 个序列，第一个序列长度: {len(all_event_sequences[0][0]) if all_event_sequences[0] else 0}")
    
    # print(f"all_patient_ids: {len(all_patient_ids)} 个批次")
    # if all_patient_ids:
    #     print(f"  - 第一个批次: {len(all_patient_ids[0])} 个ID")
    # print()
    
    # 处理解析后的数据
    all_predictions = []
    
    # 确保所有列表长度一致
    batch_count = min(len(all_intensity_matrices), len(all_time_sequences), len(all_event_sequences), len(all_patient_ids)) if all_intensity_matrices and all_time_sequences and all_event_sequences and all_patient_ids else 0
    for batch in range(batch_count):
        intensity_matrix = all_intensity_matrices[batch]
        time_sequence = all_time_sequences[batch][0]  # 直接获取第一个元素，因为每个批次只有一个患者
        event_sequence = all_event_sequences[batch][0]  # 同上
        patient_id = all_patient_ids[batch][0] if isinstance(all_patient_ids[batch], list) else all_patient_ids[batch]  # 确保获取单个ID
        
        patient_predictions = {
            'id': patient_id,
            'historical_events': [],
            'future_events': []
        }
        
        # 处理历史事件（前n-1个时间点）
        seq_length = len(time_sequence)
        
        if seq_length > 0:
            for j in range(seq_length - 1):  # 除了最后一个时间点
                # 获取该时间点的所有事件强度
                event_intensities = intensity_matrix[j] if j < len(intensity_matrix) else []
                # 确保event_intensities是列表
                if isinstance(event_intensities, (int, float)):
                    event_intensities = [event_intensities]
                
                # 只取前13个事件强度（有效的事件类型）
                event_intensities = event_intensities[:6] if len(event_intensities) > 6 else event_intensities
                
                # 归一化强度值（使用softmax）
                normalized_intensities = softmax(event_intensities)
                
                # 记录该时间点的信息
                patient_predictions['historical_events'].append({
                    'time': time_sequence[j+1],
                    'event_type': event_sequence[j+1],
                    'all_event_types': list(range(len(event_intensities))),
                    'all_intensities': normalized_intensities.tolist() if isinstance(normalized_intensities, np.ndarray) else normalized_intensities
                })
        
        # 处理最后一个时间点（预测未来事件）
        if seq_length > 0:
            last_time = time_sequence[-1]
            last_intensities = intensity_matrix[-1] if len(intensity_matrix) > 0 else []
            
            # 确保last_intensities是列表
            if isinstance(last_intensities, (int, float)):
                last_intensities = [last_intensities]
            
            # 只取前13个事件强度（有效的事件类型）
            last_intensities = last_intensities[:6] if len(last_intensities) > 6 else last_intensities
                
            if last_intensities:
                # 找出强度最大的3个事件类型
                top_indices = sorted(range(len(last_intensities)), key=lambda k: last_intensities[k], reverse=True)[:min(3, len(last_intensities))]
                # 归一化所有强度
                normalized_intensities = softmax(last_intensities)
                
                # 为每个强度最大的事件类型计算预测时间
                for idx in top_indices:
                    intensity = normalized_intensities[idx]
                    # 避免除以零
                    if intensity > 0:
                        time_delta = 1.0 / intensity  # 强度的倒数作为时间增量
                    else:
                        time_delta = 24.0  # 默认24小时
                    
                    predicted_time = last_time + time_delta
                    
                    # 记录预测事件
                    patient_predictions['future_events'].append({
                        'time': predicted_time,
                        'event_type': idx,  # 这里是13类事件中的索引
                        'probability': float(normalized_intensities[idx]) if isinstance(normalized_intensities, np.ndarray) else normalized_intensities[idx]
                    })
        
        all_predictions.append(patient_predictions)
    
    return all_predictions

def softmax(x):
    """计算softmax值，用于归一化概率分布"""
    e_x = np.exp(x - np.max(x))  # 减去最大值以提高数值稳定性
    return e_x / e_x.sum()

def save_predictions_to_db(all_predictions):
    """将预测结果保存到数据库"""
    with app.app_context():
        # 清空现有数据
        EventPrediction.query.delete()
        PatientPrediction.query.delete()
        db.session.commit()
        
        event_predictions = []
        patient_predictions = []
        
        for patient_data in all_predictions:
            patient_id = patient_data['id']
            
            # 获取患者的ICU入院时间
            patient = Patient.query.get(patient_id)
            if not patient or not patient.in_icu:
                print(f"患者 {patient_id} 未找到或无入ICU时间记录")
                continue
            
            # 处理历史事件
            for event_data in patient_data['historical_events']:
                event_time = patient.in_icu + timedelta(hours=event_data['time'])
                
                # 为每个事件类型创建预测记录
                for idx, event_type in enumerate(event_data['all_event_types']):
                    # 将13类事件ID映射回49类事件ID
                    event_id_49 = reverse_map_event_id(event_type)
                    if event_id_49 is None:
                        print(f"警告: 无法将事件类型 {event_type} 映射到49类事件ID")
                        continue
                    
                    probability = event_data['all_intensities'][idx]
                    
                    event_predictions.append(EventPrediction(
                        patient_id=patient_id,
                        event_id=event_id_49,
                        probability=probability,
                        time=event_time
                    ))
            
            # 处理未来事件预测
            for event_data in patient_data['future_events']:
                event_time = patient.in_icu + timedelta(hours=event_data['time'])
                
                # 将13类事件ID映射回49类事件ID
                event_id_49 = reverse_map_event_id(event_data['event_type'])
                if event_id_49 is None:
                    print(f"警告: 无法将预测事件类型 {event_data['event_type']} 映射到49类事件ID")
                    continue
                
                # 添加到EventPrediction表
                event_predictions.append(EventPrediction(
                    patient_id=patient_id,
                    event_id=event_id_49,
                    probability=event_data['probability'],
                    time=event_time
                ))
                
                # 添加到PatientPrediction表
                patient_predictions.append(PatientPrediction(
                    patient_id=patient_id,
                    event_id=event_id_49,
                    time=event_time
                ))
        
        # 批量添加记录
        if event_predictions:
            db.session.add_all(event_predictions)
        if patient_predictions:
            db.session.add_all(patient_predictions)
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"成功保存 {len(event_predictions)} 条事件预测和 {len(patient_predictions)} 条患者预测")
        except Exception as e:
            db.session.rollback()
            print(f"保存预测结果时出错: {str(e)}")


def run():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_pkl_path = os.path.join(current_dir, "anhp_with_rule", "data", "test.pkl")
    test_path=os.path.join(current_dir, "anhp_with_rule", "test1.py")
    test_data_path=os.path.join(current_dir, "anhp_with_rule", "data")
    test_model_path=os.path.join(current_dir, "anhp_with_rule","model.pth")
    with app.app_context(): 
        print("开始查询和准备数据...")
        query_and_prepare_data(test_pkl_path)
        print("数据准备完成，开始运行预测模型...")
        predictions = run_command_with_args(test_path, test_data_path, test_model_path)
        print("模型运行完成，开始保存预测结果到数据库...")
        save_predictions_to_db(predictions)
        print("预测结果保存完成。")
        
        return predictions
if __name__ == "__main__":
    run()
    