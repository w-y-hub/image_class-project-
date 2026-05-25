import cv2
import numpy as np


def mean_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    均值滤波：用邻域像素的平均值替换中心像素，实现图像平滑去噪。
    参数：
        image: 输入图像 (OpenCV BGR格式)
        kernel_size: 滤波核大小，必须为奇数，默认5
    返回：
        处理后的图像
    """
    # 确保kernel_size为奇数
    kernel_size = max(1, kernel_size // 2 * 2 + 1)
    # 使用cv2.blur进行均值滤波
    return cv2.blur(image, (kernel_size, kernel_size))


def gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    高斯滤波：使用高斯核进行加权平均，实现平滑去噪，保留边缘更好。
    参数：
        image: 输入图像
        kernel_size: 高斯核大小，默认5
    返回：
        处理后的图像
    """
    kernel_size = max(1, kernel_size // 2 * 2 + 1)
    # sigma=0表示自动计算标准差
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    中值滤波：用邻域像素的中值替换中心像素，擅长去除椒盐噪声。
    参数：
        image: 输入图像
        kernel_size: 滤波核大小，默认5
    返回：
        处理后的图像
    """
    kernel_size = max(1, kernel_size // 2 * 2 + 1)
    return cv2.medianBlur(image, kernel_size)


def bilateral_filter(image: np.ndarray, d: int = 9, sigma_color: int = 75, sigma_space: int = 75) -> np.ndarray:
    """
    双边滤波：保持边缘的同时进行平滑，适合磨皮。
    参数：
        image: 输入图像
        d: 滤波直径
        sigma_color: 颜色空间标准差
        sigma_space: 坐标空间标准差
    返回：
        处理后的图像
    """
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    直方图均衡化：增强图像对比度，拉伸灰度范围。
    参数：
        image: 输入图像
    返回：
        处理后的图像
    """
    if len(image.shape) == 3:
        # 彩色图像：转换到YCrCb空间，只对亮度通道均衡化
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    else:
        # 灰度图像：直接均衡化
        return cv2.equalizeHist(image)


def clahe_equalization(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    """
    CLAHE（对比度受限自适应直方图均衡化）：局部增强，避免过度增强。
    参数：
        image: 输入图像
        clip_limit: 对比度限制，默认2.0
        tile_grid_size: 网格大小，默认(8,8)
    返回：
        处理后的图像
    """
    if len(image.shape) == 3:
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        ycrcb[:, :, 0] = clahe.apply(ycrcb[:, :, 0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    else:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)


def laplacian_sharpen(image: np.ndarray) -> np.ndarray:
    """
    拉普拉斯锐化：使用拉普拉斯算子增强边缘。
    参数：
        image: 输入图像
    返回：
        处理后的图像
    """
    # 转换为灰度
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用拉普拉斯算子
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    # 转换为绝对值并归一化
    lap = cv2.convertScaleAbs(lap)
    # 锐化：原图 + 拉普拉斯边缘
    sharpened = cv2.addWeighted(gray, 1.0, lap, 1.0, 0)
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)


def unsharp_mask_sharpen(image: np.ndarray, sigma: float = 1.0, strength: float = 1.5) -> np.ndarray:
    """
    卷积核锐化（Unsharp Mask）：通过高斯模糊增强细节。
    参数：
        image: 输入图像
        sigma: 高斯模糊的标准差
        strength: 锐化强度
    返回：
        处理后的图像
    """
    # 高斯模糊
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    # 计算细节层
    detail = cv2.subtract(image, blurred)
    # 增强细节
    sharpened = cv2.addWeighted(image, 1.0 + strength, detail, strength, 0)
    return sharpened


def sobel_filter(image: np.ndarray) -> np.ndarray:
    """
    Sobel边缘检测：计算梯度幅值，检测边缘。
    参数：
        image: 输入图像
    返回：
        边缘图像（BGR格式）
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 计算x和y方向梯度
    dx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    dy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    # 计算梯度幅值
    mag = cv2.magnitude(dx, dy)
    # 归一化到0-255
    normalized = cv2.convertScaleAbs(mag)
    return cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)


def canny_edge(image: np.ndarray, threshold1: int = 100, threshold2: int = 200) -> np.ndarray:
    """
    Canny边缘检测：多阶段算法，检测高质量边缘。
    参数：
        image: 输入图像
        threshold1: 低阈值
        threshold2: 高阈值
    返回：
        边缘图像（BGR格式）
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1, threshold2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def erode(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    腐蚀：缩小前景区域，消除小噪声。
    参数：
        image: 输入图像
        kernel_size: 结构元素大小
    返回：
        处理后的图像
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


def dilate(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    膨胀：扩大前景区域，填充小孔。
    参数：
        image: 输入图像
        kernel_size: 结构元素大小
    返回：
        处理后的图像
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def opening(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    开运算：先腐蚀后膨胀，去除小噪声。
    参数：
        image: 输入图像
        kernel_size: 结构元素大小
    返回：
        处理后的图像
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def closing(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    闭运算：先膨胀后腐蚀，填充小孔。
    参数：
        image: 输入图像
        kernel_size: 结构元素大小
    返回：
        处理后的图像
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
