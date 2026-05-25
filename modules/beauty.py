import cv2
import numpy as np


def beautify_face_roi(image: np.ndarray, faces: np.ndarray, smooth_strength: int = 15, brightness: int = 20) -> np.ndarray:
    """
    人脸区域美化：对检测到的人脸区域进行磨皮和亮度调整。
    参数：
        image: 输入图像
        faces: 人脸矩形框数组 (x, y, w, h)
        smooth_strength: 磨皮强度，默认15
        brightness: 亮度调整值，默认20
    返回：
        美化后的图像
    """
    result = image.copy()
    smooth_strength = max(1, smooth_strength)
    brightness = max(-100, min(100, brightness))

    for (x, y, w, h) in faces:
        # 计算人脸区域坐标
        x2 = x + w
        y2 = y + h
        # 提取人脸ROI
        face_roi = result[y:y2, x:x2]

        if face_roi.size == 0:
            continue

        # 双边滤波磨皮
        smooth = cv2.bilateralFilter(face_roi, d=9, sigmaColor=smooth_strength * 2, sigmaSpace=smooth_strength)

        # 亮度调整：转换到YCrCb空间调整亮度通道
        yuv = cv2.cvtColor(smooth, cv2.COLOR_BGR2YCrCb)
        y_channel = yuv[:, :, 0].astype(np.int16)
        y_channel = np.clip(y_channel + brightness, 0, 255).astype(np.uint8)
        yuv[:, :, 0] = y_channel
        smooth = cv2.cvtColor(yuv, cv2.COLOR_YCrCb2BGR)

        # 混合原图和磨皮结果
        smooth = cv2.addWeighted(face_roi, 0.4, smooth, 0.6, 0)
        result[y:y2, x:x2] = smooth

    return result


def skin_softening(image: np.ndarray, faces: np.ndarray, softness: float = 0.5) -> np.ndarray:
    """
    肤色柔和调整：对人脸区域进行肤色柔和处理。
    参数：
        image: 输入图像
        faces: 人脸矩形框
        softness: 柔和程度 (0-1)，默认0.5
    返回：
        处理后的图像
    """
    result = image.copy()
    softness = max(0.0, min(1.0, softness))

    for (x, y, w, h) in faces:
        x2 = x + w
        y2 = y + h
        face_roi = result[y:y2, x:x2]

        if face_roi.size == 0:
            continue

        # 转换到HSV空间调整饱和度
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1].astype(np.float32)
        s = s * (1 - softness) + np.mean(s) * softness
        s = np.clip(s, 0, 255).astype(np.uint8)
        hsv[:, :, 1] = s
        softened = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # 混合原图和柔和结果
        result[y:y2, x:x2] = cv2.addWeighted(face_roi, 1 - softness, softened, softness, 0)

    return result


def global_contrast_enhancement(image: np.ndarray, alpha: float = 1.2, beta: int = 10) -> np.ndarray:
    """
    全图对比度增强：调整对比度和亮度。
    参数：
        image: 输入图像
        alpha: 对比度系数，默认1.2
        beta: 亮度偏移，默认10
    返回：
        处理后的图像
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def eye_enhancement(image: np.ndarray, faces: np.ndarray, enhancement: float = 0.3) -> np.ndarray:
    """
    简单眼部增强：对眼睛区域进行亮度提升（可选扩展）。
    参数：
        image: 输入图像
        faces: 人脸矩形框
        enhancement: 增强强度，默认0.3
    返回：
        处理后的图像
    """
    result = image.copy()
    enhancement = max(0.0, min(1.0, enhancement))

    for (x, y, w, h) in faces:
        # 简单估计眼睛位置（上半部分中间）
        eye_y1 = y + int(h * 0.2)
        eye_y2 = y + int(h * 0.5)
        eye_x1 = x + int(w * 0.2)
        eye_x2 = x + int(w * 0.8)

        eye_roi = result[eye_y1:eye_y2, eye_x1:eye_x2]
        if eye_roi.size == 0:
            continue

        # 亮度提升
        yuv = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2YCrCb)
        y_channel = yuv[:, :, 0].astype(np.int16)
        y_channel = np.clip(y_channel + int(enhancement * 50), 0, 255).astype(np.uint8)
        yuv[:, :, 0] = y_channel
        enhanced = cv2.cvtColor(yuv, cv2.COLOR_YCrCb2BGR)

        result[eye_y1:eye_y2, eye_x1:eye_x2] = cv2.addWeighted(eye_roi, 1 - enhancement, enhanced, enhancement, 0)

    return result
