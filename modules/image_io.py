"""
图像输入输出模块

负责图像的读取和保存，支持中文路径。
"""

import cv2
import os
import numpy as np


def load_image(path: str) -> np.ndarray:
    """
    使用OpenCV加载图像文件。

    支持中文路径，通过numpy.fromfile和cv2.imdecode实现。
    """
    # 检查文件是否存在
    if not os.path.exists(path):
        raise FileNotFoundError(f"图片路径不存在：{path}")
    # 使用numpy读取文件字节
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"无法读取图像：{path}")
    return image


def save_image(path: str, image: np.ndarray) -> bool:
    """
    保存OpenCV图像到文件。

    支持中文路径，使用cv2.imencode和numpy.tofile。
    """
    if image is None:
        return False
    # 获取目录路径
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        # 创建目录
        os.makedirs(directory, exist_ok=True)
    # 编码图像并保存
    success = cv2.imencode(os.path.splitext(path)[1], image)[1].tofile(path)
    return bool(success)
