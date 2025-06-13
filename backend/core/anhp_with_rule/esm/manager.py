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
class Manager:
    def __init__(self, args):
        self.args = args
        [self.train_loader, self.dev_loader, self.test_loader] \
            = self.get_dataloader(args)
        self.model = XFMRNHPFast(self.train_loader.dataset, args.ModelDim, args.Layer, args.NumHead, args.Dropout,
                                 args.TimeEmbeddingDim,num_rule=len(args.rules)).cuda()
        
        self.writer = args.TensorboardWriter
        self.savePath=args.PathSave
        train_dataset = self.train_loader.dataset
        event_seqs = train_dataset.event_seq  # List[List[int]]
        pad_idx = train_dataset.pad_index

        # 展平并去掉 PAD
        flat_events = [int(e) for seq in event_seqs for e in seq if e != pad_idx]

        # 统计每类的出现次数
        counter = Counter(flat_events)
        total = sum(counter.values())
        
        # 生成类别权重（出现越少权重越大）
        weights = []
        for i in range(train_dataset.num_types):
            weights.append(total / counter.get(i, 1))  # 防止为0除

        # 保存为 Tensor
        self.type_weights = torch.tensor(weights, dtype=torch.float32).cuda()
    def get_dataloader(self, args):
        loaders = []
        splits = ["train", 'dev', 'tests']
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

    def run_one_iteration(self, model:XFMRNHPFast, dataLoader, mode, optimizer=None,epoch=0):
        assert mode in {"train", "eval","tests"}
        if mode == "eval" or "tests":
            model = model.eval()
        else:
            assert optimizer is not None
        total_log_like = 0
        total_acc = 0
        total_event_ll, total_non_event_ll = 0, 0
        num_tokens = 0
        pad_idx = self.train_loader.dataset.pad_index
        num_events = 0
        all_logs = []
        all_logs_token = []
        all_type_ll_token = []
        all_time_ll_token = []
        #change total_type_ll, total_time_ll = 0.0, 0.0
        all_pred_times = []
        all_true_times = []
        all_time_masks = []
        total_type_ll, total_time_ll = 0.0, 0.0
        total_mean_interval_loss=0.0
        #change 
        correct_per_type = defaultdict(int)   # 每个类型预测对了多少次
        total_per_type = defaultdict(int)     # 每个类型一共出现了多少次
        for batch in tqdm(dataLoader, mininterval=2, desc=f'   - ({mode}) -    ', leave=False):
            new_batch = [x.cuda() for x in batch]
            time_seq, time_delta_seq, event_seq, batch_non_pad_mask, attention_mask, type_mask,rule_result = new_batch
            #change 增加了sampled_times, sampled_lambdas的接收
            event_ll, non_event_ll, enc_inten, sampled_times, sampled_lambdas,focus_inten = model.compute_loglik(new_batch)
            if hasattr(self.args, "IgnoreFirst"):
                if self.args.IgnoreFirst:
                    non_event_ll[:, 0] *= 0
            #_batch_loss = event_ll.sum(dim=-1) - non_event_ll.sum(dim=-1)
            #_loss = -torch.sum(_batch_loss)
            #忽略了event_nll,因此加权进行调节
            #change
            original_event_ll = event_ll.detach()
            type_lls = event_ll - torch.log(enc_inten.sum(dim=-1) + model.eps)
            time_lls = event_ll - non_event_ll - type_lls

            # === 2. 加类别权重
            if model.add_bos:
                event_types = event_seq[:, 1:]
                mask = batch_non_pad_mask[:, 1:]
            else:
                event_types = event_seq
                mask = batch_non_pad_mask
            
            type_weights = self.type_weights.to(event_types.device)
            type_weights = torch.sqrt(type_weights)
            type_weights = torch.clamp(type_weights, max=5.0)
            type_weights[5]=10
            
            token_weights = type_weights[event_types]  # shape: [B, L]
            type_lls = type_lls * token_weights * mask  # 加权

            # === 3. 重组 event_ll 并计算 loss
            event_ll = type_lls + time_lls
            
            alpha = self.args.EventWeight if hasattr(self.args, "EventWeight") else 0.15
            _batch_loss = alpha * event_ll.sum(dim=-1) - (1 - alpha) * non_event_ll.sum(dim=-1)

            # 提取 ground truth
            if model.add_bos:
                gt_event_types = event_seq[:, 1:]
                mask = batch_non_pad_mask[:, 1:]
                true_times_delta = time_delta_seq[:, 1:]
            else:
                gt_event_types = event_seq
                mask = batch_non_pad_mask
                true_times_delta = time_delta_seq
            
            predicted_event_types = torch.argmax(enc_inten, dim=-1)  # [B, L]

            # 获取每个位置预测事件类型的 λ（强度），即最大类别的强度值
            # -> 用 gather 从 enc_inten 中挑选出最大类型对应的 λ 值
            predicted_lambda = enc_inten.gather(
                dim=-1,
                index=predicted_event_types.unsqueeze(-1)  # [B, L, 1]
            ).squeeze(-1)  # -> [B, L]

            # 为数值稳定加一点 epsilon，防止除以 0
            eps = 1e-6
            predicted_interval = 1.0 / (predicted_lambda + eps)  # [B, L]

            # 真实的时间间隔
            true_interval = true_times_delta  # [B, L]

            # mask 掉 padding 的位置（取 batch_non_pad_mask 中的对应位置）
            time_interval_loss = (predicted_interval - true_interval).abs()
            masked_time_interval_loss = time_interval_loss[batch_non_pad_mask[:, 1:].bool()]
            mean_interval_loss = masked_time_interval_loss.sum()
            #print(mean_interval_loss)
            _loss = -torch.sum(_batch_loss)+20*mean_interval_loss
           
            if mode == "train":
                _loss.backward()
                optimizer.step()
                optimizer.zero_grad()

            total_log_like += -_loss.item()
            total_event_ll += event_ll.sum().item()
            total_non_event_ll += non_event_ll.sum().item()
            total_mean_interval_loss+=mean_interval_loss.sum().item()
            #change 加上了with torch.no_grad():
            with torch.no_grad():
                type_lls = original_event_ll - torch.log(enc_inten.sum(dim=-1) + model.eps)
                time_lls = original_event_ll - non_event_ll - type_lls
                if model.add_bos:
                    #change 增加pred = torch.argmax(enc_inten, dim=-1)[:, :] true_times = time_seq[:, 1:]   mask = batch_non_pad_mask[:, 1:]
                    pred = torch.argmax(enc_inten, dim=-1)[:, :]
                    truth = event_seq[:, 1:] 
                    true_times = time_seq[:, 1:]
                    #print('true_times',time_seq)
                    mask = batch_non_pad_mask[:, 1:]
                    total_acc += ((torch.argmax(enc_inten, dim=-1) == event_seq[:, 1:]) * batch_non_pad_mask[:, 1:]).sum()
                    num_tokens += event_seq[:, 1:].ne(pad_idx).sum().item()
                    num_events += (event_seq[:, 1:] < pad_idx).sum().item()
                    all_logs_token.extend([(x, 1.0) for x in (event_ll - non_event_ll)[batch_non_pad_mask[:, 1:]].tolist()])
                    all_type_ll_token.extend([(x, 1.0) for x in type_lls[batch_non_pad_mask[:, 1:]].tolist()])
                    all_time_ll_token.extend([(x, 1.0) for x in time_lls[batch_non_pad_mask[:, 1:]].tolist()])
                else:
                    #change pred = torch.argmax(enc_inten, dim=-1) true_times = time_seq  mask = batch_non_pad_mask 
                    pred = torch.argmax(enc_inten, dim=-1)
                    truth = event_seq
                    true_times = time_seq
                    #print('true_times',time_seq)
                    mask = batch_non_pad_mask  
                    total_acc += ((torch.argmax(enc_inten, dim=-1) == event_seq) * batch_non_pad_mask).sum()
                    num_tokens += event_seq.ne(pad_idx).sum().item()
                    num_events += (event_seq < pad_idx).sum().item()
                    all_logs_token.extend([(x, 1.0) for x in (event_ll - non_event_ll)[batch_non_pad_mask].tolist()])
                    all_type_ll_token.extend([(x, 1.0) for x in type_lls[batch_non_pad_mask].tolist()])
                    all_time_ll_token.extend([(x, 1.0) for x in time_lls[batch_non_pad_mask].tolist()])
                #change all_logs之前都是增加内容
                unique_types = truth[mask].unique()
                for t in unique_types:
                    t = t.item()
                    mask_t = (truth == t) & mask
                    correct_per_type[t] += ((pred == truth) & mask_t).sum().item()
                    total_per_type[t] += mask_t.sum().item()
                
                argmax_idx = sampled_lambdas.argmax(dim=0)
                batch_size, seq_len = argmax_idx.shape

                pred_times = sampled_times[
                    argmax_idx,
                    torch.arange(batch_size).unsqueeze(1).expand(-1, seq_len),
                    torch.arange(seq_len).unsqueeze(0).expand(batch_size, -1)
                ]
                #print('pred_times',pred_times)
                # 保存当前 batch 的预测、真实和 mask
                all_pred_times.append(pred_times.detach().cpu())
                all_true_times.append(true_times.detach().cpu())
                all_time_masks.append(mask.detach().cpu())
                all_logs.extend([(x, y) for x, y in zip(_batch_loss.tolist(), event_seq.ne(pad_idx).sum(dim=-1).tolist())])
                #change
                total_type_ll += type_lls.sum().item()
                total_time_ll += time_lls.sum().item()
        #change
        if num_tokens > 0 and mode=='train':
            self.writer.add_scalar("Train/internal_loss", total_mean_interval_loss/num_tokens, epoch)
            self.writer.add_scalar("Train/Type_NLL", -total_type_ll / num_tokens, epoch)
            self.writer.add_scalar("Train/Time_NLL", -total_time_ll / num_tokens, epoch)
            flattened = [row for batch in all_pred_times for row in batch]
            all_pred_times = pad_sequence(flattened, batch_first=True, padding_value=0.0)
            flattened = [row for batch in all_true_times for row in batch]
            all_true_times = pad_sequence(flattened, batch_first=True, padding_value=0.0)
            flattened = [row for batch in all_time_masks for row in batch]
            all_time_masks = pad_sequence(flattened, batch_first=True, padding_value=0.0)
            #all_pred_times = torch.cat(all_pred_times, dim=0)
            #all_true_times = torch.cat(all_true_times, dim=0)
            #all_time_masks = torch.cat(all_time_masks, dim=0)

            mse = ((all_pred_times - all_true_times) ** 2)[all_time_masks.bool()].mean()
            rmse = torch.sqrt(mse).item()
            self.writer.add_scalar("Train/Time_RMSE", rmse, epoch)
            for t in sorted(total_per_type.keys()):
                acc_t = correct_per_type[t] / total_per_type[t] if total_per_type[t] > 0 else 0
                self.writer.add_scalar(f"Train/Type_Accuracy_{t}", acc_t, epoch)
        if num_tokens > 0 and mode=='eval':
            self.writer.add_scalar("Val/Type_NLL", -total_type_ll / num_tokens, epoch)
            self.writer.add_scalar("Val/Time_NLL", -total_time_ll / num_tokens, epoch)
            flattened = [row for batch in all_pred_times for row in batch]
            all_pred_times = pad_sequence(flattened, batch_first=True, padding_value=0.0)
            flattened = [row for batch in all_true_times for row in batch]
            all_true_times = pad_sequence(flattened, batch_first=True, padding_value=0.0)
            flattened = [row for batch in all_time_masks for row in batch]
            all_time_masks = pad_sequence(flattened, batch_first=True, padding_value=0.0)
            #all_pred_times = torch.cat(all_pred_times, dim=0)
            #all_true_times = torch.cat(all_true_times, dim=0)
            #all_time_masks = torch.cat(all_time_masks, dim=0)
            mse = ((all_pred_times - all_true_times) ** 2)[all_time_masks.bool()].mean()
            rmse = torch.sqrt(mse).item()
            self.writer.add_scalar("Val/Time_RMSE", rmse, epoch)
            for t in sorted(total_per_type.keys()):
                acc_t = correct_per_type[t] / total_per_type[t] if total_per_type[t] > 0 else 0
                self.writer.add_scalar(f"Val/Type_Accuracy_{t}", acc_t, epoch)
        return total_log_like, total_acc / num_tokens, (total_event_ll, total_non_event_ll), \
               num_tokens, num_events, all_logs, all_logs_token, \
               all_type_ll_token, all_time_ll_token

    def create_thinningsampler(self, num_sample, num_exp):
        self.thinning_sampler = EventSampler(num_sample, num_exp)


    def run_prediction(self, model:XFMRNHPFast, dataLoader):
        self.thinning_sampler.cuda()
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
                    _event_prefix, _time_prefix = _event_seq[:j + 1].unsqueeze(0).cuda(), _time_seq[:j + 1].unsqueeze(0).cuda()
                    accepted_times, weights = thinning_sampler.draw_next_time(
                        [[_event_prefix, _time_prefix],
                        time_last_event, boundary, model]
                    )
                    time_uncond = float(torch.sum(accepted_times * weights))
                    dtime_uncond = time_uncond - time_last_event
                    intensities_at_times = model.compute_intensities_at_sampled_times(
                        _event_prefix, _time_prefix,
                        _time_seq[j + 1].reshape(1, 1).cuda()
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

    

