# -*- coding: utf-8 -*-
"""
应用启动能力（能力三）
查找策略（按优先级）：
  1. 直接给定完整路径
  2. PATH / 注册表 App Paths（交给 shell 的 start 解析）
  3. 常见安装目录扫描（可选 name 匹配）
"""

import os
import subprocess
import glob

COMMON_ROOTS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
    os.path.expandvars(r"%LOCALAPPDATA%\Kingsoft"),
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    os.path.expanduser(r"~\AppData\Local"),
    os.path.expanduser(r"~\Desktop"),
]


def _find_by_name(name):
    """在常见根目录下按 exe 文件名模糊查找"""
    exe = name if name.lower().endswith(".exe") else name + ".exe"
    hits = []
    for root in COMMON_ROOTS:
        if not os.path.isdir(root):
            continue
        # 深度 3 以内查找，避免太慢
        for depth_root in _walk_depth(root, 3):
            for p in glob.glob(os.path.join(depth_root, exe)):
                hits.append(p)
                break  # 每个目录只取一个
        if hits:
            break
    return hits[:1]


def _walk_depth(root, max_depth):
    """产出 root 下深度 <= max_depth 的目录"""
    yield root
    if max_depth <= 0:
        return
    try:
        for entry in os.listdir(root):
            full = os.path.join(root, entry)
            if os.path.isdir(full):
                yield from _walk_depth(full, max_depth - 1)
    except OSError:
        pass


def launch(name=None, path=None, args=""):
    """
    启动程序（异步，不阻塞）。
    返回 (True, detail) 或 (False, err)
    """
    try:
        if path:
            target = os.path.expandvars(os.path.expanduser(path))
            if not os.path.exists(target):
                return False, f"路径不存在: {path}"
        elif name:
            # 1) 若带路径则直接用
            if os.path.sep in name or "/" in name:
                target = os.path.expandvars(os.path.expanduser(name))
            else:
                # 2) 常见目录查找
                found = _find_by_name(name)
                if found:
                    target = found[0]
                else:
                    # 3) 交给 shell start（解析 PATH / App Paths / 注册表）
                    subprocess.Popen(f'start "" "{name}" {args}', shell=True)
                    return True, f"已通过系统解析启动: {name}（若未弹出，请提供完整路径）"
        else:
            return False, "需要 name 或 path"

        cmd = f'start "" "{target}"'
        if args:
            cmd += f" {args}"
        subprocess.Popen(cmd, shell=True)
        return True, f"已启动: {target}"
    except Exception as e:
        return False, f"启动失败: {e}"
