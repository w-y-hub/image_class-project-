# 人脸美化系统（Python）

这是一个基于python的“人脸美化系统”项目，完整实现了课程设计题目中的所有项目一功能。

## 项目目标

根据《图像识别实践》课程设计题目，实现一个基于Python的人脸美化系统，综合使用图像处理与模式识别相关知识。

## 功能特性

### 基础界面功能
- ✅ 加载本地图片（支持jpg、png、bmp等格式）
- ✅ 显示原图和处理后图像
- ✅ 保存处理结果到本地
- ✅ 重置图像到原始状态

### 图像处理功能（不少于3个）
- ✅ **去噪滤波**：
  - 均值滤波：用邻域平均值平滑图像
  - 高斯滤波：高斯加权平滑，保留边缘更好
  - 中值滤波：用中值去除椒盐噪声
  - 双边滤波：保持边缘的平滑滤波，适合磨皮

- ✅ **图像增强**：
  - 直方图均衡化：拉伸灰度范围，增强对比度
  - CLAHE（对比度受限自适应直方图均衡化）：局部增强，避免过度增强

- ✅ **图像锐化**：
  - 拉普拉斯锐化：使用二阶导数增强边缘
  - Unsharp Mask锐化：通过模糊增强细节

- ✅ **边缘检测**：
  - Sobel算子：计算梯度幅值检测边缘
  - Canny算法：多阶段高质量边缘检测

- ✅ **形态学操作**：
  - 腐蚀：缩小前景区域，去除小噪声
  - 膨胀：扩大前景区域，填充小孔
  - 开运算：腐蚀+膨胀，去除噪声
  - 闭运算：膨胀+腐蚀，填充孔洞

- ✅ **人脸检测**：
  - Haar Cascade分类器：检测人脸位置
  - 实时绘制检测框用于调试

### 美化相关功能
- ✅ 人脸区域磨皮：双边滤波+亮度调整
- ✅ 人脸区域亮度提升：YCrCb空间调整亮度
- ✅ 肤色柔和调整：HSV空间调整饱和度
- ✅ 全图对比度增强：线性变换调整对比度和亮度
- ✅ 眼部增强（扩展）：眼睛区域亮度提升

### 妆造迁移（BeautyGAN）功能
- 新增“妆造迁移(BeautyGAN)”单选按钮，支持无妆图片+妆容图片一键迁移。
- 选择妆造迁移后，需弹窗选择妆容图片，自动调用BeautyGAN模型推理，结果直接显示。
- 支持多种图片格式，推理失败有错误提示。

#### 依赖
- TensorFlow 1.x（兼容模式）
- 预训练模型已集成于modules/modelBeautyGAN/

#### 使用方法
1. 加载无妆图片
2. 选择“妆造迁移(BeautyGAN)”
3. 弹窗选择妆容图片，自动完成迁移
4. 结果可保存

## 技术栈

- **编程语言**：Python 3.10+
- **图像处理库**：OpenCV 4.x
- **数值计算**：NumPy
- **图像格式转换**：Pillow (PIL)
- **图形界面**：tkinter (Python内置)
- **人脸检测**：OpenCV Haar Cascade

## 项目结构

```
image_class（project）/
│
├─ main.py                    # 程序入口
├─ README.md                  # 项目说明文档
├─ requirements.txt           # 依赖包列表
│
├─ modules/                   # 功能模块
│   ├─ gui.py                 # 图形界面模块
│   ├─ image_io.py            # 图像读写模块
│   ├─ filters.py             # 基础图像处理模块
│   ├─ face_detection.py      # 人脸检测模块
│   ├─ beauty.py              # 人脸美化模块
│   └─ utils.py               # 工具函数模块
│
├─ resources/                 # 资源文件目录
└─ docs/                      # 文档目录
    └─ project_architecture.md # 项目架构说明
```

## 安装与运行

### 1. 环境要求
- Python 3.10 或 3.11
- Windows 10/11 或其他操作系统

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python main.py
```

### 4. 使用说明
1. 点击"加载图片"选择一张人脸图像
2. 左侧显示原图，右侧显示处理结果
3. 选择不同的处理功能（单选按钮）
4. 调整参数滑块（模糊强度、亮度等）
5. 点击"执行处理"查看效果
6. 点击"保存结果"保存处理后的图像
7. 点击"重置图像"回到原始状态

## 模块详细说明

### main.py
```python
from modules.gui import run_app

if __name__ == "__main__":
    run_app()  # 启动图形界面应用程序
```

### modules/gui.py
负责创建图形界面，包含：
- 主窗口布局（控制面板 + 显示面板）
- 按钮事件处理（加载、保存、重置、处理）
- 参数调节控件（滑块）
- 图像显示更新

### modules/image_io.py
处理图像的输入输出：
- `load_image(path)`: 加载图像，支持中文路径
- `save_image(path, image)`: 保存图像，支持中文路径

### modules/filters.py
实现各种图像处理算法：
- 滤波函数：均值、高斯、中值、双边
- 增强函数：直方图均衡化、CLAHE
- 锐化函数：拉普拉斯、Unsharp Mask
- 检测函数：Sobel、Canny
- 形态学函数：腐蚀、膨胀、开闭运算

### modules/face_detection.py
人脸检测功能：
- `load_face_detector()`: 加载Haar Cascade分类器
- `detect_faces(image)`: 检测图像中的人脸
- `draw_faces(image, faces)`: 绘制检测框

### modules/beauty.py
人脸美化功能：
- `beautify_face_roi()`: 人脸区域磨皮和亮度调整
- `skin_softening()`: 肤色柔和处理
- `global_contrast_enhancement()`: 全图对比度增强
- `eye_enhancement()`: 眼部增强

### modules/utils.py
工具函数：
- `cv2_to_pil()`: OpenCV图像转PIL格式
- `pil_to_cv2()`: PIL图像转OpenCV格式
- `resize_for_display()`: 缩放图像适应显示
- `clamp()`: 值范围限制


## 课程要求对应

| 课程要求 | 实现情况 |
|---------|---------|
| 图像基础处理方法 | ✅ 滤波、增强、锐化 |
| 边缘检测与形态学处理 | ✅ Sobel/Canny、腐蚀/膨胀/开闭运算 |
| 人脸检测与关键点定位 | ✅ Haar Cascade人脸检测 |
| 图像局部处理（ROI） | ✅ 人脸区域磨皮和增强 |
| Python图像处理工具使用 | ✅ OpenCV、NumPy、Pillow、tkinter |
| 简单神经网络应用 | 可作为扩展方向提及 |


## 扩展方向

1. **算法改进**：
   - 使用DNN人脸检测器（更准确）
   - 添加关键点检测（眼睛、鼻子、嘴巴）
   - 实现更高级的美颜算法

2. **功能扩展**：
   - 批量处理多张图片
   - 添加滤镜效果
   - 支持视频处理

3. **界面优化**：
   - 使用更现代的GUI框架（如PyQt）
   - 添加实时预览
   - 支持拖拽加载图片

## 参考资料

- OpenCV官方文档：https://docs.opencv.org/
- Python图像处理教程：https://www.geeksforgeeks.org/python-opencv/
- tkinter GUI教程：https://docs.python.org/3/library/tkinter.html

---

