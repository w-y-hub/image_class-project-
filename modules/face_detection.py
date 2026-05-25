"""
人脸检测模块

使用OpenCV的Haar Cascade分类器进行人脸检测。
"""

import cv2
import numpy as np


def load_face_detector() -> cv2.CascadeClassifier:
    """
    加载人脸检测级联分类器。

    使用OpenCV内置的Haar特征人脸检测器。
    """
    # 获取OpenCV数据目录中的人脸检测器路径
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    # 创建级联分类器对象
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        raise RuntimeError("无法加载人脸检测级联分类器，请检查 OpenCV 安装")
    return face_cascade


def detect_faces(image: np.ndarray, scale_factor: float = 1.1, min_neighbors: int = 5) -> np.ndarray:
    """
    检测图像中的人脸。

    返回人脸矩形框数组，每个元素为(x, y, w, h)。
    """
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 加载人脸检测器
    face_cascade = load_face_detector()
    # 进行人脸检测
    faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbors)
    return faces


def draw_faces(image: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """
    在图像上绘制人脸检测框。

    用于调试和显示检测结果。
    """
    # 复制图像避免修改原图
    result = image.copy()
    # 遍历每个人脸矩形框
    for (x, y, w, h) in faces:
        # 绘制绿色矩形框
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return result
