from modules import filters, face_detection, beauty


def apply_operation(
    image,
    operation,
    blur_strength=5,
    brightness=20,
    contrast=1.2,
    softness=0.5,
    eye_enhance=0.3,
    canny_low=50,
    canny_high=150,
    clahe_clip=2.0,
    makeup_image=None,
    makeup_path=None,
):
    if image is None:
        raise ValueError("输入图像不能为空")

    op = operation

    # 统一兼容中英文操作名
    alias = {
        "原图": "none",
        "均值滤波": "mean",
        "高斯模糊": "gaussian",
        "中值滤波": "median",
        "双边滤波": "bilateral",
        "直方图均衡": "hist_eq",
        "CLAHE": "clahe",
        "拉普拉斯锐化": "laplacian",
        "USM锐化": "unsharp",
        "Sobel边缘": "sobel",
        "Canny边缘": "canny",
        "腐蚀": "erode",
        "膨胀": "dilate",
        "开运算": "opening",
        "闭运算": "closing",
        "人脸检测": "detect",
        "美颜": "beauty",
        "肤色柔和": "skin_soft",
        "对比度增强": "contrast",
        "眼部增强": "eye_enhance",
        "妆容迁移": "beautygan",
    }

    op = alias.get(op, op)

    if op == "none":
        return image.copy()

    elif op == "mean":
        return filters.mean_blur(image, blur_strength)

    elif op == "gaussian":
        return filters.gaussian_blur(image, blur_strength)

    elif op == "median":
        return filters.median_blur(image, blur_strength)

    elif op == "bilateral":
        return filters.bilateral_filter(
            image,
            d=9,
            sigma_color=blur_strength * 2,
            sigma_space=blur_strength
        )

    elif op == "hist_eq":
        return filters.histogram_equalization(image)

    elif op == "clahe":
        return filters.clahe_equalization(image, clip_limit=clahe_clip)

    elif op == "laplacian":
        return filters.laplacian_sharpen(image)

    elif op == "unsharp":
        return filters.unsharp_mask_sharpen(
            image,
            sigma=1.0,
            strength=blur_strength / 10.0
        )

    elif op == "sobel":
        return filters.sobel_filter(image)

    elif op == "canny":
        return filters.canny_edge(image, threshold1=canny_low, threshold2=canny_high)

    elif op == "erode":
        return filters.erode(image, blur_strength)

    elif op == "dilate":
        return filters.dilate(image, blur_strength)

    elif op == "opening":
        return filters.opening(image, blur_strength)

    elif op == "closing":
        return filters.closing(image, blur_strength)

    elif op == "detect":
        faces = face_detection.detect_faces(image)
        return face_detection.draw_faces(image, faces)

    elif op == "beauty":
        faces = face_detection.detect_faces(image)
        if len(faces) == 0:
            raise ValueError("未检测到人脸，无法执行人脸磨皮")
        return beauty.beautify_face_roi(
            image,
            faces,
            smooth_strength=blur_strength,
            brightness=brightness
        )

    elif op == "skin_soft":
        faces = face_detection.detect_faces(image)
        if len(faces) == 0:
            raise ValueError("未检测到人脸，无法执行肤色柔和")
        return beauty.skin_softening(image, faces, softness)

    elif op == "contrast":
        return beauty.global_contrast_enhancement(image, contrast, brightness)

    elif op == "eye_enhance":
        faces = face_detection.detect_faces(image)
        if len(faces) == 0:
            raise ValueError("未检测到人脸，无法执行眼部增强")
        return beauty.eye_enhancement(image, faces, eye_enhance)

    elif op == "beautygan":
        # 懒加载：只有选择 BeautyGAN 时才导入 tensorflow
        from modules import beautygan

        # 同时兼容 makeup_image 和 makeup_path
        makeup_ref = makeup_image if makeup_image is not None else makeup_path
        if makeup_ref is None:
            raise ValueError("未提供妆容参考图")

        return beautygan.beautygan_transfer(image, makeup_ref)

    else:
        raise ValueError(f"不支持的操作类型: {operation}")