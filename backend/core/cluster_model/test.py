import torch.optim as optim
import torch
from core.cluster_model.dataset import EventSequenceDataset
from core.cluster_model.model import EventSequenceClustering
from sklearn.cluster import KMeans

def assign_clusters(features, cluster_centers):
    # features: [batch_size, feature_dim]
    # cluster_centers: [num_clusters, feature_dim]

    # 将 cluster_centers 转换为 Tensor
    cluster_centers = torch.tensor(cluster_centers).to(features.device)
    
    # 计算每个样本到每个簇中心的欧式距离
    distances = torch.cdist(features, cluster_centers)  # 计算欧式距离 [batch_size, num_clusters]

    # 为每个样本选择最近的聚类中心（即最小距离）
    cluster_assignments = torch.argmin(distances, dim=1)  # [batch_size]，表示每个样本所属的簇编号
    return cluster_assignments

def test_clustering_model(event_seqs, time_seqs, rule_features,model_path):
    # 加载模型和其他变量
    checkpoint = torch.load(model_path, weights_only=False)

    # 恢复模型参数
    model_1 = EventSequenceClustering(num_event_types=50, num_rules=9, embedding_dim=10, hidden_dim=64, num_clusters=4)
    model_1.load_state_dict(checkpoint['model_state_dict'])

    # 恢复其他变量
    model_1.num_clusters = checkpoint['num_clusters']
    model_1.cluster_center = checkpoint['cluster_center']

    # 前向传播
    features = model_1(event_seqs, time_seqs, rule_features)

    cluster_assignments = assign_clusters(features, model_1.cluster_center)
    
    return cluster_assignments

    