import cv2
import numpy as np



def beautify_face_roi(image: np.ndarray, faces: np.ndarray,
                      smooth_strength: int = 15, brightness: int = 20) -> np.ndarray:
    """
    人脸区域美化：
    - 肤色掩膜（YCbCr）定位皮肤区域
    - 中值滤波平滑皮肤，保留五官边缘
    - YCrCb 空间调整亮度
    - 仅对肤色区域应用磨皮+提亮，非肤色区保持原图
    """
    result = image.copy()
    smooth_strength = max(1, smooth_strength)
    brightness = max(-100, min(100, brightness))

    for (x, y, w, h) in faces:
        x2 = x + w
        y2 = y + h
        face_roi = result[y:y2, x:x2]

        if face_roi.size == 0 or w < 30 or h < 30:   # 安全保护：过小区域跳过
            continue

        # ---------- 1. 肤色掩膜（YCbCr 空间）----------
        ycrcb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2YCrCb)
        # 常见亚洲肤色范围，可微调
        skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]),
                                np.array([255, 173, 127]))
        # 形态学去噪 + 柔化边缘
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        skin_mask = cv2.GaussianBlur(skin_mask, (5, 5), 0)

        # ---------- 2. 中值滤波磨皮 ----------
        # 中值滤波用邻域中位数代替中心像素，去噪同时保留边缘
        ksize = max(3, smooth_strength // 2 * 2 + 1)    # 确保奇数、最小 3
        smoothed = cv2.medianBlur(face_roi, ksize)

        # ---------- 3. 亮度调整（仅在肤色区）----------
        # 转到 YCrCb，调整亮度通道
        yuv = cv2.cvtColor(smoothed, cv2.COLOR_BGR2YCrCb)
        y_ch = yuv[:, :, 0].astype(np.int16)
        y_ch = np.clip(y_ch + brightness, 0, 255).astype(np.uint8)
        yuv[:, :, 0] = y_ch
        smoothed_bright = cv2.cvtColor(yuv, cv2.COLOR_YCrCb2BGR)

        # ---------- 4. 按掩膜混合：肤色区用磨皮+提亮，非肤色区保留原图 ----------
        skin_mask_3ch = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2BGR) / 255.0
        beauty_face = (smoothed_bright * skin_mask_3ch +
                       face_roi * (1 - skin_mask_3ch)).astype(np.uint8)

        result[y:y2, x:x2] = beauty_face

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
