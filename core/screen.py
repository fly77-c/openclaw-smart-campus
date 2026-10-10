# -*- coding: utf-8 -*-
"""
截屏能力（能力四）：让虚拟机里的 AI 能"看"电脑屏幕
依赖：Pillow（pip install pillow），全屏/多显示器捕获
返回 PNG/JPEG 的 base64，由调用方决定如何展示
"""

import io
import base64


def capture(fmt="png"):
    """
    截取当前屏幕。fmt: png | jpeg
    返回 (True, {image_base64, format, size, width, height})
    """
    try:
        from PIL import ImageGrab
    except ImportError:
        return False, "缺少 Pillow 库，请先执行: pip install pillow"
    try:
        img = ImageGrab.grab(all_screens=True)
        buf = io.BytesIO()
        if fmt == "jpeg":
            img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=80)
        else:
            img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        w, h = img.size
        return True, {
            "image_base64": b64,
            "format": fmt,
            "width": w,
            "height": h,
            "size_bytes": len(buf.getvalue()),
        }
    except Exception as e:
        return False, f"截屏失败: {e}"
