
import locale
import os

# 设置locale确保UTF-8支持（解决Linux下中文显示问题）
locale.setlocale(locale.LC_ALL, "C.utf8")
os.environ.setdefault("LANG", "C.utf8")

# 屏蔽 TensorFlow + absl 日志噪音（必须在 import tensorflow 之前设置）
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["ABSL_MIN_LOG_LEVEL"] = "3"

from modules.gui import run_app 


if __name__ == "__main__":
    run_app()
