import os
import sys

# 确保项目根目录在 sys.path，兼容直接运行 python modules/gui.py
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk

from modules import image_io, utils, services, template_manager
from modules.text_renderer import (
    make_label,
    make_button,
    make_radio,
    make_option_menu,
    make_label_frame,
    render_photo,
)


class FaceBeautyApp:
    def __init__(self, root):
        # 初始化主窗口
        self.root = root
        self.root.title("人脸美化系统")

        self.root.geometry("1280x720")
        self.root.minsize(1100, 650)

        # 图像存储变量
        self.original_image = None
        self.processed_image = None
        self.photo_original = None
        self.photo_processed = None
        self.template_preview_photo = None

        # 参数变量
        self.operation = tk.StringVar(value="none")
        self.blur_strength = tk.IntVar(value=5)
        self.brightness = tk.IntVar(value=20)
        self.contrast = tk.DoubleVar(value=1.2)
        self.softness = tk.DoubleVar(value=0.5)
        self.eye_enhance = tk.DoubleVar(value=0.3)
        self.canny_low = tk.IntVar(value=50)
        self.canny_high = tk.IntVar(value=150)
        self.clahe_clip = tk.DoubleVar(value=2.0)

        # 妆造模板相关
        self.templates = template_manager.load_templates()
        self.template_name = tk.StringVar()
        self.custom_makeup_path = None
        self.makeup_source = tk.StringVar(value="builtin")  # builtin / custom

        if self.templates:
            self.template_name.set(self.templates[0]["name"])
        else:
            self.template_name.set("")

        # 选择内置模板时自动切换来源 + 刷新预览
        self.template_name.trace_add("write", self._on_template_selected)

        # 构建用户界面
        self._build_ui()

        # 初始化模板预览
        self._update_template_preview()

    def _build_ui(self):
        # 主布局
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # =========================
        # 左侧：可滚动控制面板
        # =========================
        left_container = tk.Frame(main_frame, width=320)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_container.pack_propagate(False)

        self.control_canvas = tk.Canvas(left_container, highlightthickness=0)
        self.control_scrollbar = tk.Scrollbar(
            left_container, orient=tk.VERTICAL, command=self.control_canvas.yview
        )
        self.control_inner = tk.Frame(self.control_canvas)

        self.control_inner.bind(
            "<Configure>",
            lambda e: self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))
        )

        self.control_canvas.create_window((0, 0), window=self.control_inner, anchor="nw")
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)

        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 鼠标滚轮支持
        self.control_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        control_frame = self.control_inner

        # ===== 基本操作区（LabelFrame 替换为 Frame + 渲染标题）=====
        action_frame, _ = make_label_frame(control_frame, "基本操作",
                                           relief=tk.GROOVE, bd=2, padx=8, pady=12)
        action_frame.pack(fill=tk.X, pady=6)

        make_button(action_frame, "加载图片", self.load_image,
                    width=120, height=28).grid(row=0, column=0, padx=5, pady=4)
        make_button(action_frame, "保存结果", self.save_image,
                    width=120, height=28).grid(row=0, column=1, padx=5, pady=4)
        make_button(action_frame, "重置图像", self.reset_image,
                    width=120, height=28).grid(row=1, column=0, padx=5, pady=4)
        make_button(action_frame, "执行处理", self.apply_operation,
                    width=120, height=28, bg="#4CAF50").grid(row=1, column=1, padx=5, pady=4)

        # ===== 功能选择区 =====
        op_frame, _ = make_label_frame(control_frame, "功能选择",
                                       relief=tk.GROOVE, bd=2, padx=8, pady=12)
        op_frame.pack(fill=tk.X, pady=6)

        self._operation_radios = []  # 保持引用
        operations = [
            ("无处理", "none"),
            ("均值滤波", "mean"),
            ("高斯滤波", "gaussian"),
            ("中值滤波", "median"),
            ("双边滤波", "bilateral"),
            ("直方图均衡化", "hist_eq"),
            ("CLAHE均衡化", "clahe"),
            ("拉普拉斯锐化", "laplacian"),
            ("Unsharp Mask锐化", "unsharp"),
            ("Sobel边缘检测", "sobel"),
            ("Canny边缘检测", "canny"),
            ("腐蚀", "erode"),
            ("膨胀", "dilate"),
            ("开运算", "opening"),
            ("闭运算", "closing"),
            ("人脸检测", "detect"),
            ("人脸磨皮", "beauty"),
            ("肤色柔和", "skin_soft"),
            ("对比度增强", "contrast"),
            ("眼部增强", "eye_enhance"),
            ("妆造迁移(BeautyGAN)", "beautygan"),
        ]

        for i, (text, value) in enumerate(operations):
            r = i // 2
            c = i % 2
            rb = make_radio(op_frame, text, self.operation, value)
            rb.grid(row=r, column=c, sticky="w", padx=5, pady=2)
            self._operation_radios.append(rb)

        # ===== BeautyGAN模板区 =====
        template_frame, _ = make_label_frame(control_frame, "妆造模板设置",
                                             relief=tk.GROOVE, bd=2, padx=8, pady=12)
        template_frame.pack(fill=tk.X, pady=6)

        make_radio(template_frame, "使用内置模板", self.makeup_source,
                   "builtin", command=self._update_template_preview).pack(anchor=tk.W)
        make_radio(template_frame, "使用自定义模板", self.makeup_source,
                   "custom", command=self._update_template_preview).pack(anchor=tk.W)

        make_label(template_frame, "内置模板：", fg="#333333").pack(anchor=tk.W, pady=(8, 0))
        template_names = [tpl["name"] for tpl in self.templates] if self.templates else []

        self.template_combo = make_option_menu(
            template_frame, template_names, self.template_name, width=180
        )
        self.template_combo.pack(fill=tk.X, pady=4)

        make_button(template_frame, "选择自定义模板", self.select_custom_template,
                    width=180, height=28, bg="#2196F3").pack(fill=tk.X, pady=6)

        self.template_info_label = make_label(
            template_frame, "当前：内置模板", fg="#0000FF", pad_w=2, pad_h=2,
            wraplength=260, anchor="w"
        )
        self.template_info_label.pack(fill=tk.X, pady=(4, 4))

        self.template_preview_label = tk.Label(
            template_frame,
            bd=1, relief=tk.SUNKEN,
            width=18, height=10
        )
        self.template_preview_label.pack(pady=6)
        # 初始文字用渲染图片
        _ph, _, _ = render_photo("模板预览区", fg="#999999")
        self.template_preview_label.configure(image=_ph)
        self._template_placeholder = _ph

        # ===== 参数调整区（根据所选操作动态显示）=====
        param_frame, _ = make_label_frame(control_frame, "参数调整",
                                          relief=tk.GROOVE, bd=2, padx=8, pady=12)
        param_frame.pack(fill=tk.X, pady=6)
        self._param_frame = param_frame

        # 每个参数用一个 Frame 包裹（label + scale），以便整体 show/hide
        # 模糊/磨皮强度（操作不同，标签不同）
        self._param_blur = tk.Frame(param_frame)
        self._lbl_blur = make_label(self._param_blur, "滤波核大小：", fg="#333333")
        self._lbl_blur.pack(anchor=tk.W, pady=(4, 0))
        tk.Scale(self._param_blur, from_=1, to=31, orient=tk.HORIZONTAL,
                 variable=self.blur_strength).pack(fill=tk.X)

        # 亮度调整
        self._param_bright = tk.Frame(param_frame)
        self._lbl_bright = make_label(self._param_bright, "亮度偏移：", fg="#333333")
        self._lbl_bright.pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(self._param_bright, from_=-50, to=50, orient=tk.HORIZONTAL,
                 variable=self.brightness).pack(fill=tk.X)

        # 对比度
        self._param_contrast = tk.Frame(param_frame)
        self._lbl_contrast = make_label(self._param_contrast, "对比度系数：", fg="#333333")
        self._lbl_contrast.pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(self._param_contrast, from_=0.5, to=2.0, resolution=0.1,
                 orient=tk.HORIZONTAL, variable=self.contrast).pack(fill=tk.X)

        # 柔和度
        self._param_soft = tk.Frame(param_frame)
        self._lbl_soft = make_label(self._param_soft, "柔和度：", fg="#333333")
        self._lbl_soft.pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(self._param_soft, from_=0.0, to=1.0, resolution=0.1,
                 orient=tk.HORIZONTAL, variable=self.softness).pack(fill=tk.X)

        # 眼部增强
        self._param_eye = tk.Frame(param_frame)
        self._lbl_eye = make_label(self._param_eye, "眼部增强：", fg="#333333")
        self._lbl_eye.pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(self._param_eye, from_=0.0, to=1.0, resolution=0.1,
                 orient=tk.HORIZONTAL, variable=self.eye_enhance).pack(fill=tk.X)

        # Canny 低阈值
        self._param_canny_low = tk.Frame(param_frame)
        self._lbl_canny_low = make_label(self._param_canny_low, "Canny 低阈值：", fg="#333333")
        self._lbl_canny_low.pack(anchor=tk.W, pady=(4, 0))
        tk.Scale(self._param_canny_low, from_=0, to=255, orient=tk.HORIZONTAL,
                 variable=self.canny_low).pack(fill=tk.X)

        # Canny 高阈值
        self._param_canny_high = tk.Frame(param_frame)
        self._lbl_canny_high = make_label(self._param_canny_high, "Canny 高阈值：", fg="#333333")
        self._lbl_canny_high.pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(self._param_canny_high, from_=0, to=255, orient=tk.HORIZONTAL,
                 variable=self.canny_high).pack(fill=tk.X)

        # CLAHE 对比度限制
        self._param_clahe = tk.Frame(param_frame)
        self._lbl_clahe = make_label(self._param_clahe, "CLAHE 对比度限制：", fg="#333333")
        self._lbl_clahe.pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(self._param_clahe, from_=1.0, to=5.0, resolution=0.5,
                 orient=tk.HORIZONTAL, variable=self.clahe_clip).pack(fill=tk.X)

        # 参数可见性 + 标签文字映射
        self._param_map = {
            "blur":   {"mean", "gaussian", "median", "bilateral", "unsharp",
                       "erode", "dilate", "opening", "closing", "beauty"},
            "bright": {"beauty", "contrast"},
            "contrast": {"contrast"},
            "soft":   {"skin_soft"},
            "eye":    {"eye_enhance"},
            "canny_low":   {"canny"},
            "canny_high":  {"canny"},
            "clahe":       {"clahe"},
        }
        self._param_widgets = {
            "blur":       self._param_blur,
            "bright":     self._param_bright,
            "contrast":   self._param_contrast,
            "soft":       self._param_soft,
            "eye":        self._param_eye,
            "canny_low":  self._param_canny_low,
            "canny_high": self._param_canny_high,
            "clahe":      self._param_clahe,
        }
        # 标签文字映射：操作名 → (参数key → 标签文字)
        self._param_label_texts = {
            "mean":      {"blur": "滤波核大小："},
            "gaussian":  {"blur": "高斯核大小："},
            "median":    {"blur": "滤波核大小："},
            "bilateral": {"blur": "颜色标准差："},
            "unsharp":   {"blur": "锐化强度："},
            "erode":     {"blur": "结构元素大小："},
            "dilate":    {"blur": "结构元素大小："},
            "opening":   {"blur": "结构元素大小："},
            "closing":   {"blur": "结构元素大小："},
            "beauty":    {"blur": "磨皮强度：", "bright": "亮度提升："},
            "contrast":  {"contrast": "对比度系数：", "bright": "亮度偏移："},
            "skin_soft": {"soft": "柔和度："},
            "eye_enhance": {"eye": "眼部增强："},
            "canny":     {"canny_low": "Canny 低阈值：", "canny_high": "Canny 高阈值："},
            "clahe":     {"clahe": "CLAHE 对比度限制："},
        }
        # 标签 widget 引用
        self._param_labels = {
            "blur":       self._lbl_blur,
            "bright":     self._lbl_bright,
            "contrast":   self._lbl_contrast,
            "soft":       self._lbl_soft,
            "eye":        self._lbl_eye,
            "canny_low":  self._lbl_canny_low,
            "canny_high": self._lbl_canny_high,
            "clahe":      self._lbl_clahe,
        }

        # 监听操作变化，动态显示/隐藏参数
        self.operation.trace_add("write", self._on_operation_changed)
        # 初始调用一次，根据默认值 "none" 隐藏所有
        self._on_operation_changed()

        # 底部留白
        tk.Label(control_frame, text="").pack(pady=10)

        # =========================
        # 右侧：图像显示区
        # =========================
        display_frame = tk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        title_frame = tk.Frame(display_frame)
        title_frame.pack(fill=tk.X, pady=(0, 8))

        make_label(title_frame, "图像显示区", size=14, fg="#333333",
                   bold=True).pack(anchor=tk.W)
        make_label(title_frame, "左侧为原图，右侧为处理结果",
                   fg="#999999").pack(anchor=tk.W)

        image_frame = tk.Frame(display_frame)
        image_frame.pack(fill=tk.BOTH, expand=True)

        # 原图 / 结果图 LabelFrame 改用 Frame + 渲染标题
        original_box, _ = make_label_frame(image_frame, "原图",
                                           relief=tk.GROOVE, bd=2, padx=5, pady=5)
        original_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        processed_box, _ = make_label_frame(image_frame, "处理结果",
                                            relief=tk.GROOVE, bd=2, padx=5, pady=5)
        processed_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.label_original = tk.Label(original_box, bd=1, relief=tk.SUNKEN)
        self.label_original.pack(fill=tk.BOTH, expand=True)

        self.label_processed = tk.Label(processed_box, bd=1, relief=tk.SUNKEN)
        self.label_processed.pack(fill=tk.BOTH, expand=True)

        # ===== 底部状态栏 + 进度条 =====
        status_frame = tk.Frame(display_frame)
        status_frame.pack(fill=tk.X, pady=(6, 0))

        self._progress_bar = ttk.Progressbar(
            status_frame, mode="indeterminate", length=200
        )
        self._progress_bar.pack(side=tk.RIGHT, padx=(8, 0))

        self._status_label = tk.Label(
            status_frame, text="就绪", anchor="w", fg="#666666", font=("TkDefaultFont", 9)
        )
        self._status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _set_status(self, text, processing=False):
        """更新底部状态文字，处理时显示进度条"""
        self._status_label.configure(text=text)
        if processing:
            self._progress_bar.start(10)  # 每 10ms 步进一次
            self._progress_bar.pack(side=tk.RIGHT, padx=(8, 0))
        else:
            self._progress_bar.stop()
            self._progress_bar.pack_forget()
        self.root.update_idletasks()

    def _on_mousewheel(self, event):
        """左侧控制面板鼠标滚轮滚动"""
        try:
            self.control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _on_operation_changed(self, *_args):
        """根据当前所选操作，显示/隐藏参数区 + 更新标签文字"""
        op = self.operation.get()
        all_keys = ["blur", "bright", "contrast", "soft", "eye",
                     "canny_low", "canny_high", "clahe"]

        any_visible = False
        op_labels = self._param_label_texts.get(op, {})

        # 先确定是否有可见参数
        for key in all_keys:
            if op in self._param_map[key]:
                any_visible = True
                break

        # 先控制整个参数区的显隐
        if any_visible:
            self._param_frame.pack(fill=tk.X, pady=6)
        else:
            self._param_frame.pack_forget()
            return

        # 再逐行控制（此时父容器已可见）
        for key in all_keys:
            frame = self._param_widgets[key]
            label = self._param_labels[key]
            if op in self._param_map[key]:
                # 更新标签文字（每操作的专有名词）
                txt = op_labels.get(key, None)
                if txt:
                    photo, _, _ = render_photo(txt, fg="#333333")
                    label.configure(image=photo)
                    label.image = photo
                frame.pack(fill=tk.X, pady=(0, 0))
            else:
                frame.pack_forget()

    def _on_template_selected(self, *_args):
        """从下拉菜单选择内置模板时，自动切回内置模板来源 + 刷新预览"""
        if self.makeup_source.get() != "builtin":
            self.makeup_source.set("builtin")
        self._update_template_preview()

    def load_image(self):
        """加载图像文件"""
        path = filedialog.askopenfilename(
            filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("所有文件", "*")]
        )
        if not path:
            return

        self._set_status("正在加载图片...", processing=True)
        try:
            self.original_image = image_io.load_image(path)
            self.processed_image = self.original_image.copy()
            self._update_display()
            self._set_status(f"已加载: {path.split('/')[-1].split(chr(92))[-1]}")
        except Exception as exc:
            err_msg = str(exc) or type(exc).__name__
            self._set_status(f"加载失败：{err_msg}")
            self._safe_messagebox(messagebox.showerror, "加载失败", err_msg)

    def save_image(self):
        """保存处理后的图像"""
        if self.processed_image is None:
            self._safe_messagebox(messagebox.showwarning, "保存失败", "请先加载并处理图片")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG 文件", "*.jpg"), ("PNG 文件", "*.png"), ("BMP 文件", "*.bmp")],
        )
        if not path:
            return

        try:
            ok = image_io.save_image(path, self.processed_image)
            if ok:
                self._set_status(f"已保存: {path.split('/')[-1].split(chr(92))[-1]}")
                self._safe_messagebox(messagebox.showinfo, "保存成功", f"已保存到：{path}")
            else:
                self._safe_messagebox(messagebox.showerror, "保存失败", "图像保存时发生错误")
        except Exception as exc:
            err_msg = str(exc) or type(exc).__name__
            self._safe_messagebox(messagebox.showerror, "保存失败", err_msg)

    def reset_image(self):
        """重置图像到原始状态"""
        if self.original_image is None:
            return
        self._set_status("已重置到原始状态")
        self.processed_image = self.original_image.copy()
        self._update_display()

    def select_custom_template(self):
        """选择自定义妆容模板图"""
        path = filedialog.askopenfilename(
            title="选择自定义妆容模板",
            filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("所有文件", "*")]
        )
        if not path:
            return

        self.custom_makeup_path = path
        self.makeup_source.set("custom")
        self._update_template_preview()

    def _get_selected_builtin_template(self):
        """获取当前选中的内置模板信息"""
        selected_name = self.template_name.get()
        for tpl in self.templates:
            if tpl["name"] == selected_name:
                return tpl
        return None

    def _update_template_preview(self):
        """更新模板预览图和模板来源说明"""
        preview_img = None

        try:
            if self.makeup_source.get() == "builtin":
                tpl = self._get_selected_builtin_template()
                if tpl is not None:
                    preview_img = image_io.load_image(tpl["path"])
                    txt = f"当前：内置模板\n名称：{tpl['name']}\n分类：{tpl['category']}"
                    clr = "#0000FF"
                else:
                    txt = "当前：内置模板\n未找到模板"
                    clr = "#FF0000"

            else:
                if self.custom_makeup_path:
                    preview_img = image_io.load_image(self.custom_makeup_path)
                    txt = f"当前：自定义模板\n路径：{self.custom_makeup_path}"
                    clr = "#008000"
                else:
                    txt = "当前：自定义模板\n尚未选择文件"
                    clr = "#FF0000"

            # 渲染文字为图片更新标签
            self._update_info_label(txt, clr)

            if preview_img is not None:
                preview_img = utils.resize_for_display(preview_img, max_size=(160, 160))
                self.template_preview_photo = ImageTk.PhotoImage(image=utils.cv2_to_pil(preview_img))
                self.template_preview_label.configure(image=self.template_preview_photo)
            else:
                _ph, _, _ = render_photo("模板预览区", fg="#999999")
                self._template_placeholder = _ph
                self.template_preview_label.configure(image=self._template_placeholder)

        except Exception as exc:
            err_msg = str(exc) or type(exc).__name__
            try:
                _ph, _, _ = render_photo("模板预览失败", fg="#FF0000")
                self._template_placeholder = _ph
                self.template_preview_label.configure(image=self._template_placeholder)
            except Exception:
                self.template_preview_label.configure(image="", text="预览失败",
                                                       fg="red", font=("TkDefaultFont", 9))
            self._update_info_label(f"模板加载失败：{err_msg}", "#FF0000")

    def _update_info_label(self, text, color="#000000"):
        """用渲染文字更新 template_info_label，内置容错兜底"""
        if not text or not text.strip():
            text = "(无详细信息)"
        try:
            photo, _, _ = render_photo(text, size=10, fg=color, pad_w=2, pad_h=2)
            self.template_info_label.configure(image=photo)
            self.template_info_label.image = photo
        except Exception:
            # 渲染失败时回退到 tk 原生 Label（可能中文显示乱码但不影响诊断）
            self.template_info_label.configure(
                image="", text=text, fg=color,
                font=("TkDefaultFont", 10),
                wraplength=260, justify=tk.LEFT, anchor="w"
            )

    def _get_makeup_image_for_beautygan(self):
        """根据当前设置获取BeautyGAN需要的妆容参考图"""
        if self.makeup_source.get() == "builtin":
            tpl = self._get_selected_builtin_template()
            if tpl is None:
                raise ValueError("未选择有效的内置妆造模板")
            return image_io.load_image(tpl["path"])

        elif self.makeup_source.get() == "custom":
            if not self.custom_makeup_path:
                raise ValueError("尚未选择自定义妆造模板")
            return image_io.load_image(self.custom_makeup_path)

        else:
            raise ValueError("未知的妆造模板来源")

    def _safe_messagebox(self, fn, title, message):
        """用渲染文字对话框替代原生 messagebox（中文不乱码 + 容错兜底）"""
        try:
            if not self.root.winfo_exists():
                print(f"[{title}] {message}")
                return

            dlg = tk.Toplevel(self.root)
            dlg.title("")
            dlg.resizable(False, False)
            dlg.transient(self.root)
            dlg.grab_set()

            # 中/英文标题映射
            title_map = {
                messagebox.showerror:   ("错误", "Error"),
                messagebox.showwarning: ("警告", "Warning"),
                messagebox.showinfo:    ("提示", "Info"),
            }
            cn_title, en_title = title_map.get(fn, ("提示", "Info"))
            accent = {"错误":"#D32F2F", "警告":"#F57C00", "提示":"#1976D2"}.get(cn_title, "#333333")

            try:
                # ---- 尝试渲染中文版 ----
                title_photo, _, _ = render_photo(cn_title, size=13, fg=accent, bold=True)
                msg_photo, _, _ = render_photo(message, size=11, fg="#333333", pad_w=8, pad_h=4)

                title_frame = tk.Frame(dlg)
                title_frame.pack(fill=tk.X, padx=12, pady=(12, 4))
                tk.Label(title_frame, image=title_photo).pack(side=tk.LEFT)
                title_frame._img = title_photo

                msg_frame = tk.Frame(dlg)
                msg_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))
                tk.Label(msg_frame, image=msg_photo, wraplength=360).pack()
                msg_frame._img = msg_photo

                btn_text = "确定"
            except Exception:
                # ---- 渲染失败 → 降级为英文版（无需中文字体） ----
                title_frame = tk.Frame(dlg)
                title_frame.pack(fill=tk.X, padx=12, pady=(12, 4))
                tk.Label(title_frame, text=f" {en_title}", fg=accent,
                         font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)

                msg_frame = tk.Frame(dlg)
                msg_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))
                tk.Label(msg_frame, text=message, fg="#333333",
                         font=("TkDefaultFont", 10), wraplength=360,
                         justify=tk.LEFT).pack()
                btn_text = "OK"

            # 确定按钮
            btn_frame = tk.Frame(dlg)
            btn_frame.pack(pady=(0, 10))
            btn = make_button(btn_frame, btn_text, dlg.destroy, width=80, height=28)
            btn.pack()

            # 居中
            dlg.update_idletasks()
            rw = self.root.winfo_x()
            rh = self.root.winfo_y()
            rww = self.root.winfo_width()
            rwh = self.root.winfo_height()
            dw = dlg.winfo_width()
            dh = dlg.winfo_height()
            dlg.geometry(f"+{rw + (rww - dw) // 2}+{rh + (rwh - dh) // 2}")
            dlg.wait_window()
        except Exception:
            print(f"[{title}] {message}")

    def apply_operation(self):
        """根据选择的处理类型应用图像处理（统一走services层）"""
        if self.original_image is None:
            self._safe_messagebox(messagebox.showwarning, "操作失败", "请先加载图片")
            return

        op = self.operation.get()
        if op == "none":
            self.reset_image()
            return

        # 妆造迁移前置检查：必须有有效模板
        if op == "beautygan":
            if self.makeup_source.get() == "builtin":
                tpl = self._get_selected_builtin_template()
                if tpl is None:
                    print(f"[debug] templeta check fail: name='{self.template_name.get()}' "
                          f"templates={[t['name'] for t in self.templates]}")
                    self._safe_messagebox(messagebox.showwarning, "缺少模板",
                                           "请先在「妆造模板设置」中选择一个有效的内置模板")
                    return
                # 加载妆容参考图（确保路径正确，能正常读取）
                try:
                    _test = image_io.load_image(tpl["path"])
                except Exception as e:
                    print(f"[debug] template image load fail: {tpl['path']} -> {e}")
                    self._safe_messagebox(messagebox.showerror, "模板错误",
                                           f"模板图片无法读取：{tpl['name']}\n文件可能已损坏或缺失")
                    return
            if self.makeup_source.get() == "custom" and not self.custom_makeup_path:
                self._safe_messagebox(messagebox.showwarning, "缺少模板",
                                       "请先在「妆造模板设置」中选择自定义模板图片")
                return

        # 操作名映射（用于状态栏显示）
        op_names = {
            "mean": "均值滤波", "gaussian": "高斯滤波", "median": "中值滤波",
            "bilateral": "双边滤波", "hist_eq": "直方图均衡化", "clahe": "CLAHE均衡化",
            "laplacian": "拉普拉斯锐化", "unsharp": "USM锐化",
            "sobel": "Sobel边缘检测", "canny": "Canny边缘检测",
            "erode": "腐蚀", "dilate": "膨胀", "opening": "开运算", "closing": "闭运算",
            "detect": "人脸检测", "beauty": "人脸磨皮", "skin_soft": "肤色柔和",
            "contrast": "对比度增强", "eye_enhance": "眼部增强",
            "beautygan": "妆造迁移(BeautyGAN)",
        }
        display_name = op_names.get(op, op)
        self._set_status(f"正在处理: {display_name}...", processing=True)

        try:
            makeup_img = None
            if op == "beautygan":
                makeup_img = self._get_makeup_image_for_beautygan()
                self._set_status("BeautyGAN 推理中（首次需加载模型）...", processing=True)

            self.processed_image = services.apply_operation(
                image=self.original_image,
                operation=op,
                blur_strength=self.blur_strength.get(),
                brightness=self.brightness.get(),
                contrast=self.contrast.get(),
                softness=self.softness.get(),
                eye_enhance=self.eye_enhance.get(),
                canny_low=self.canny_low.get(),
                canny_high=self.canny_high.get(),
                clahe_clip=self.clahe_clip.get(),
                makeup_image=makeup_img,
            )

            self._update_display()
            self._set_status(f"完成: {display_name}")

        except Exception as exc:
            err_msg = str(exc) or type(exc).__name__
            self._set_status(f"处理失败：{err_msg}")
            self._safe_messagebox(messagebox.showerror, "处理失败", err_msg)

    def _update_display(self):
        """更新图像显示"""
        if self.original_image is not None:
            original = utils.resize_for_display(self.original_image, max_size=(450, 550))
            self.photo_original = ImageTk.PhotoImage(image=utils.cv2_to_pil(original))
            self.label_original.configure(image=self.photo_original, text="")

        if self.processed_image is not None:
            processed = utils.resize_for_display(self.processed_image, max_size=(450, 550))
            self.photo_processed = ImageTk.PhotoImage(image=utils.cv2_to_pil(processed))
            self.label_processed.configure(image=self.photo_processed, text="")


def run_app():
    """启动应用程序"""
    root = tk.Tk()
    app = FaceBeautyApp(root)
    root.mainloop()