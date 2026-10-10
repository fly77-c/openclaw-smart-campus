# -*- coding: utf-8 -*-
"""
Shell 命令执行（能力一）
- 兼容 Windows cmd（GBK 输出）与 PowerShell
- 输出字节流自动解码：UTF-8 -> GBK -> 兜底替换
"""

import subprocess


def smart_decode(raw):
    """bytes -> str，自动适配 Windows 中文编码"""
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def run(cmd, timeout=120, cwd=None, shell_choice="cmd"):
    """
    执行命令。
    shell_choice: "cmd" | "powershell"
    返回统一结构：{success, code, stdout, stderr} 或 {success:False, error}
    """
    try:
        if shell_choice == "powershell":
            full = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
            proc = subprocess.run(full, capture_output=True, cwd=cwd, timeout=timeout)
        else:
            proc = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, timeout=timeout)

        return {
            "success": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": smart_decode(proc.stdout),
            "stderr": smart_decode(proc.stderr),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"命令执行超时（>{timeout}s），已终止", "code": None}
    except Exception as e:
        return {"success": False, "error": f"执行异常: {e}", "code": None}
