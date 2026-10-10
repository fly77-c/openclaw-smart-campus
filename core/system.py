# -*- coding: utf-8 -*-
"""
系统信息：主机名 / 系统 / Python / 用户 / 简要网络
"""

import os
import sys
import platform
import socket


def info():
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"
    return {
        "hostname": hostname,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "",
        "computer": os.environ.get("COMPUTERNAME") or "",
        "cwd": os.getcwd(),
    }
