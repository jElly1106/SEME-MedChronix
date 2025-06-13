# abstract class for both trainer and tester
# Author: Chenghao Yang
from model.xfmr_nhp_fast import XFMRNHPFast
from data.NHPDataset import NHPDataset, createDataLoader
from esm.thinning import EventSampler
import os
import pickle
from tqdm import tqdm
import torch
import numpy
from collections import Counter,defaultdict
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence
torch.set_printoptions(profile="full")
import numpy as np

np.set_printoptions(threshold=np.inf) 
class Manager:
    def __init__(self, args):
        self.args = args
        [self.train_loader,self.test_loader]= self.get_dataloader(args)
        self.model = XFMRNHPFast(self.train_loader.dataset, args.ModelDim, args.Layer, args.NumHead, args.Dropout,
                                 args.TimeEmbeddingDim,num_rule=len(args.rules))
        self.load_pretrained_model(args.pretrained_model_path)

    def load_pretrained_model(self, pretrained_model_path):
        """
        加载预训练的模型权重
        """
        if pretrained_model_path is not None:
            print(f"Loading pretrained model from {pretrained_model_path}")
            
            pretrained_dict = torch.load(pretrained_model_path, map_location=torch.device('cpu'))

            
            # 如果预训练模型的权重是保存为模型的state_dict，直接加载
            model_dict = self.model.state_dict()
            pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
            model_dict.update(pretrained_dict)
            self.model.load_state_dict(model_dict)
            print("Pretrained model loaded successfully.")
        else:
            print("No pretrained model path provided, initializing the model from scratch.")
            
    def get_dataloader(self, args):
        loaders = []
        splits = ['train','tests']
        event_types = None
        token_types = 0
        for _split in splits:
            with open(os.path.join(args.PathDomain, f"{_split}.pkl"), "rb") as f_in:
                # latin-1 for GaTech data
                try:
                    _data = pickle.load(f_in, encoding='latin-1')
                except:
                    _data = pickle.load(f_in)
                if event_types is None:
                    event_types = _data["dim_process"]
                else:
                    assert _data["dim_process"] == event_types, "inconsistent dim_process in different splits?"
                dataset = NHPDataset(_data[_split], event_types, concurrent=False, add_bos=False, add_eos=False,rules=args.rules)
                assert dataset.event_num <= event_types, f"{_split}.pkl has more event types than specified in dim_process!"
                token_types = max(token_types, dataset.num_types)
                loaders.append(createDataLoader(dataset, batch_size=args.BatchSize))
        assert token_types > event_types, f"at least we should include [PAD]! token: {token_types}, event: {event_types}"
        return loaders

    def create_thinningsampler(self, num_sample, num_exp):
        self.thinning_sampler = EventSampler(num_sample, num_exp)

    def run_prediction(self, model:XFMRNHPFast, dataLoader):
        self.thinning_sampler
        
        results = []
        seq_id = 0
        verbose = self.args.Verbose
        thinning_sampler = self.thinning_sampler
        for _batch in tqdm(dataLoader, desc=f"   (Pred)    ", leave=False, mininterval=2):
            time_seq, time_delta_seq, event_seq, batch_non_pad_mask, attention_mask, type_mask = _batch
            # thinning can only run in single instance mode, not in batch mode
            num_batch = time_seq.size(0)
            for i in range(num_batch):
                rst = []
                _time_seq, _event_seq = time_seq[i][batch_non_pad_mask[i]], event_seq[i][batch_non_pad_mask[i]]
                seq_len = _time_seq.size(0)
                duration = _time_seq[-1].item() + numpy.finfo(float).eps
                num_sub = seq_len - 1
                for j in range(seq_len - 1):
                    next_event_name, next_event_time = _event_seq[j + 1].item(), _time_seq[j + 1].item()
                    current_event_name, current_event_time = _event_seq[j].item(), _time_seq[j].item()
                    time_last_event = _time_seq[j].item()
                    if verbose:
                        print(f"for {seq_id}-th seq, predict after {j}-th event {current_event_name} at {current_event_time:.4f}")
                    next_event_dtime = next_event_time - time_last_event
                    avg_future_dtime = (duration - time_last_event) / (num_sub - j)
                    look_ahead = max(next_event_dtime, avg_future_dtime)
                    boundary = time_last_event + 4 * look_ahead
                    _event_prefix, _time_prefix = _event_seq[:j + 1].unsqueeze(0), _time_seq[:j + 1].unsqueeze(0)
                    accepted_times, weights = thinning_sampler.draw_next_time(
                        [[_event_prefix, _time_prefix],
                        time_last_event, boundary, model]
                    )
                    time_uncond = float(torch.sum(accepted_times * weights))
                    dtime_uncond = time_uncond - time_last_event
                    intensities_at_times = model.compute_intensities_at_sampled_times(
                        _event_prefix, _time_prefix,
                        _time_seq[j + 1].reshape(1, 1)
                    )[0, 0]
                    top_ids = torch.argsort(intensities_at_times, dim=0, descending=True)
                    # since we use int to represent event names already
                    top_event_names = [int(top_i) for top_i in top_ids]
                    rst.append(
                        (
                            time_uncond, dtime_uncond, top_event_names,
                            next_event_time, next_event_dtime, next_event_name
                        )
                    )
                    if verbose:
                        print(
                            f"our predicted time is {time_uncond:.4f} and sorted event types are :\n{top_event_names}")
                        print(
                            f"gold ({next_event_name}) ranked {top_event_names.index(next_event_name)} out of {len(top_event_names)}")
                results.append(rst)
                seq_id += 1
        return results
    '''
    def predict_multi_step_since_last_event(self):
        """Multi-step prediction since last event in the sequence.

        Args:
            time_seqs (tensor): [batch_size, seq_len].
            time_delta_seqs (tensor): [batch_size, seq_len].
            type_seqs (tensor): [batch_size, seq_len].
            num_step (int): num of steps for prediction.

        Returns:
            tuple: tensors of dtime and type prediction, [batch_size, seq_len].
        """
        model=self.model
        dataLoader=self.train_loader
        model.eval()
        self.create_thinningsampler(1, 20)
        self.thinning_sampler.cuda()
        thinning_sampler = self.thinning_sampler
        num_step = 6
        for _batch in tqdm(dataLoader, desc=f"   (Pred)    ", leave=False, mininterval=2):
            time_seq, time_delta_seq, event_seq, batch_non_pad_mask, attention_mask, type_mask,rule_result = _batch
            enc_out = model.forward(event_seq.cuda(), time_seq.cuda(), batch_non_pad_mask.cuda(), attention_mask.cuda(),rule_result.cuda())
            #change
            #enc_inten = self.softplus(self.inten_linear(enc_out))
            enc_inten = torch.clamp(model.softplus(model.inten_linear(enc_out)), max=10.0)
            print(enc_inten)
            pred = torch.argmax(enc_inten, dim=-1)[:, :]
            print(len(pred[0]))
            print(pred)
            print('first',time_seq)
            print(len(event_seq[0]))
            print('first',event_seq)
            if time_seq.size(1)<=num_step:
                continue
            time_seq = time_seq[:, :-num_step]
            time_delta_seq = time_delta_seq[:, :-num_step]
            event_seq = event_seq[:, :-num_step]
            print('second',time_seq)
            print('second',event_seq)
            seq_len = time_seq.size(1)
            duration = time_seq[0, -1].item() + numpy.finfo(float).eps  # Prevent zero division
            num_sub = seq_len
            predicted_intensity_list = []
            for i in range(num_step):
                time_first_event = time_seq[0,0].item()
                avg_future_dtime = (duration - time_first_event) / (num_sub)
                boundary = time_seq[0,-1].item() + 1 * avg_future_dtime
                #_event_prefix, _time_prefix = event_seq.unsqueeze(0).cuda(), time_seq.unsqueeze(0).cuda()
                _event_prefix, _time_prefix = event_seq.cuda(), time_seq.cuda()
                # Use thinning sampler to predict next event time
                accepted_times, weights = thinning_sampler.draw_next_time(
                    [[_event_prefix, _time_prefix], time_seq[0,-1].item(), boundary, model,50]
                )
                # Calculate predicted time
                time_uncond = float(torch.sum(accepted_times * weights))
                dtime_uncond = time_uncond - time_seq[0,-1].item()
                # Compute intensities at sampled times for event prediction
                intensities_at_times = model.compute_intensities_at_sampled_times(
                    _event_prefix, _time_prefix, time_seq[0,-1].reshape(1, 1).cuda()
                )[0, 0]

                # Sort intensities to get the most likely event type
                top_ids = torch.argsort(intensities_at_times, dim=0, descending=True)
                top_event_names = [int(top_i) for top_i in top_ids]
                #print(f"Predicted next time: {time_uncond:.4f}, Event types sorted by intensity: {top_event_names}")

                next_event_type = top_event_names[0] 
                time_uncond = torch.full((time_seq.size(0), 1), time_uncond, device=time_seq.device)
                time_seq = torch.cat([time_seq, time_uncond], dim=-1)
                dtime_uncond = torch.full((time_delta_seq.size(0), 1), dtime_uncond, device=time_delta_seq.device)
                time_delta_seq = torch.cat([time_delta_seq, dtime_uncond], dim=-1)
                next_event_type = torch.full((event_seq.size(0), 1), next_event_type, device=event_seq.device)
                event_seq = torch.cat([event_seq, next_event_type], dim=-1) 
                print('top_event_name',top_event_names)    
            print('third',time_seq[:,-num_step:])
            print('third',event_seq[:,-num_step:])
        return time_delta_seq[:, -num_step:], event_seq[:, -num_step:], predicted_intensity_list
    '''
    def predict_multi_step_since_last_event(self):
        """Multi-step prediction since last event in the sequence.

        Args:
            time_seqs (tensor): [batch_size, seq_len].
            time_delta_seqs (tensor): [batch_size, seq_len].
            type_seqs (tensor): [batch_size, seq_len].
            num_step (int): num of steps for prediction.

        Returns:
            tuple: tensors of dtime and type prediction, [batch_size, seq_len].
        """
        model=self.model
        dataLoader=self.test_loader
        model.eval()
        for _batch in tqdm(dataLoader, desc=f"   (Pred)    ", leave=False, mininterval=2):
            time_seq, time_delta_seq, event_seq, batch_non_pad_mask, attention_mask, type_mask,rule_result,ids = _batch
            # enc_out = model.forward(event_seq, time_seq, batch_non_pad_mask, attention_mask,rule_result)
            enc_out = model.forward(event_seq[:, :-1], time_seq[:, :-1], batch_non_pad_mask[:, 1:], attention_mask[:, 1:, :-1],rule_result[:,:-1])
            enc_inten = torch.clamp(model.softplus(model.inten_linear(enc_out)), max=10.0)
            
            print("INTENSITY_MATRIX")
            print(enc_inten.cpu().detach().numpy())
            pred = torch.argmax(enc_inten, dim=-1)[:, :]
            print("PREDICTED_EVENTS")
            print(pred.cpu().detach().numpy())
            # 打印时间序列和事件序列
            print("TIME_SEQUENCE")
            print(time_seq.cpu().detach().numpy())
            
            print("EVENT_SEQUENCE")
            print(event_seq.cpu().detach().numpy())
            print("PATIENT_IDS")
            print(ids)
            
            '''
            output_file = "model_output.txt"
            with open(output_file, 'a') as f:
                f.write("INTENSITY_MATRIX\n")
                f.write(str(enc_inten.cpu().detach().numpy()) + "\n")
                
                pred = torch.argmax(enc_inten, dim=-1)[:, :]
                f.write("PREDICTED_EVENTS\n")
                f.write(str(pred.cpu().detach().numpy()) + "\n")
                
                # 打印时间序列和事件序列
                f.write("TIME_SEQUENCE\n")
                f.write(str(time_seq.cpu().detach().numpy()) + "\n")
                
                f.write("EVENT_SEQUENCE\n")
                f.write(str(event_seq.cpu().detach().numpy()) + "\n")
                
                f.write("PATIENT_IDS\n")
                f.write(str(ids) + "\n")
                
                matches = (pred == event_seq[:,1:])
                correct_counts = matches.sum(dim=1)  # 每个样本的正确个数
                total_counts = len(event_seq[:,1:])
                
                # 若 event_seq 没有 padding 可直接用 pred.shape[1]
                accuracy = correct_counts / total_counts
                print(accuracy)
                f.write("ACCURACY\n")
                f.write(str(accuracy) + "\n")
                if pred.size(1) == 0:
                    continue
                # 2. 判断每条序列最后一个预测值是否等于真实值
                last_match = (pred[:, -1] == event_seq[:, -1])
                last_match_rate = last_match.item()

                f.write("LAST_EVENT_MATCH_RATE\n")
                f.write(str(last_match_rate) + "\n")
                
            print(f"模型输出已保存到 {output_file}")
            '''