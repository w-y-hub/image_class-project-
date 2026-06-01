# 环境搭建说明

## 技术栈选择

本项目使用 **uv**（Python 包管理器）管理虚拟环境和依赖，而非 conda。

| 组件 | 选择 | 原因 |
|------|------|------|
| 包管理器 | uv | 速度快、跨平台一致、自动管理 Python 版本 |
| Python 版本 | 3.11 | pyproject.toml 中指定，由 uv 自动下载 |
| 虚拟环境 | `.venv/` | uv 创建的本地隔离环境 |

## 环境搭建（首次运行）

### 1. 安装 uv

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

重启终端后检查：
```bash
uv --version
```

### 2. 创建虚拟环境并安装依赖

项目已配置好 `pyproject.toml` 和 `requirements.txt`，只需一条命令：

```bash
# 在项目根目录执行
uv sync
```

`uv sync` 会自动：
- 创建 `.venv/` 虚拟环境（使用 Python 3.11）
- 安装 `pyproject.toml` 中列出的所有依赖
- 锁定版本至 `uv.lock`

### 3. 启动程序

```bash
# 激活环境后运行
.venv/bin/python main.py

# 或使用 uv
uv run python main.py
```

### 4. 日常运行（环境已建好）

```bash
uv run python main.py
```

## 常见问题

### Q: 提示 "No module named pip"
A: 首次运行需先执行 `uv sync` 安装依赖。直接 `uv run` 会自动处理。

### Q: 提示找不到 Python 3.11
A: uv 会自动下载所需的 Python 版本（`uv python install 3.11`）。若手动安装，确保版本在 3.10–3.13 之间。

### Q: 需要添加新的依赖
```bash
uv add <包名>        # 写入 pyproject.toml 并安装
uv remove <包名>     # 从 pyproject.toml 移除
```

### Q: 想要更新所有依赖
```bash
uv sync --upgrade
```

### Q: 虚拟环境坏了想重建
```bash
rm -rf .venv
uv sync
```

## 关于 conda

本项目**不依赖 conda**。如果之前使用 conda 管理环境：

1. 无需卸载 conda，只需使用 uv 创建独立环境
2. 项目中的 `.venv/` 与 conda 环境完全隔离
3. 如需彻底清理 conda 残留：
   ```bash
   conda env remove -n image-course   # 如果有同名 conda 环境
   ```
4. 删除 `~/.conda/` 目录中的与本项目相关的缓存（可选）
