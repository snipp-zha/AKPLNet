# model settings
model = dict(
    type='D2Det',
    pretrained='torchvision://resnet101',
    backbone=dict(
        type='ResNet',
        depth=101,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        style='pytorch'),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        num_outs=5),
    # change(aabo_start)
    rpn_head=dict(
        type='AABORPNHead',
        in_channels=256,
        feat_channels=256,
        anchor_scales=[[5.2, 6.1, 3.4, 4.9, 5.8, 4.8, 14.6, 7.4, 10.3],
                       [11.0, 7.6, 11.8, 4.7, 5.7, 3.8],
                       [10.5, 11.1, 8.5, 6.7, 12.4, 4.6, 3.5],
                       [5.7, 8.5, 7.0, 11.2, 15.2, 15.5],
                       [5.0, 14.2, 14.0, 10.1, 7.8]],
        anchor_ratios=[[6.0, 0.3, 0.5, 1.6, 1.7, 2.6, 0.5, 0.5, 0.6],
                       [0.2, 2.0, 2.3, 2.8, 1.0, 0.5],
                       [0.4, 4.2, 2.2, 1.6, 2.3, 0.5, 1.1],
                       [0.3, 0.4, 0.8, 0.7, 2.9, 2.8],
                       [1.1, 1.4, 0.8, 0.7, 2.5]],
        anchor_strides=[4, 8, 16, 32, 64],
        target_means=[0.0, 0.0, 0.0, 0.0],
        target_stds=[1.0, 1.0, 1.0, 1.0],
        loss_cls=dict(
            type='CrossEntropyLoss',
            use_sigmoid=True,
            loss_weight=1.0,
        ),
        loss_bbox=dict(
            type='SmoothL1Loss',
            beta=1.0 / 9.0,
            loss_weight=1.0,
        ),
    ),
    # change(aabo_end)
    bbox_roi_extractor=dict(
        type='SingleRoIExtractor',
        roi_layer=dict(
            type='DeformRoIPoolingPack',
            out_size=7,
            sample_per_part=1,
            out_channels=256,
            no_trans=False,
            group_size=1,
            trans_std=0.1),
        out_channels=256,
        featmap_strides=[4, 8, 16, 32]),
    bbox_head=dict(
        type='SharedFCBBoxHead',
        with_reg=False,
        num_fcs=2,
        in_channels=256,
        fc_out_channels=1024,
        roi_feat_size=7,
        num_classes=7,
        target_means=[0., 0., 0., 0.],
        target_stds=[0.1, 0.1, 0.2, 0.2],
        reg_class_agnostic=False,
        loss_cls=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0)),
    reg_roi_extractor=dict(
        type='SingleRoIExtractor',
        roi_layer=dict(type='RoIAlign', out_size=14, sample_num=2),
        out_channels=256,
        featmap_strides=[4, 8, 16, 32]),
    D2Det_head=dict(
        type='D2DetHead',
        num_convs=8,
        in_channels=256,
        norm_cfg=dict(type='GN', num_groups=36),
        MASK_ON=False))
# model training and testing settings
train_cfg = dict(
    rpn=dict(
        assigner=dict(
            type='MaxIoUAssigner',
            pos_iou_thr=0.7,
            neg_iou_thr=0.3,
            min_pos_iou=0.3,
            ignore_iof_thr=-1),
        sampler=dict(
            type='RandomSampler',
            num=256,
            pos_fraction=0.5,
            neg_pos_ub=-1,
            add_gt_as_proposals=False),
        allowed_border=0,
        pos_weight=-1,
        debug=False),
    rpn_proposal=dict(
        nms_across_levels=False,
        nms_pre=2000,
        nms_post=2000,
        max_num=2000,
        nms_thr=0.7,
        min_bbox_size=0),
    rcnn=dict(
        assigner=dict(
            type='MaxIoUAssigner',
            pos_iou_thr=0.7,
            neg_iou_thr=0.3,
            min_pos_iou=0.3,
            ignore_iof_thr=-1),
        sampler=dict(
            type='RandomSampler',
            num=512,
            pos_fraction=0.25,
            neg_pos_ub=-1,
            add_gt_as_proposals=True),
        pos_radius=1,
        pos_weight=-1,
        max_num_reg=192,
        debug=False))
test_cfg = dict(
    rpn=dict(
        nms_across_levels=False,
        nms_pre=1000,
        nms_post=1000,
        max_num=1000,
        nms_thr=0.7,
        min_bbox_size=0),
    rcnn=dict(
        score_thr=0.05, nms=dict(type='nms', iou_thr=0.8), max_per_img=100))
# dataset settings
dataset_type = 'VOCDataset'
data_root = '/home/b418/wangyanshu/D2Det/data/VOCdevkit(PCB_master)/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1333, 800),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    imgs_per_gpu=2,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        ann_file=data_root + 'VOC2007/ImageSets/Main/trainval.txt',
        img_prefix=data_root + 'VOC2007/',
        pipeline=train_pipeline),

    val=dict(
        type=dataset_type,
        ann_file=data_root + 'VOC2007/ImageSets/Main/test.txt',
        img_prefix=data_root + 'VOC2007/',
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        ann_file=data_root + 'VOC2007/ImageSets/Main/test.txt',
        img_prefix=data_root + 'VOC2007/',
        pipeline=test_pipeline))
evaluation = dict(interval=1, metric='mAP')
# optimizer
optimizer = dict(type='SGD', lr=0.0025, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=1000,
    warmup_ratio=1.0 / 80,
    step=[27, 29])
checkpoint_config = dict(interval=1)
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 30
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = './work_dirs/PCB_AT_GL_R50'
load_from = None
resume_from = None
workflow = [('train', 1)]
