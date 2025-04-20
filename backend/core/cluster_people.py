from core.cluster_model.event_get import preprocess
from core.cluster_model.test import assign_clusters,test_clustering_model
from main import app
import os
from database.models import PatientCluster, db
def run_model():
    print("开始运行聚类模型...")
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建模型文件的绝对路径
    model_path = os.path.join(current_dir, "cluster_model", "event_sequence_clustering_1_1.pth")
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None
    event_seqs_tensor, time_seqs_tensor, rules_tensor, ids_tensor = preprocess(time_limit=5)
    result=test_clustering_model(event_seqs_tensor, time_seqs_tensor, rules_tensor,model_path=model_path)
    
    with app.app_context():
        # 先清除之前的聚类结果
        PatientCluster.query.delete()
        
        # 遍历结果并保存
        for i, patient_id in enumerate(ids_tensor.numpy()):
            # 获取该患者的聚类结果
            cluster_id = result[i]
            
            # 创建新的PatientCluster记录
            patient_cluster = PatientCluster(
                patient_id=int(patient_id),
                cluster_id=int(cluster_id),
                time=5  # 使用当前时间作为聚类时间
            )
            
            # 添加到数据库会话
            db.session.add(patient_cluster)
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"成功将{len(result)}个患者的聚类结果保存到数据库")
        except Exception as e:
            db.session.rollback()
            print(f"保存聚类结果时出错: {str(e)}")
    model_path = os.path.join(current_dir, "cluster_model", "event_sequence_clustering_1_2.pth")
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None
    event_seqs_tensor, time_seqs_tensor, rules_tensor, ids_tensor = preprocess(time_limit=10)
    result=test_clustering_model(event_seqs_tensor, time_seqs_tensor, rules_tensor,model_path=model_path)
    
    with app.app_context():
        # 先清除之前的聚类结果
        # 遍历结果并保存
        for i, patient_id in enumerate(ids_tensor.numpy()):
            # 获取该患者的聚类结果
            cluster_id = result[i]
            
            # 创建新的PatientCluster记录
            patient_cluster = PatientCluster(
                patient_id=int(patient_id),
                cluster_id=int(cluster_id),
                time=10  # 使用当前时间作为聚类时间
            )
            
            # 添加到数据库会话
            db.session.add(patient_cluster)
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"成功将{len(result)}个患者的聚类结果保存到数据库")
        except Exception as e:
            db.session.rollback()
            print(f"保存聚类结果时出错: {str(e)}")
    model_path = os.path.join(current_dir, "cluster_model", "event_sequence_clustering_1_4.pth")
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None
    event_seqs_tensor, time_seqs_tensor, rules_tensor, ids_tensor = preprocess(time_limit=15)
    result=test_clustering_model(event_seqs_tensor, time_seqs_tensor, rules_tensor,model_path=model_path)
    
    with app.app_context():
        # 先清除之前的聚类结果
        # 遍历结果并保存
        for i, patient_id in enumerate(ids_tensor.numpy()):
            # 获取该患者的聚类结果
            cluster_id = result[i]
            
            # 创建新的PatientCluster记录
            patient_cluster = PatientCluster(
                patient_id=int(patient_id),
                cluster_id=int(cluster_id),
                time=15  # 使用当前时间作为聚类时间
            )
            
            # 添加到数据库会话
            db.session.add(patient_cluster)
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"成功将{len(result)}个患者的聚类结果保存到数据库")
        except Exception as e:
            db.session.rollback()
            print(f"保存聚类结果时出错: {str(e)}")
    model_path = os.path.join(current_dir, "cluster_model", "event_sequence_clustering_1_8.pth")
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None
    event_seqs_tensor, time_seqs_tensor, rules_tensor, ids_tensor = preprocess(time_limit=20)
    result=test_clustering_model(event_seqs_tensor, time_seqs_tensor, rules_tensor,model_path=model_path)
    
    with app.app_context():
        # 先清除之前的聚类结果
        # 遍历结果并保存
        for i, patient_id in enumerate(ids_tensor.numpy()):
            # 获取该患者的聚类结果
            cluster_id = result[i]
            
            # 创建新的PatientCluster记录
            patient_cluster = PatientCluster(
                patient_id=int(patient_id),
                cluster_id=int(cluster_id),
                time=20  # 使用当前时间作为聚类时间
            )
            
            # 添加到数据库会话
            db.session.add(patient_cluster)
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"成功将{len(result)}个患者的聚类结果保存到数据库")
        except Exception as e:
            db.session.rollback()
            print(f"保存聚类结果时出错: {str(e)}")
    return result
