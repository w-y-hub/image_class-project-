"""
文字→图片渲染引擎

所有中文文字通过 Pillow + 项目自带 NotoSansSC.ttf 渲染为图片，
再用 tkinter.Label(image=...) 显示，彻底绕过系统字体 / fontconfig。
"""
import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk


# ── 常量 ─────────────────────────────────────────────
_FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "fonts", "NotoSansSC.ttf",
)
_DEFAULT_SIZE = 11


# ── 字体缓存 ─────────────────────────────────────────
_font_cache = {}


def _get_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        font = ImageFont.truetype(_FONT_PATH, size)
        _font_cache[key] = font
    return _font_cache[key]


# ── 图片缓存 ─────────────────────────────────────────
_image_cache = {}
_cache_hits = 0
_cache_misses = 0


def _make_key(text, size, fg, bg, bold, pad_w, pad_h):
    """生成缓存键"""
    return (text, size, fg, bg, bold, pad_w, pad_h)


def _render_image(text, size=None, fg="#000000", bg=None, bold=False,
                  pad_w=4, pad_h=2, min_w=None):
    """将文字渲染为 RGBA 图片，返回 (PIL.Image, 宽度, 高度)"""
    size = size or _DEFAULT_SIZE
    font = _get_font(size, bold)
    bb = font.getbbox(text)
    tw = abs(bb[2] - bb[0])
    th = abs(bb[3] - bb[1])
    w = max(tw + pad_w * 2, min_w or 0)
    h = th + pad_h * 2

    if bg:
        img = Image.new("RGBA", (w, h), bg)
    else:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((pad_w, pad_h), text, font=font, fill=fg)
    return img, w, h


# ── 公开 API ─────────────────────────────────────────


def render_photo(text, size=None, fg="#000000", bg=None, bold=False,
                 pad_w=4, pad_h=2, min_w=None):
    """
    将文字渲染为 tkinter.PhotoImage。
    返回 (PhotoImage, 图片宽度, 图片高度)
    """
    global _cache_hits, _cache_misses
    key = _make_key(text, size, fg, bg, bold, pad_w, pad_h)
    if key in _image_cache:
        _cache_hits += 1
        return _image_cache[key]

    img, w, h = _render_image(text, size, fg, bg, bold, pad_w, pad_h, min_w)
    photo = ImageTk.PhotoImage(img)
    _image_cache[key] = (photo, w, h)
    _cache_misses += 1
    return photo, w, h


def clear_cache():
    """清空渲染缓存（字体变更或主题切换时调用）"""
    _image_cache.clear()
    global _cache_hits, _cache_misses
    _cache_hits = 0
    _cache_misses = 0


# ── 便捷控件工厂 ─────────────────────────────────────


def make_label(parent, text, size=None, fg="#000000", bg=None, bold=False,
               pad_w=4, pad_h=2, **kwargs):
    """创建一个显示中文文字的 Label（图片渲染）"""
    photo, w, h = render_photo(text, size, fg, bg, bold, pad_w, pad_h)
    lbl = tk.Label(parent, image=photo, **kwargs)
    lbl.image = photo  # 保持引用，防止 GC
    return lbl


def make_button(parent, text, command=None, width=130, height=30,
                bg="#4CAF50", fg="#FFFFFF", active_bg="#45a049", size=12,
                **kwargs):
    """
    创建一个中文按钮（可点击 Label + 图片渲染）。
    提供 hover 高亮效果。
    """
    # 正常状态
    normal_img, _, _ = _render_image(text, size, fg, bg, bold=False,
                                     pad_w=8, pad_h=4, min_w=width)
    normal_photo = ImageTk.PhotoImage(normal_img)

    # 悬停状态（稍暗背景）
    hover_bg = _darken_color(bg, 0.9)
    hover_img, _, _ = _render_image(text, size, fg, hover_bg, bold=False,
                                    pad_w=8, pad_h=4, min_w=width)
    hover_photo = ImageTk.PhotoImage(hover_img)

    lbl = tk.Label(parent, image=normal_photo, cursor="hand2", **kwargs)
    lbl.normal_img = normal_photo
    lbl.hover_img = hover_photo
    lbl.image = normal_photo

    # 事件绑定
    if command:
        lbl.bind("<Button-1>", lambda e: command())
    lbl.bind("<Enter>", lambda e: lbl.configure(image=hover_photo))
    lbl.bind("<Leave>", lambda e: lbl.configure(image=normal_photo))

    return lbl


def make_radio(parent, text, variable, value, size=None,
               fg="#000000", selected_fg="#0000CC",
               command=None, **kwargs):
    """
    创建一个中文单选钮（可点击 Label + 图片渲染）。
    选中时左侧显示 ●，未选中时显示 ○。
    """
    def _render(selected=False):
        prefix = "● " if selected else "○ "
        txt = prefix + text
        clr = selected_fg if selected else fg
        photo, w, h = render_photo(txt, size=(size or _DEFAULT_SIZE), fg=clr,
                                   pad_w=2, pad_h=2)
        return photo

    # 初始状态
    is_selected = (variable.get() == value)
    photo = _render(is_selected)

    lbl = tk.Label(parent, image=photo, cursor="hand2", anchor="w",
                   justify=tk.LEFT, **kwargs)
    lbl.photo_normal = _render(False)
    lbl.photo_selected = _render(True)
    lbl.image = photo

    def _on_click(event):
        variable.set(value)
        lbl.configure(image=lbl.photo_selected)
        if command:
            command()

    def _trace_callback(*_args):
        if variable.get() == value:
            lbl.configure(image=lbl.photo_selected)
        else:
            lbl.configure(image=lbl.photo_normal)

    variable.trace_add("write", _trace_callback)
    lbl.bind("<Button-1>", _on_click)

    return lbl


def make_option_menu(parent, items, textvariable, width=200, height=26,
                     size=None, **kwargs):
    """
    创建一个中文下拉选择器（替代 ttk.Combobox）。
    点击弹出 Toplevel 列表供选择。
    """
    size = size or _DEFAULT_SIZE

    # 显示当前选中项的 Label（空列表时显示提示）
    current_text = (textvariable.get()
                    or (items[0] if items else "无可选模板"))
    photo, _, _ = render_photo(f"▾ {current_text}", size=size, pad_w=6, pad_h=3,
                               min_w=width)
    lbl = tk.Label(parent, image=photo, cursor="hand2", **kwargs)
    lbl.image = photo

    # 弹出列表
    def _show_dropdown(event=None):
        popup = tk.Toplevel(lbl)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        x = lbl.winfo_rootx()
        y = lbl.winfo_rooty() + lbl.winfo_height()
        popup.geometry(f"+{x}+{y}")

        list_frame = tk.Frame(popup, bd=1, relief=tk.SOLID)
        list_frame.pack()

        for item in items:
            is_sel = (item == textvariable.get())
            item_photo, iw, ih = render_photo(
                f"{'● ' if is_sel else '○ '}{item}",
                size=size, pad_w=6, pad_h=3, min_w=width,
                fg="#0000CC" if is_sel else "#000000",
            )
            item_lbl = tk.Label(list_frame, image=item_photo, cursor="hand2",
                                anchor="w")
            item_lbl.image = item_photo
            item_lbl.pack(fill=tk.X)

            def _select(event, i=item, lb=item_lbl):
                textvariable.set(i)
                _update_display()
                popup.destroy()

            item_lbl.bind("<Button-1>", _select)

    def _update_display():
        txt = textvariable.get()
        photo, _, _ = render_photo(f"▾ {txt}", size=size, pad_w=6, pad_h=3,
                                   min_w=width)
        lbl.configure(image=photo)
        lbl.image = photo

    lbl.bind("<Button-1>", _show_dropdown)
    # 当外部更新变量时同步显示
    textvariable.trace_add("write", lambda *_: _update_display())

    return lbl


# ── 内部工具 ─────────────────────────────────────────


def _darken_color(hex_color, factor=0.9):
    """将十六进制颜色按 factor 调暗"""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def make_label_frame(parent, title, title_size=None, **frame_kw):
    """
    替代 tk.LabelFrame：使用 Frame + 渲染文字标题。
    返回 (frame, title_label) 元组。
    """
    frame = tk.Frame(parent, **frame_kw)
    title_photo, _, _ = render_photo(title, size=(title_size or _DEFAULT_SIZE),
                                     fg="#333333", bold=False, pad_w=4, pad_h=1)
    title_lbl = tk.Label(frame, image=title_photo, anchor="w")
    title_lbl.image = title_photo
    title_lbl.place(x=8, y=-8)  # 重叠上边框，模拟 LabelFrame 风格
    return frame, title_lbl
