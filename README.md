# 人脸美化系统

基于 Python 的图像识别课程设计项目，综合运用图像处理与模式识别知识，实现一个功能完整的人脸美化系统。

## 功能总览

### 8 类 21 种图像处理功能

| 类别 | 功能 | 参数调节 |
|------|------|---------|
| **去噪滤波** | 均值滤波、高斯滤波、中值滤波、双边滤波 | ✅ 滤波核大小 |
| **图像增强** | 直方图均衡化、CLAHE（对比度限制可调） | ✅ CLAHE 参数 |
| **图像锐化** | 拉普拉斯锐化、Unsharp Mask 锐化 | ✅ 锐化强度 |
| **边缘检测** | Sobel 算子、Canny 算子（双阈值可调） | ✅ 低/高阈值 |
| **形态学操作** | 腐蚀、膨胀、开运算、闭运算 | ✅ 结构元素大小 |
| **人脸检测** | Haar Cascade 分类器 | — |
| **人脸美化** | 磨皮、肤色柔和、对比度增强、眼部增强 | ✅ 多参数可调 |
| **妆造迁移** | BeautyGAN 妆容迁移（4种内置模板 + 自定义） | 模板选择 |

### 技术亮点

- 🎨 **中文无乱码**：Pillow + 项目自带 Noto Sans SC 字体直接渲染文字为图片，完全绕过系统字体，Linux / macOS / Windows 显示一致；错误弹窗也使用自定义渲染对话框，无系统字体依赖
- ⚡ **快速启动**：TensorFlow 懒加载，仅使用 BeautyGAN 时才导入，其余操作即时响应；`TF_CPP_MIN_LOG_LEVEL=3` + `ABSL_MIN_LOG_LEVEL=3` 屏蔽 TF 日志噪音
- 🛡️ **健壮错误处理**：所有 `messagebox` 替换为 `_safe_messagebox` 自定义弹窗（Pillow 渲染中文文字）；窗口销毁后回退到控制台输出，避免二次崩溃
- 🎯 **参数动态调整**：选择不同操作时，自动显示对应的参数滑块，标签文字随操作变化
- 📊 **进度反馈**：底部状态栏 + 进度条，加载和处理过程一目了然
- 📦 **妆造模板系统**：内置 4 种妆容模板（日常淡妆/清新自然/韩系裸妆/晚宴浓妆），支持自定义模板

## 快速开始

### 环境要求

- Python 3.10 ~ 3.12
- uv（包管理器，自动管理 Python 版本）

### 安装与运行

```bash
# 1. 安装 uv（如已安装则跳过）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境并安装依赖
uv sync

# 3. 启动程序
uv run python main.py
```

> 首次启动会自动注册项目自带的 Noto Sans SC 中文字体，无需手动安装。

### 使用说明

1. 点击 **加载图片** 选择一张含人脸的图像
2. 左侧显示原图，右侧显示处理结果
3. 在 **功能选择** 区点击需要的处理功能
4. 如有参数滑块，按需调整（仅显示当前功能相关的参数）
5. 点击 **执行处理** 查看效果
6. 点击 **保存结果** 保存图像
7. 点击 **重置图像** 回到原始状态

### 妆造迁移使用

1. 加载一张无妆人脸图片
2. 选择 **妆造迁移(BeautyGAN)**
3. 选择 **使用内置模板**，从下拉菜单挑选妆容风格
4. 也可导入自定义妆容参考图
5. 点击 **执行处理**，等待 BeautyGAN 推理完成

## 项目结构

```
├─ main.py                     # 程序入口（locale 设置）
├─ modules/
│   ├─ gui.py                  # tkinter 图形界面（文字图片化渲染）
│   ├─ text_renderer.py        # 中文文字→图片渲染引擎（Pillow + TTF）
│   ├─ services.py             # 统一调度层（算法路由 + 懒加载）
│   ├─ filters.py              # 图像处理算法（滤波/增强/锐化/边缘/形态学）
│   ├─ face_detection.py       # Haar Cascade 人脸检测
│   ├─ beauty.py               # 人脸美化算法（磨皮/肤色/对比度/眼部）
│   ├─ beautygan.py            # BeautyGAN 妆造迁移（TensorFlow 懒加载）
│   ├─ image_io.py             # 图像读写（支持中文路径）
│   ├─ utils.py                # 格式转换 / 显示缩放
│   └─ template_manager.py     # 妆造模板配置加载
├─ assets/
│   ├─ fonts/                  # 项目自带中文字体 NotoSansSC
│   └─ makeup_templates/       # 4 种内置妆造模板 + 配置
├─ docs/
│   ├─ project_architecture.md # 项目架构详细说明
│   ├─ environment_setup.md    # 环境搭建指南
│   ├─ 报告.md                  # 课程设计报告
│   └─ 零基础代码解读.md        # 面向初学者的代码讲解
└─ pyproject.toml              # 项目配置与依赖声明
```

## 模块架构

```
main.py
  └─ gui.py（界面层）
       └─ text_renderer.py（文字→图片渲染）
       └─ services.py（调度层）
            ├─ filters.py        — 7类基础图像处理
            ├─ face_detection.py — 人脸检测
            ├─ beauty.py         — 人脸美化
            └─ beautygan.py      — 妆造迁移（懒加载 TensorFlow）
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 编程语言 | Python 3.11 |
| 包管理器 | uv（自动管理 Python 版本与依赖） |
| 图像处理 | OpenCV、NumPy |
| 中文渲染 | Pillow + Noto Sans SC（跨平台，无需系统字体） |
| 图形界面 | tkinter（内置） |
| 人脸检测 | OpenCV Haar Cascade |
| 妆容迁移 | TensorFlow + BeautyGAN（预训练模型） |

## 课程要求对应

| 课程要求 | 实现情况 |
|---------|:--------:|
| 图像基础处理方法（滤波、增强、锐化） | ✅ 4种滤波 + 2种增强 + 2种锐化 |
| 边缘检测与形态学处理 | ✅ Sobel/Canny + 腐蚀/膨胀/开/闭 |
| 人脸检测与关键点定位 | ✅ Haar Cascade 人脸检测 |
| 图像局部处理（ROI 操作） | ✅ 人脸区域磨皮/肤色/眼部增强 |
| Python 图像处理工具使用 | ✅ OpenCV + NumPy + Pillow + tkinter |
| 图形界面（加载/显示/保存） | ✅ 完整 GUI 交互 |
| 简单神经网络应用 | ✅ BeautyGAN 妆容迁移（TensorFlow） |

---

_课程设计项目 — 图像识别实践_
