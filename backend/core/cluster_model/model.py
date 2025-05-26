import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.cluster import KMeans
import torch.nn.functional as F


# 自注意力层
class SelfAttention(nn.Module):
    def __init__(self, hidden_dim):
        super(SelfAttention, self).__init__()
        self.attention_weights = nn.Parameter(torch.randn(hidden_dim, hidden_dim))

    def forward(self, x):
        # x 是 (batch_size, seq_len, hidden_dim)
        attn_scores = torch.matmul(x, self.attention_weights)  # (batch_size, seq_len, hidden_dim)
        attn_scores = torch.matmul(attn_scores, x.transpose(1, 2))  # (batch_size, seq_len, seq_len)
        attn_weights = F.softmax(attn_scores, dim=-1)  # 计算注意力权重
        
        # 计算加权的特征表示
        attn_output = torch.matmul(attn_weights, x)  # (batch_size, seq_len, hidden_dim)
        return attn_output

class EventSequenceClustering(nn.Module):
    def __init__(self, num_event_types, num_rules, embedding_dim, hidden_dim, num_clusters):
        super(EventSequenceClustering, self).__init__()
        
        # 事件序号嵌入层
        self.embedding = nn.Embedding(num_event_types, embedding_dim)
        
        # LSTM 层
        self.lstm = nn.LSTM(embedding_dim + 1, hidden_dim, batch_first=True)  # +1 是时间特征
        
        # 自注意力机制层
        self.attn = SelfAttention(hidden_dim)
        
        # 输出层（全连接层）
        self.fc = nn.Linear(hidden_dim + num_rules, hidden_dim)  # LSTM 的输出 + 规则特征

        # 保存聚类中心的变量
        self.num_clusters = num_clusters
        self.cluster_center=torch.zeros(num_clusters, hidden_dim)
        
    def forward(self, event_sequences, time_features, rule_features):
        # event_sequences: [batch_size, seq_length] 事件序号
        # time_features: [batch_size, seq_length] 时间戳
        # rule_features: [batch_size, seq_length, num_rules] 规则数组

        # 将事件序号嵌入到低维空间
        event_embeddings = self.embedding(event_sequences)  # [batch_size, seq_length, embedding_dim]
        
        # 时间特征与事件嵌入拼接
        time_features = time_features.unsqueeze(-1)  # [batch_size, seq_length, 1]
        event_time_features = torch.cat((event_embeddings, time_features), dim=-1)  # [batch_size, seq_length, embedding_dim + 1]

        # LSTM 层
        event_time_features = event_time_features.to(torch.float32)
        lstm_out, _ = self.lstm(event_time_features)  # [batch_size, seq_length, hidden_dim]

        # 自注意力层
        attn_out = self.attn(lstm_out)  # (batch_size, seq_len, hidden_dim)
        attn_out = attn_out.mean(dim=1)  # 对序列长度进行池化，得到 (batch_size, hidden_dim)

        # 拼接规则特征与 LSTM 的输出
        combined_features = torch.cat((attn_out,rule_features), dim=-1)  # [batch_size, hidden_dim + num_rules]


        # 通过全连接层
        output = self.fc(combined_features)  # [batch_size, hidden_dim]
        return output





    
