"""
General utilities
"""
import os
import torch
import numpy as np
from os.path import join, exists


def print_header(stdout, style=None):
    if style is None:
        print("-" * len(stdout))
        print(stdout)
        print("-" * len(stdout))
    elif style == "bottom":
        print(stdout)
        print("-" * len(stdout))
    elif style == "top":
        print("-" * len(stdout))
        print(stdout)


def set_seed(seed):
    """Sets seed"""
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def init_experiment(args):
    """Initialize experiment name and set seed"""
    model_params = f'me={args.max_epoch}-bst={args.bs_trn}-o={args.optim}-lr={args.lr}-mo={args.momentum}-wd={args.weight_decay}-vs={args.val_split}'
    model_params_s = f'spur-me={args.max_epoch_s}-bst={args.bs_trn_s}-lr={args.lr_s}-mo={args.momentum_s}-wd={args.weight_decay_s}-sts={args.spurious_train_split}'
    if args.subsample_labels is True:
        sample = '-sub_l'
    elif args.supersample_labels is True:
        sample = '-sup_l'
    elif args.subsample_groups is True:
        sample = '-sub_g'
    else:
        sample = ''
        
    if args.weigh_slice_samples_by_loss:
        sample += f'-wsbl-lf={args.loss_factor}'
        
    if args.resample_class != '':
        if args.resample_class == 'upsample':
            sample += '-rsc=u'
        elif args.resample_class == 'subsample':
            sample += '-rsc=s'

    flipped = '-flip' if args.flipped is True else ''
    test_cmap = ''
    if args.test_cmap != '':
        args.test_shift = 'generalize'
        test_cmap = f'-tcmap={args.test_cmap}'
    arch = args.arch if args.arch != 'mlp' else f'mlp_hd={args.hidden_dim}'
    
    if args.dataset in ['waterbirds', 'waterbirds_r', 'cxr', 'multinli']:  # 'celebA'
        experiment_configs = f'config-tn={args.target_name}-cn={args.confounder_names}'
    elif args.dataset == 'colored_mnist':
        if args.p_corr_by_class is None:
            p_corr_arg = args.p_correlation
        else:
            p_corr_arg = '_'.join([str(pcc[0]) for pcc in args.train_class_ratios])
            
        train_classes_arg = '_'.join([str(tc) for tc in args.train_classes])
        experiment_configs = f'config-p={p_corr_arg}-cmap={args.data_cmap}-test={args.test_shift}{test_cmap}{flipped}-tr_c={train_classes_arg}'
        
        if args.train_class_ratios is not None:
            tcr = '_'.join([str(tcr[0]) for tcr in args.train_class_ratios])
            experiment_configs += f'-tr_cr={tcr}'
    else:
        experiment_configs = f'config'
    args.experiment_configs = experiment_configs
    
    # Clean this up here
    try:
        if args.mode == 'train_spurious':
            model_params = model_params_s
    except:
        pass
    args.experiment_name = f'a={arch}-d={args.dataset}-tm={args.train_method}{sample}-{model_params}-{model_params_s}-s={args.seed}-r={args.replicate}'
#     args.experiment_name = f'a={arch}-d={args.dataset}-tm={args.train_method}{sample}-{experiment_configs[7:]}-{model_params}-s={args.seed}'  # {model_params_s} Taken out for now - remember what these are though
    set_seed(args.seed)

    # Update saving paths
    new_model_path = join(args.model_path, args.dataset)
    new_image_path = join(args.image_path, args.dataset)
    new_log_path = join(args.log_path, args.dataset)
    new_results_path = join(args.results_path, args.dataset)
    if not exists(new_model_path):
        os.makedirs(new_model_path)
        os.makedirs(new_image_path)
        os.makedirs(new_log_path)
        os.makedirs(new_results_path)
    # Make more granular - save specific folders per experiment configs
    new_model_path = join(new_model_path, experiment_configs)
    new_image_path = join(new_image_path, experiment_configs)
    new_log_path = join(new_log_path, experiment_configs)
    new_results_path = join(new_results_path, experiment_configs)
    if not exists(new_model_path):
        os.makedirs(new_model_path)
        os.makedirs(new_image_path)
        os.makedirs(new_log_path)
        os.makedirs(new_results_path)
    args.model_path = new_model_path
    args.image_path = new_image_path
    args.log_path = new_log_path
    args.results_path = new_results_path
    
    
def update_contrastive_experiment_name(args):
    print(f'Old experiment name: {args.experiment_name}')
    args.experiment_name = f'a={args.arch}-d={args.dataset}-tm={args.train_method}'  #'-{args.experiment_configs[7:]}'
    slice_with = args.slice_with[0] + args.slice_with.split('_')[-1][0] + args.rep_cluster_method[:2]
    args.experiment_name += f'-sw={slice_with}'
    if args.no_projection_head:
        args.experiment_name += '-nph'
    else:
        args.experiment_name += f'-pd{args.projection_dim}'
    args.experiment_name += f'-np={args.num_positive}-nn={args.num_negative}-bf={args.batch_factor}'
    if args.hard_negative_factor > 0:
        args.experiment_name += f'-hnf={args.hard_negative_factor}'
    if args.weight_pos_by_loss is True:
        args.experiment_name += f'-wpl={args.weight_pos_by_loss}-plt={args.pos_loss_temp}-psp={args.prioritize_spurious_pos}'
    if args.weight_neg_by_loss is True:
        args.experiment_name += f'-wnl={args.weight_neg_by_loss}-nlt={args.neg_loss_temp}'
    args.experiment_name += f'-me={args.max_epoch}'
    if args.contrastive_type == 'contrastive':
        # args.experiment_name += f'-lt=c-t={args.temperature}-bt={args.base_temperature}'
        args.experiment_name += f'-lt=c-t={args.temperature}'
    elif args.contrastive_type == 'triplet':
        args.experiment_name += f'-lt=t-m={args.margin}'
    if args.balance_targets:
        training_params = '-bt'
    else:
        training_params = ''
    if args.resample_class == 'upsample':
        args.experiment_name += '-rsc=u'
    elif args.resample_class == 'subsample':
        args.experiment_name += '-rsc=s'
    training_params += f'-tr={args.target_sample_ratio}-o={args.optim}-lr={args.lr}-m={args.momentum}-wd={args.weight_decay}'
    if args.lr_scheduler != '':
        training_params += f'-lrs={args.lr_scheduler[:3]}'
    if args.lr_scheduler_classifier != '':
        training_params += f'-clrs={args.lr_scheduler[:3]}'
    if args.additional_negatives:
        training_params += '-an'
    if args.data_wide_pos:
        training_params += '-dwp'
    if args.supervised_contrast and 'supcon' not in args.experiment_name:
        training_params += '-sc'
    try:
        training_params += f'-ci={args.classifier_update_interval}'
    except:
        pass
    if args.full_contrastive:
        training_params += '-FC'
    if args.clip_grad_norm:
        training_params += '-cg'
    args.experiment_name += f'{training_params}-s={args.seed}-r={args.replicate}'
    args.experiment_name = args.experiment_name.replace('True', '1').replace('False', '0')
    args.experiment_name = args.experiment_name.replace('0.0001', '1e_4')
    args.experiment_name = args.experiment_name.replace('0.00001', '1e_5')
    args.experiment_name = args.experiment_name.replace('waterbird', 'wb')
    args.experiment_name = args.experiment_name.replace('celebA', 'cA')
    args.experiment_name = args.experiment_name.replace('resnet', 'rn')
    print(f'New experiment name: {args.experiment_name}')
