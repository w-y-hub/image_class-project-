# -*- coding: utf-8 -*-
"""
modules/beautygan.py
封装BeautyGAN妆造迁移推理逻辑，供GUI调用。
"""
import tensorflow.compat.v1 as tf
import numpy as np
import os
import cv2

tf.disable_v2_behavior()

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'modelBeautyGAN')
META_PATH = os.path.join(MODEL_DIR, 'model.meta')
CKPT_DIR = MODEL_DIR
IMG_SIZE = 256

def preprocess(img):
    return (img / 255.0 - 0.5) * 2.0

def deprocess(img):
    return (img + 1.0) / 2.0

def beautygan_transfer(no_makeup_img: np.ndarray, makeup_img: np.ndarray) -> np.ndarray:
    """
    输入：无妆图片、带妆图片（BGR格式，np.ndarray）
    输出：妆造迁移后图片（BGR格式，np.ndarray）
    """
    if no_makeup_img is None or makeup_img is None:
        raise ValueError("输入图像不能为空")

    if not os.path.exists(META_PATH):
        raise FileNotFoundError(f"找不到模型文件: {META_PATH}")

    ckpt = tf.train.latest_checkpoint(CKPT_DIR)
    if ckpt is None:
        raise FileNotFoundError(f"找不到checkpoint文件: {CKPT_DIR}")

    # 记录原图尺寸
    h, w = no_makeup_img.shape[:2]

    # OpenCV读入是BGR，先转RGB
    no_makeup_rgb = cv2.cvtColor(no_makeup_img, cv2.COLOR_BGR2RGB)
    makeup_rgb = cv2.cvtColor(makeup_img, cv2.COLOR_BGR2RGB)

    # resize到模型输入大小
    no_makeup_rgb = cv2.resize(no_makeup_rgb, (IMG_SIZE, IMG_SIZE))
    makeup_rgb = cv2.resize(makeup_rgb, (IMG_SIZE, IMG_SIZE))

    X_img = np.expand_dims(preprocess(no_makeup_rgb).astype(np.float32), 0)
    Y_img = np.expand_dims(preprocess(makeup_rgb).astype(np.float32), 0)

    tf.reset_default_graph()
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(META_PATH)
        saver.restore(sess, ckpt)

        graph = tf.get_default_graph()

        try:
            X = graph.get_tensor_by_name('X:0')
            Y = graph.get_tensor_by_name('Y:0')
            Xs = graph.get_tensor_by_name('generator/xs:0')
        except Exception as e:
            raise RuntimeError(f"模型张量名称不匹配，请检查模型结构: {e}")

        Xs_ = sess.run(Xs, feed_dict={X: X_img, Y: Y_img})

    Xs_ = deprocess(Xs_)
    result = np.clip(Xs_[0] * 255.0, 0, 255).astype(np.uint8)

    # RGB转回BGR
    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    # 缩放回原图尺寸，便于GUI显示
    result_bgr = cv2.resize(result_bgr, (w, h))

    return result_bgr