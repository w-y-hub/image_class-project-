"""
人脸美化系统主入口文件

这个文件是整个应用程序的启动点，负责导入GUI模块并运行应用程序。
"""

import locale
import os

# 设置locale确保UTF-8支持（解决Linux下中文显示问题）
locale.setlocale(locale.LC_ALL, "C.utf8")
os.environ.setdefault("LANG", "C.utf8")

from modules.gui import run_app  # 导入GUI运行函数


if __name__ == "__main__":
    # 当脚本直接运行时，启动应用程序
    run_app()
