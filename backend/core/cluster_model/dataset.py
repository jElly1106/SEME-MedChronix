import torch
from torch.utils.data import Dataset

class EventSequenceDataset(Dataset):
    def __init__(self, event_seqs, time_seqs, rule_features, labels=None):
        """
        初始化数据集
        :param event_seqs: 事件序列数据，形状为 (num_samples, seq_length, 2) 每个事件是[时间, 事件序号]
        :param time_seqs: 时间序列数据，形状为 (num_samples, seq_length)
        :param rule_features: 规则特征数据，形状为 (num_samples, num_rules)
        """
        self.event_seqs = event_seqs
        self.time_seqs = time_seqs
        self.rule_features = rule_features

    def __len__(self):
        """
        返回数据集的大小（样本数）
        """
        return len(self.event_seqs)

    def __getitem__(self, idx):
        """
        返回指定索引的数据（事件序列、时间、规则特征）
        """
        event_seq = self.event_seqs[idx]      # 事件序列
        time_seq = self.time_seqs[idx]        # 时间序列
        rule_feature = self.rule_features[idx] # 规则特征

        return event_seq, time_seq, rule_feature


