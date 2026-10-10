# -*- coding: utf-8 -*-
"""
文件能力（能力二）：读 / 写 / 列目录 / 删除
- 自动编码探测：读文件时先试 UTF-8，再试 GBK（Windows 常见）
- 支持二进制（content_b64）
"""

import os
import base64


def _resolve(path):
    """展开用户目录符号，返回绝对路径"""
    return os.path.abspath(os.path.expanduser(path))


def read(path, encoding=None):
    """读文件。文本返回 {content, encoding, size}；失败返回 (False, err)"""
    try:
        p = _resolve(path)
        if not os.path.exists(p):
            return False, f"文件不存在: {path}"
        with open(p, "rb") as f:
            raw = f.read()
        if encoding == "base64":
            return True, {"content_b64": base64.b64encode(raw).decode(), "encoding": "base64", "size": len(raw)}
        # 文本：自动探测编码
        used = encoding
        if not used:
            for enc in ("utf-8", "gbk"):
                try:
                    raw.decode(enc)
                    used = enc
                    break
                except UnicodeDecodeError:
                    continue
            if not used:
                used = "latin-1"
        text = raw.decode(used, errors="replace")
        return True, {"content": text, "encoding": used, "size": len(raw)}
    except Exception as e:
        return False, f"读取失败: {e}"


def write(path, content=None, content_b64=None, encoding="utf-8", append=False):
    """写文件。content_b64 优先（二进制场景）。返回 (True, None) 或 (False, err)"""
    try:
        p = _resolve(path)
        d = os.path.dirname(p)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        mode = "ab" if append else "wb"
        if content_b64:
            raw = base64.b64decode(content_b64)
        else:
            if content is None:
                return False, "需要提供 content 或 content_b64"
            raw = content.encode(encoding if encoding != "base64" else "utf-8")
        with open(p, mode) as f:
            f.write(raw)
        return True, None
    except Exception as e:
        return False, f"写入失败: {e}"


def list_dir(path):
    """列目录。返回 {path, entries:[{name, type, size, mtime}]}"""
    try:
        p = _resolve(path)
        if not os.path.isdir(p):
            return False, f"目录不存在: {path}"
        entries = []
        for name in sorted(os.listdir(p)):
            fp = os.path.join(p, name)
            try:
                st = os.stat(fp)
                entries.append({
                    "name": name,
                    "type": "dir" if os.path.isdir(fp) else "file",
                    "size": st.st_size if os.path.isfile(fp) else None,
                    "mtime": st.st_mtime,
                })
            except OSError:
                continue
        return True, {"path": p, "count": len(entries), "entries": entries}
    except Exception as e:
        return False, f"列目录失败: {e}"


def delete(path, recursive=False):
    """删除文件或目录。目录需 recursive=True"""
    try:
        p = _resolve(path)
        if not os.path.exists(p):
            return False, f"路径不存在: {path}"
        if os.path.isdir(p):
            if not recursive:
                return False, "目标是目录，删除需 recursive=true"
            import shutil
            shutil.rmtree(p)
        else:
            os.remove(p)
        return True, None
    except Exception as e:
        return False, f"删除失败: {e}"
