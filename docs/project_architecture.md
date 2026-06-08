# 人脸美化系统项目架构详细说明

## 项目概述

本项目是一个完整的"人脸美化系统"，采用模块化设计，便于初学者理解和维护。每个模块职责清晰，代码注释详细。

## 架构设计原则

1. **模块化**：功能分离，每个模块负责特定任务
2. **松耦合**：GUI 不直接调用算法，通过 services 调度层路由
3. **可扩展性**：新增功能只需在 services.py 加一个 elif 分支
4. **易用性**：对初学者友好，注释详细
5. **健壮性**：包含错误处理和边界检查

## 模块职责分工

### 1. main.py - 程序入口
**职责**：启动应用程序
**代码逻辑**：
```python
import locale, os
locale.setlocale(locale.LC_ALL, "C.utf8")    # UTF-8支持
os.environ.setdefault("LANG", "C.utf8")      # 中文不乱码

from modules.gui import run_app

if __name__ == "__main__":
    run_app()
```

### 2. modules/gui.py - 图形界面模块
**职责**：创建用户界面，处理用户交互
**主要组件**：
- `FaceBeautyApp` 类：主应用程序类
- 左侧可滚动控制面板：按钮、单选钮、模板设置、动态参数
- 右侧显示面板：原图和结果图双栏展示 + 底部状态栏与进度条

**关键方法**：
- `__init__()`: 初始化界面和变量
- `_build_ui()`: 构建界面布局
- `load_image()`: 加载图片文件
- `save_image()`: 保存处理结果
- `apply_operation()`: 执行选择的处理操作，含状态反馈
- `_update_display()`: 更新图像显示
- `_set_status()`: 更新底部状态栏文字及进度条显隐
- `_on_operation_changed()`: 操作切换时动态显示/隐藏参数

**技术特点**：
- 所有中文文字通过 `text_renderer.py` 渲染为图片显示，彻底解决 Linux 中文乱码
- 参数区根据所选操作动态显隐，标签文字随操作变化

### 3. modules/text_renderer.py - 中文文字渲染引擎
**职责**：将中文文字通过 Pillow + 项目自带字体渲染为图片
**关键函数**：
- `render_photo()`: 文字 → RGBA图片 → PhotoImage
- `make_label()`: 创建图片化文字标签
- `make_button()`: 创建带 hover 高亮的图片化按钮
- `make_radio()`: 创建带 ●/○ 选中态的图片化单选钮
- `make_option_menu()`: 创建带弹出列表的图片化下拉菜单
- `make_label_frame()`: 创建带渲染标题的分组框

**技术细节**：
- 使用 `ImageFont.truetype()` 加载 `assets/fonts/NotoSansSC.ttf`
- 内置渲染缓存，避免重复绘制

### 4. modules/services.py - 统一调度层
**职责**：接收 GUI 发来的操作指令，路由到对应的算法模块

**关键函数**：
- `apply_operation()`: 根据 operation 参数路由到不同算法，统一传递全部参数

**设计特点**：
- 界面与算法解耦，GUI 不直接调用 filters/beauty 等模块
- BeautyGAN 采用懒加载，只在需要时才 `from modules import beautygan`
- 支持中英文操作名别名映射

### 5. modules/image_io.py - 图像输入输出
**职责**：处理图像文件的读取和保存
**关键函数**：
- `load_image(path)`: 使用OpenCV加载图像，支持中文路径
- `save_image(path, image)`: 保存图像到文件，支持中文路径

**技术细节**：
- 使用 `np.fromfile()` 和 `cv2.imdecode()` 解决中文路径问题
- 使用 `cv2.imencode()` 和 `tofile()` 保存图像

### 6. modules/utils.py - 工具函数
**职责**：提供通用的图像处理辅助函数
**关键函数**：
- `cv2_to_pil()`: OpenCV BGR转PIL RGB
- `pil_to_cv2()`: PIL RGB转OpenCV BGR
- `resize_for_display()`: 缩放图像适应GUI显示
- `clamp()`: 值范围限制

### 7. modules/filters.py - 基础图像处理
**职责**：实现各种图像处理算法
**算法分类**：

#### 滤波函数
- `mean_blur()`: 均值滤波，简单平滑
- `gaussian_blur()`: 高斯滤波，加权平滑
- `median_blur()`: 中值滤波，去除椒盐噪声
- `bilateral_filter()`: 双边滤波，保持边缘平滑

#### 增强函数
- `histogram_equalization()`: 全局直方图均衡化
- `clahe_equalization()`: 自适应直方图均衡化（clip_limit 可调）

#### 锐化函数
- `laplacian_sharpen()`: 拉普拉斯锐化
- `unsharp_mask_sharpen()`: Unsharp Mask锐化

#### 检测函数
- `sobel_filter()`: Sobel边缘检测
- `canny_edge()`: Canny边缘检测（双阈值可调）

#### 形态学函数
- `erode()`: 腐蚀操作
- `dilate()`: 膨胀操作
- `opening()`: 开运算
- `closing()`: 闭运算

### 8. modules/face_detection.py - 人脸检测
**职责**：检测图像中的人脸位置
**技术**：OpenCV Haar Cascade分类器
**关键函数**：
- `load_face_detector()`: 加载预训练分类器
- `detect_faces()`: 执行人脸检测
- `draw_faces()`: 绘制检测框用于调试

### 9. modules/beauty.py - 人脸美化
**职责**：对人脸区域进行美化处理
**关键函数**：
- `beautify_face_roi()`: 人脸磨皮（双边滤波）和亮度调整（YCrCb空间）
- `skin_softening()`: 肤色柔和（HSV饱和度调整）
- `global_contrast_enhancement()`: 全图对比度增强
- `eye_enhancement()`: 眼部亮度提升

### 10. modules/beautygan.py - 妆造迁移（BeautyGAN）
**职责**：实现无妆人脸与妆容图片的妆造迁移
**关键函数**：
- `beautygan_transfer(no_makeup_img, makeup_img)`: 输入无妆图+妆容参考图，输出迁移后图片

**注意**：TensorFlow 在此模块首次导入时加载。services.py 采用懒加载策略，仅当用户选择 BeautyGAN 时才触发此模块的导入。

### 11. modules/template_manager.py - 妆造模板管理
**职责**：加载和管理妆造模板配置
**关键函数**：
- `load_templates()`: 从 `assets/makeup_templates/templates.json` 读取模板列表，验证图片文件存在

## 数据流向

```
用户操作 → gui.py 接收命令 → services.py 路由
    ↓
image_io 加载图片 → filters/beauty 处理 → 结果返回 GUI
    ↓
GUI 更新显示 → 状态栏更新
```

## 项目文件结构

```
├─ main.py                     # 程序入口
├─ modules/
│   ├─ gui.py                  # 图形界面
│   ├─ text_renderer.py        # 中文文字→图片渲染
│   ├─ services.py             # 调度层
│   ├─ filters.py              # 7类21种图像处理
│   ├─ face_detection.py       # 人脸检测
│   ├─ beauty.py               # 人脸美化
│   ├─ beautygan.py            # 妆造迁移（TF懒加载）
│   ├─ image_io.py             # 图像读写
│   ├─ utils.py                # 工具函数
│   └─ template_manager.py     # 模板加载
├─ assets/
│   ├─ fonts/                  # 中文字体
│   └─ makeup_templates/       # 妆造模板
├─ docs/                       # 文档
└─ pyproject.toml              # 配置
```

## 错误处理机制

- 文件不存在：抛出 `FileNotFoundError`
- 图像读取失败：抛出 `ValueError`
- 人脸检测器加载失败：抛出 `RuntimeError`
- 模板图片缺失：跳过并在控制台打印警告
- GUI操作异常：显示错误对话框

## 扩展性设计

### 添加新滤波算法
1. 在 `filters.py` 中添加新函数
2. 在 `services.py` 中添加 elif 分支
3. 在 `gui.py` 的操作列表中添加条目
4. 如有新增参数，在 `_param_map` 中注册

### 添加新美化功能
1. 在 `beauty.py` 中添加新函数
2. 在 `services.py` 中添加路由
3. 在 GUI 中添加控件

### 更换人脸检测算法
1. 修改 `face_detection.py` 中的检测函数
2. 保持接口一致（返回 faces 数组）

## 性能优化

1. **TensorFlow 懒加载**：仅在 BeautyGAN 使用时导入，其余操作即时响应
2. **图像缩放显示**：GUI 显示时缩小图像尺寸到 450×550 以内
3. **渲染缓存**：text_renderer 缓存已渲染的文字图片，避免重复绘制
4. **灰度预处理**：人脸检测前将彩色图转为灰度图，提速 3 倍
