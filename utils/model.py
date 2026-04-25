#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型操作模块

实现了AI模型加载、预处理和推理功能。
使用PyTorch框架和ResNet50预训练模型进行病虫害识别。

主要功能：
- 病虫害识别模型的定义和加载
- 图像预处理和数据增强
- 模型推理和结果解析
- 批量预测支持

模型架构：
- 基于ResNet50预训练模型
- 自定义全连接层输出类别数
- 支持增量学习和类别扩展

"""

import torch
from PIL import Image
from torchvision import transforms, models
import torch.nn as nn
from .class_names import get_class_name, load_active_class_names

# 模型配置常量
IMAGE_SIZE = (224, 224)  # 模型输入图像尺寸

# 病虫害识别模型类
class PlantDiseaseModel(nn.Module):
    """
    植物病虫害识别模型

    基于ResNet50预训练模型的自定义神经网络，
    用于识别农作物病虫害。

    模型结构：
    - ResNet50主干网络（不使用预训练权重）
    - 自定义全连接层输出指定数量的类别
    """

    def __init__(self, num_classes: int):
        """
        初始化模型

        参数：
        - num_classes: 输出类别数量，由当前激活的类别名称决定
        """
        super(PlantDiseaseModel, self).__init__()
        # 使用ResNet50作为基础模型
        self.base_model = models.resnet50(pretrained=False)
        # 获取ResNet50全连接层的输入特征数
        in_features = self.base_model.fc.in_features
        # 替换全连接层以匹配输出类别数
        self.base_model.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        """
        前向传播

        参数：
        - x: 输入张量 (batch_size, 3, 224, 224)

        返回：
        - torch.Tensor: 模型输出 logits
        """
        return self.base_model(x)

# 模型加载函数
def load_model(model_path):
    """
    加载训练好的病虫害识别模型

    从指定路径加载模型权重，并根据当前激活的类别数量
    动态调整模型结构以支持增量学习。

    参数：
    - model_path: 模型文件路径

    返回：
    - PlantDiseaseModel: 加载完成的模型（已设置为评估模式）
    """
    # 加载当前激活的类别名称以确定类别数量
    class_names = load_active_class_names()
    num_classes = len(class_names)

    # 创建模型实例
    model = PlantDiseaseModel(num_classes=num_classes)

    # 加载模型状态字典
    state = torch.load(model_path, map_location=torch.device("cpu"))

    # strict=False 允许在增量训练时权重维度不完全一致的情况
    model.load_state_dict(state, strict=False)

    # 设置为评估模式
    model.eval()

    return model

# 图像预处理函数
def preprocess_image(image):
    """
    预处理输入图像以符合模型要求

    对输入图像进行尺寸调整、标准化和张量转换，
    使其符合ResNet50模型的输入要求。

    参数：
    - image: PIL Image对象

    返回：
    - torch.Tensor: 预处理后的图像张量 (1, 3, 224, 224)
    """
    # 定义预处理变换
    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),  # 调整图像尺寸
        transforms.ToTensor(),          # 转换为张量
        # ImageNet标准化参数
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 确保图像为RGB模式
    image = image.convert('RGB')

    # 应用预处理变换
    image = transform(image)

    # 添加批次维度
    image = image.unsqueeze(0)  # (3, 224, 224) -> (1, 3, 224, 224)

    return image

# 单张图像预测函数
def predict(model, image):
    """
    对单张图像进行病虫害识别预测

    使用加载的模型对输入图像进行推理，返回预测结果。

    参数：
    - model: 加载的PlantDiseaseModel实例
    - image: PIL Image对象

    返回：
    - dict: 预测结果字典，包含：
        - 'class_id': 预测类别ID
        - 'class_name': 预测类别名称
        - 'confidence': 预测置信度
        - 'probabilities': 各类别概率分布
    """
    # 预处理图像
    image = preprocess_image(image)

    # 禁用梯度计算以提高推理效率
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = probabilities.max(1)
    return predicted.item(), confidence.item()

# 批量图像预测函数
def batch_predict(model, images):
    """
    对多张图像进行批量病虫害识别预测

    遍历输入的图像列表，对每张图像进行预测，
    返回所有图像的预测结果列表。

    参数：
    - model: 加载的PlantDiseaseModel实例
    - images: PIL Image对象列表

    返回：
    - list: 预测结果字典列表，每个字典包含：
        - 'class_id': 预测类别ID
        - 'class_name': 预测类别名称
        - 'confidence': 预测置信度
    """
    results = []
    for image in images:
        # 对每张图像进行预测
        class_id, confidence = predict(model, image)
        class_name = get_class_name(class_id)
        results.append({
            'class_id': class_id,
            'class_name': class_name,
            'confidence': confidence
        })
    return results