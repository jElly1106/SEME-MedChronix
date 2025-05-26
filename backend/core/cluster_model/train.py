# event_sequences: [batch_size, seq_length]，时间序列的事件索引
# time_features: [batch_size, seq_length]，每个事件的时间戳
# rule_features: [batch_size, seq_length, num_rules]，规则满足情况的二值数组
import torch.optim as optim
import torch
from dataset import EventSequenceDataset
from model import EventSequenceClustering
from sklearn.cluster import KMeans

event_seqs = torch.load('event_seqs_1.pt')
time_seqs = torch.load('time_seqs_1.pt')
rule_features = torch.load('rules_1.pt')

# 创建模型
model = EventSequenceClustering(num_event_types=50, num_rules=9, embedding_dim=10, hidden_dim=64, num_clusters=4)
#可以修改聚类数
# 初始化优化器
optimizer = optim.Adam(model.parameters(), lr=0.001)
total_loss=[]
# 损失函数定义
def clustering_loss(features, cluster_centers):
    # 计算特征与聚类中心的欧式距离
    # features: [batch_size, feature_dim]
    # cluster_centers: [num_clusters, feature_dim]
    
    # 将 cluster_centers 转换为 Tensor
    cluster_centers = torch.tensor(cluster_centers).to(features.device)

    # 计算距离矩阵，形状为 [batch_size, num_clusters]
    distances = torch.cdist(features, cluster_centers)  # 欧式距离计算

    # 对于每个样本，选择与其最近的聚类中心的距离
    min_distances, _ = torch.min(distances, dim=1)

    # 聚类损失：最小距离的平方和
    loss = torch.sum(min_distances ** 2)  # 可以根据需要调整
    return loss

num_epochs = 100  # 训练 10 个 epoch

for epoch in range(num_epochs):
    # 迭代 DataLoader
    print(event_seqs.shape, time_seqs.shape, rule_features.shape)
    
    optimizer.zero_grad()

    # 前向传播
    features = model(event_seqs, time_seqs, rule_features)
    print(f"feature{features.shape}")
    kmeans=KMeans(n_clusters=model.num_clusters, init=model.cluster_center)
    kmeans.fit(features.detach().cpu().numpy())
    # 获取聚类中心
    model.cluster_center = kmeans.cluster_centers_
    labels=kmeans.labels_
    print(f"labels{len(labels)}")
    print(labels.size)
    # 计算聚类损失
    loss = clustering_loss(features, model.cluster_center)
    total_loss.append(loss.item())
    # 反向传播
    loss.backward()
    optimizer.step()

    print(f"Loss: {loss.item()}")

# 保存模型
# torch.save(model.state_dict(), 'event_sequence_clustering.pth')
# 保存模型的状态字典和其他变量
torch.save({
    'model_state_dict': model.state_dict(),
    'num_clusters': model.num_clusters,
    'cluster_center': model.cluster_center,
}, 'event_sequence_clustering_1_8.pth')

x = range(1, len(total_loss) + 1)
import matplotlib.pyplot as plt
# 生成图形

plt.plot(x, total_loss, label="Loss")
plt.xlabel("Iteration")
plt.ylabel("Loss")
plt.title("Loss Curve")
plt.legend()
plt.grid()
plt.show() 