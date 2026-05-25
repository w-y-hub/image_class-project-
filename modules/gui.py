import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
import cv2

from modules import image_io, filters, face_detection, beauty, utils


class FaceBeautyApp:
    def __init__(self, root):
        # 初始化主窗口
        self.root = root
        self.root.title("人脸美化系统")
        self.root.geometry("1200x700")

        # 图像存储变量
        self.original_image = None  # 原始图像
        self.processed_image = None  # 处理后图像
        self.photo_original = None  # 原图显示用PhotoImage
        self.photo_processed = None  # 处理图显示用PhotoImage

        # 参数变量
        self.operation = tk.StringVar(value="none")  # 当前选择的处理操作
        self.blur_strength = tk.IntVar(value=5)  # 模糊强度
        self.brightness = tk.IntVar(value=20)  # 亮度调整
        self.contrast = tk.DoubleVar(value=1.2)  # 对比度
        self.softness = tk.DoubleVar(value=0.5)  # 柔和度
        self.eye_enhance = tk.DoubleVar(value=0.3)  # 眼部增强

        # 构建用户界面
        self._build_ui()

    def _build_ui(self):
        # 创建控制面板（左侧）
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 基本操作按钮
        tk.Button(control_frame, text="加载图片", width=16, command=self.load_image).pack(pady=6)
        tk.Button(control_frame, text="保存结果", width=16, command=self.save_image).pack(pady=6)
        tk.Button(control_frame, text="重置图像", width=16, command=self.reset_image).pack(pady=6)
        tk.Button(control_frame, text="执行处理", width=16, command=self.apply_operation).pack(pady=6)

        # 分割线
        tk.Label(control_frame, text="─" * 20).pack(pady=5)

        # 功能选择单选按钮
        tk.Label(control_frame, text="选择功能：").pack(anchor=tk.W, pady=(12, 0))

        # 图像处理功能
        tk.Radiobutton(control_frame, text="无处理", variable=self.operation, value="none").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="均值滤波", variable=self.operation, value="mean").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="高斯滤波", variable=self.operation, value="gaussian").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="中值滤波", variable=self.operation, value="median").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="双边滤波", variable=self.operation, value="bilateral").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="直方图均衡化", variable=self.operation, value="hist_eq").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="CLAHE均衡化", variable=self.operation, value="clahe").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="拉普拉斯锐化", variable=self.operation, value="laplacian").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="Unsharp Mask锐化", variable=self.operation, value="unsharp").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="Sobel边缘检测", variable=self.operation, value="sobel").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="Canny边缘检测", variable=self.operation, value="canny").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="腐蚀", variable=self.operation, value="erode").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="膨胀", variable=self.operation, value="dilate").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="开运算", variable=self.operation, value="opening").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="闭运算", variable=self.operation, value="closing").pack(anchor=tk.W)

        # 人脸相关功能
        tk.Radiobutton(control_frame, text="人脸检测", variable=self.operation, value="detect").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="人脸磨皮", variable=self.operation, value="beauty").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="肤色柔和", variable=self.operation, value="skin_soft").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="对比度增强", variable=self.operation, value="contrast").pack(anchor=tk.W)
        tk.Radiobutton(control_frame, text="眼部增强", variable=self.operation, value="eye_enhance").pack(anchor=tk.W)

        # 参数调节滑块
        tk.Label(control_frame, text="模糊/磨皮强度：").pack(anchor=tk.W, pady=(12, 0))
        tk.Scale(control_frame, from_=1, to=31, orient=tk.HORIZONTAL, variable=self.blur_strength).pack(fill=tk.X)

        tk.Label(control_frame, text="亮度调整：").pack(anchor=tk.W, pady=(12, 0))
        tk.Scale(control_frame, from_=-50, to=50, orient=tk.HORIZONTAL, variable=self.brightness).pack(fill=tk.X)

        tk.Label(control_frame, text="对比度：").pack(anchor=tk.W, pady=(12, 0))
        tk.Scale(control_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.contrast).pack(fill=tk.X)

        tk.Label(control_frame, text="柔和度：").pack(anchor=tk.W, pady=(12, 0))
        tk.Scale(control_frame, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.softness).pack(fill=tk.X)

        tk.Label(control_frame, text="眼部增强：").pack(anchor=tk.W, pady=(12, 0))
        tk.Scale(control_frame, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.eye_enhance).pack(fill=tk.X)

        # 创建显示面板（右侧）
        display_frame = tk.Frame(self.root)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 原图显示标签
        self.label_original = tk.Label(display_frame, text="原图显示区", bd=1, relief=tk.SUNKEN)
        self.label_original.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 处理后图像显示标签
        self.label_processed = tk.Label(display_frame, text="处理后显示区", bd=1, relief=tk.SUNKEN)
        self.label_processed.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

    def load_image(self):
        """加载图像文件"""
        # 打开文件选择对话框
        path = filedialog.askopenfilename(
            filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("所有文件", "*")]
        )
        if not path:
            return

        try:
            # 使用image_io模块加载图像
            self.original_image = image_io.load_image(path)
            # 复制一份作为处理图像
            self.processed_image = self.original_image.copy()
            # 更新显示
            self._update_display()
        except Exception as exc:
            # 显示错误消息
            messagebox.showerror("加载失败", str(exc))

    def save_image(self):
        """保存处理后的图像"""
        if self.processed_image is None:
            messagebox.showwarning("保存失败", "请先加载并处理图片")
            return

        # 打开保存文件对话框
        path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG 文件", "*.jpg"), ("PNG 文件", "*.png"), ("BMP 文件", "*.bmp")],
        )
        if not path:
            return

        # 保存图像
        if image_io.save_image(path, self.processed_image):
            messagebox.showinfo("保存成功", f"已保存到：{path}")
        else:
            messagebox.showerror("保存失败", "图像保存时发生错误")

    def reset_image(self):
        """重置图像到原始状态"""
        if self.original_image is None:
            return
        self.processed_image = self.original_image.copy()
        self._update_display()

    def apply_operation(self):
        """根据选择的处理类型应用图像处理"""
        if self.original_image is None:
            messagebox.showwarning("操作失败", "请先加载图片")
            return

        try:
            op = self.operation.get()
            if op == "none":
                self.processed_image = self.original_image.copy()
            elif op == "mean":
                self.processed_image = filters.mean_blur(self.original_image, self.blur_strength.get())
            elif op == "gaussian":
                self.processed_image = filters.gaussian_blur(self.original_image, self.blur_strength.get())
            elif op == "median":
                self.processed_image = filters.median_blur(self.original_image, self.blur_strength.get())
            elif op == "bilateral":
                self.processed_image = filters.bilateral_filter(self.original_image, d=9, sigma_color=self.blur_strength.get()*2, sigma_space=self.blur_strength.get())
            elif op == "hist_eq":
                self.processed_image = filters.histogram_equalization(self.original_image)
            elif op == "clahe":
                self.processed_image = filters.clahe_equalization(self.original_image)
            elif op == "laplacian":
                self.processed_image = filters.laplacian_sharpen(self.original_image)
            elif op == "unsharp":
                self.processed_image = filters.unsharp_mask_sharpen(self.original_image, sigma=1.0, strength=self.blur_strength.get()/10.0)
            elif op == "sobel":
                self.processed_image = filters.sobel_filter(self.original_image)
            elif op == "canny":
                self.processed_image = filters.canny_edge(self.original_image, threshold1=100, threshold2=200)
            elif op == "erode":
                self.processed_image = filters.erode(self.original_image, self.blur_strength.get())
            elif op == "dilate":
                self.processed_image = filters.dilate(self.original_image, self.blur_strength.get())
            elif op == "opening":
                self.processed_image = filters.opening(self.original_image, self.blur_strength.get())
            elif op == "closing":
                self.processed_image = filters.closing(self.original_image, self.blur_strength.get())
            elif op == "detect":
                faces = face_detection.detect_faces(self.original_image)
                self.processed_image = face_detection.draw_faces(self.original_image, faces)
            elif op == "beauty":
                faces = face_detection.detect_faces(self.original_image)
                self.processed_image = beauty.beautify_face_roi(
                    self.original_image, faces, smooth_strength=self.blur_strength.get(), brightness=self.brightness.get()
                )
            elif op == "skin_soft":
                faces = face_detection.detect_faces(self.original_image)
                self.processed_image = beauty.skin_softening(self.original_image, faces, self.softness.get())
            elif op == "contrast":
                self.processed_image = beauty.global_contrast_enhancement(self.original_image, self.contrast.get(), self.brightness.get())
            elif op == "eye_enhance":
                faces = face_detection.detect_faces(self.original_image)
                self.processed_image = beauty.eye_enhancement(self.original_image, faces, self.eye_enhance.get())
            else:
                self.processed_image = self.original_image.copy()

            # 更新显示
            self._update_display()
        except Exception as exc:
            messagebox.showerror("处理失败", str(exc))

    def _update_display(self):
        """更新图像显示"""
        if self.original_image is not None:
            # 缩放原图用于显示
            original = utils.resize_for_display(self.original_image, max_size=(450, 550))
            # 转换为PIL格式用于tkinter显示
            self.photo_original = ImageTk.PhotoImage(image=utils.cv2_to_pil(original))
            self.label_original.configure(image=self.photo_original, text="")

        if self.processed_image is not None:
            # 缩放处理图用于显示
            processed = utils.resize_for_display(self.processed_image, max_size=(450, 550))
            self.photo_processed = ImageTk.PhotoImage(image=utils.cv2_to_pil(processed))
            self.label_processed.configure(image=self.photo_processed, text="")


def run_app():
    """启动应用程序"""
    root = tk.Tk()
    app = FaceBeautyApp(root)
    root.mainloop()
