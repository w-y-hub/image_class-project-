"""
工具函数模块

提供图像格式转换、显示缩放等通用工具函数。
"""

import cv2
import numpy as np
from PIL import Image


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """
    将OpenCV的BGR图像转换为PIL的RGB图像。

    OpenCV使用BGR颜色顺序，而PIL使用RGB，所以需要转换。
    """
    if image is None:
        raise ValueError("cv2 image is None")
    # 转换颜色空间从BGR到RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 创建PIL图像
    return Image.fromarray(image_rgb)


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """
    将PIL的RGB图像转换为OpenCV的BGR图像。

    用于将PIL图像转换回OpenCV格式进行处理。
    """
    if image.mode != "RGB":
        # 确保图像是RGB模式
        image = image.convert("RGB")
    # 转换为numpy数组
    array = np.array(image)
    # 转换颜色空间从RGB到BGR
    return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)


def resize_for_display(image: np.ndarray, max_size=(400, 400)) -> np.ndarray:
    """
    缩放图像以适应GUI显示。

    计算缩放比例，确保图像不超过最大尺寸，同时保持宽高比。
    """
    # 获取图像尺寸
    height, width = image.shape[:2]
    max_width, max_height = max_size
    # 计算缩放比例
    scale = min(max_width / width, max_height / height, 1.0)
    # 计算新尺寸
    new_width = int(width * scale)
    new_height = int(height * scale)
    # 缩放图像
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def clamp(value: int, min_value: int, max_value: int) -> int:
    """
    将值限制在指定范围内。

    用于确保参数值不会超出有效范围。
    """
    return max(min_value, min(max_value, value))
