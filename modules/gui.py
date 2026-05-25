import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk

from modules import image_io, utils, services, template_manager


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

        # 妆造模板相关
        self.templates = template_manager.load_templates()
        self.template_name = tk.StringVar()
        self.custom_makeup_path = None
        self.makeup_source = tk.StringVar(value="builtin")  # builtin / custom

        if self.templates:
            self.template_name.set(self.templates[0]["name"])
        else:
            self.template_name.set("")

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

        # ===== 基本操作区 =====
        action_frame = tk.LabelFrame(control_frame, text="基本操作", padx=8, pady=8)
        action_frame.pack(fill=tk.X, pady=6)

        tk.Button(action_frame, text="加载图片", width=16, command=self.load_image).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(action_frame, text="保存结果", width=16, command=self.save_image).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(action_frame, text="重置图像", width=16, command=self.reset_image).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(action_frame, text="执行处理", width=16, command=self.apply_operation, bg="#4CAF50", fg="white").grid(
            row=1, column=1, padx=5, pady=5
        )

        # ===== 功能选择区 =====
        op_frame = tk.LabelFrame(control_frame, text="功能选择", padx=8, pady=8)
        op_frame.pack(fill=tk.X, pady=6)

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
            tk.Radiobutton(
                op_frame,
                text=text,
                variable=self.operation,
                value=value,
                anchor="w",
                justify=tk.LEFT
            ).grid(row=r, column=c, sticky="w", padx=5, pady=2)

        # ===== BeautyGAN模板区 =====
        template_frame = tk.LabelFrame(control_frame, text="妆造模板设置", padx=8, pady=8)
        template_frame.pack(fill=tk.X, pady=6)

        tk.Radiobutton(
            template_frame,
            text="使用内置模板",
            variable=self.makeup_source,
            value="builtin",
            command=self._update_template_preview
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            template_frame,
            text="使用自定义模板",
            variable=self.makeup_source,
            value="custom",
            command=self._update_template_preview
        ).pack(anchor=tk.W)

        tk.Label(template_frame, text="内置模板：").pack(anchor=tk.W, pady=(8, 0))
        template_names = [tpl["name"] for tpl in self.templates] if self.templates else []

        self.template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.template_name,
            values=template_names,
            state="readonly"
        )
        self.template_combo.pack(fill=tk.X, pady=4)
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)

        tk.Button(
            template_frame,
            text="选择自定义模板",
            command=self.select_custom_template
        ).pack(fill=tk.X, pady=6)

        self.template_info_label = tk.Label(
            template_frame,
            text="当前：内置模板",
            fg="blue",
            justify=tk.LEFT,
            anchor="w",
            wraplength=260
        )
        self.template_info_label.pack(fill=tk.X, pady=(4, 4))

        self.template_preview_label = tk.Label(
            template_frame,
            text="模板预览区",
            bd=1,
            relief=tk.SUNKEN,
            width=18,
            height=10
        )
        self.template_preview_label.pack(pady=6)

        # ===== 参数调整区 =====
        param_frame = tk.LabelFrame(control_frame, text="参数调整", padx=8, pady=8)
        param_frame.pack(fill=tk.X, pady=6)

        tk.Label(param_frame, text="模糊/磨皮强度：").pack(anchor=tk.W, pady=(4, 0))
        tk.Scale(param_frame, from_=1, to=31, orient=tk.HORIZONTAL, variable=self.blur_strength).pack(fill=tk.X)

        tk.Label(param_frame, text="亮度调整：").pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(param_frame, from_=-50, to=50, orient=tk.HORIZONTAL, variable=self.brightness).pack(fill=tk.X)

        tk.Label(param_frame, text="对比度：").pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(
            param_frame,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.contrast
        ).pack(fill=tk.X)

        tk.Label(param_frame, text="柔和度：").pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(
            param_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.softness
        ).pack(fill=tk.X)

        tk.Label(param_frame, text="眼部增强：").pack(anchor=tk.W, pady=(8, 0))
        tk.Scale(
            param_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.eye_enhance
        ).pack(fill=tk.X)

        # 底部留白，避免滚动到底时太贴边
        tk.Label(control_frame, text="").pack(pady=10)

        # =========================
        # 右侧：图像显示区
        # =========================
        display_frame = tk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        title_frame = tk.Frame(display_frame)
        title_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(title_frame, text="图像显示区", font=("微软雅黑", 13, "bold")).pack(anchor=tk.W)
        tk.Label(title_frame, text="左侧为原图，右侧为处理结果", fg="gray").pack(anchor=tk.W)

        image_frame = tk.Frame(display_frame)
        image_frame.pack(fill=tk.BOTH, expand=True)

        original_box = tk.LabelFrame(image_frame, text="原图", padx=5, pady=5)
        original_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        processed_box = tk.LabelFrame(image_frame, text="处理结果", padx=5, pady=5)
        processed_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.label_original = tk.Label(original_box, text="原图显示区", bd=1, relief=tk.SUNKEN)
        self.label_original.pack(fill=tk.BOTH, expand=True)

        self.label_processed = tk.Label(processed_box, text="处理后显示区", bd=1, relief=tk.SUNKEN)
        self.label_processed.pack(fill=tk.BOTH, expand=True)

    def _on_mousewheel(self, event):
        """左侧控制面板鼠标滚轮滚动"""
        try:
            self.control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def on_template_selected(self, event=None):
        """选择内置模板后自动切换到内置模板来源"""
        self.makeup_source.set("builtin")
        self._update_template_preview()

    def load_image(self):
        """加载图像文件"""
        path = filedialog.askopenfilename(
            filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("所有文件", "*")]
        )
        if not path:
            return

        try:
            self.original_image = image_io.load_image(path)
            self.processed_image = self.original_image.copy()
            self._update_display()
        except Exception as exc:
            messagebox.showerror("加载失败", str(exc))

    def save_image(self):
        """保存处理后的图像"""
        if self.processed_image is None:
            messagebox.showwarning("保存失败", "请先加载并处理图片")
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
                messagebox.showinfo("保存成功", f"已保存到：{path}")
            else:
                messagebox.showerror("保存失败", "图像保存时发生错误")
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc))

    def reset_image(self):
        """重置图像到原始状态"""
        if self.original_image is None:
            return
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
                    self.template_info_label.configure(
                        text=f"当前：内置模板\n名称：{tpl['name']}\n分类：{tpl['category']}",
                        fg="blue"
                    )
                else:
                    self.template_info_label.configure(
                        text="当前：内置模板\n未找到模板",
                        fg="red"
                    )

            else:
                if self.custom_makeup_path:
                    preview_img = image_io.load_image(self.custom_makeup_path)
                    self.template_info_label.configure(
                        text=f"当前：自定义模板\n路径：{self.custom_makeup_path}",
                        fg="green"
                    )
                else:
                    self.template_info_label.configure(
                        text="当前：自定义模板\n尚未选择文件",
                        fg="red"
                    )

            if preview_img is not None:
                preview_img = utils.resize_for_display(preview_img, max_size=(160, 160))
                self.template_preview_photo = ImageTk.PhotoImage(image=utils.cv2_to_pil(preview_img))
                self.template_preview_label.configure(image=self.template_preview_photo, text="")
            else:
                self.template_preview_label.configure(image="", text="模板预览区")

        except Exception as exc:
            self.template_preview_label.configure(image="", text="模板预览失败")
            self.template_info_label.configure(text=f"模板加载失败：{exc}", fg="red")

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

    def apply_operation(self):
        """根据选择的处理类型应用图像处理（统一走services层）"""
        if self.original_image is None:
            messagebox.showwarning("操作失败", "请先加载图片")
            return

        try:
            op = self.operation.get()
            makeup_img = None

            if op == "beautygan":
                makeup_img = self._get_makeup_image_for_beautygan()

            self.processed_image = services.apply_operation(
                image=self.original_image,
                operation=op,
                blur_strength=self.blur_strength.get(),
                brightness=self.brightness.get(),
                contrast=self.contrast.get(),
                softness=self.softness.get(),
                eye_enhance=self.eye_enhance.get(),
                makeup_image=makeup_img,
            )

            self._update_display()

        except Exception as exc:
            messagebox.showerror("处理失败", str(exc))

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