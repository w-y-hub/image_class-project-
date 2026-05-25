import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_ROOT = os.path.join(BASE_DIR, "assets", "makeup_templates")
TEMPLATE_CONFIG = os.path.join(TEMPLATE_ROOT, "templates.json")


def load_templates():
    """加载妆造模板配置"""
    if not os.path.exists(TEMPLATE_CONFIG):
        print(f">>> 模板配置文件不存在: {TEMPLATE_CONFIG}")
        return []

    try:
        with open(TEMPLATE_CONFIG, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print(">>> templates.json 为空，返回空模板列表")
                return []

            data = json.loads(content)

        templates = []
        for item in data:
            file_path = os.path.join(TEMPLATE_ROOT, item["file"])
            if os.path.exists(file_path):
                templates.append({
                    "id": item["id"],
                    "name": item["name"],
                    "category": item.get("category", "默认"),
                    "path": file_path
                })
            else:
                print(f">>> 模板图片不存在，已跳过: {file_path}")

        print(f">>> 成功加载模板数量: {len(templates)}")
        return templates

    except Exception as exc:
        print(f">>> 读取模板配置失败: {exc}")
        return []