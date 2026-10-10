# -*- coding: utf-8 -*-
"""
进程能力（能力五）：列出 / 结束进程
基于 tasklist / taskkill（系统自带，无需额外依赖）
"""

import subprocess
import csv
import io


def _run_raw(cmd):
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
        return proc.returncode == 0, proc.stdout
    except Exception as e:
        return False, str(e).encode("utf-8", errors="replace")


def list_all():
    """返回 (True, {count, processes:[{pid,name,mem_kb,session}]})"""
    ok, raw = _run_raw(["tasklist", "/FO", "CSV", "/NH"])
    if not ok:
        return False, raw.decode("utf-8", errors="replace")
    text = raw.decode("utf-8", errors="replace")
    procs = []
    try:
        reader = csv.reader(io.StringIO(text))
        for row in reader:
            if len(row) < 5:
                continue
            name = row[0].strip('"')
            pid = row[1].strip('"')
            mem = row[4].strip('"').replace(",", "").replace("K", "").replace(" ", "")
            try:
                mem_kb = int(mem) if mem.isdigit() else None
            except ValueError:
                mem_kb = None
            procs.append({"pid": int(pid) if pid.isdigit() else pid, "name": name,
                          "session": row[2].strip('"'), "mem_kb": mem_kb})
    except Exception as e:
        return False, f"解析进程列表失败: {e}"
    return True, {"count": len(procs), "processes": procs}


def kill(pid=None, name=None):
    """结束进程。pid 优先；name 传 exe 名（如 notepad.exe）"""
    try:
        if pid:
            proc = subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=20)
            if proc.returncode == 0:
                return True, f"已结束进程 PID {pid}"
            return False, proc.stdout.decode("utf-8", errors="replace").strip() or "结束失败"
        if name:
            proc = subprocess.run(["taskkill", "/F", "/IM", name], capture_output=True, timeout=20)
            if proc.returncode == 0:
                return True, f"已结束进程: {name}"
            return False, proc.stdout.decode("utf-8", errors="replace").strip() or "结束失败（进程可能不存在或无权限）"
        return False, "需要 pid 或 name"
    except Exception as e:
        return False, f"结束进程异常: {e}"
