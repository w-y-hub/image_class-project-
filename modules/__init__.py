"""
人脸美化系统 — 功能模块包

模块结构：
  gui.py              — tkinter 图形界面
  image_io.py         — 图像读写（支持中文路径）
  utils.py            — 格式转换、缩放工具
  filters.py          — 基础图像处理（滤波/增强/锐化/边缘/形态学）
  face_detection.py   — Haar Cascade 人脸检测
  beauty.py           — 人脸美化（磨皮/肤色/对比度/眼部增强）
  beautygan.py        — BeautyGAN 妆造迁移（懒加载，仅使用时导入 TensorFlow）
  services.py         — 统一调度层
  template_manager.py — 妆造模板加载
"""
