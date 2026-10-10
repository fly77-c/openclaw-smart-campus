# -*- coding: utf-8 -*-
"""
配置管理：读取与 main.py 同目录的 config.json，
缺失字段自动使用内置默认值。
"""

import os
import sys
import json

# 打包成 exe 后，以 exe 所在目录为基准（config.json 放 exe 旁边，用户可编辑）
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULTS = {
    "service_name": "OpenClaw Core Executor",
    "version": "2.0.0",
    "host": "127.0.0.1",                          # ← 改：默认只监听本地
    "port": 5010,
    "auth_token": "CHANGE_ME_to_a_random_string", # ← 改：明确的占位符
    "shell_timeout": 120,
    "openclaw": {
        "base_url": "http://127.0.0.1:18789",
        "model": "openclaw",
        "auth_token": "",
        "timeout": 120,
    },
    "allow": {
        "file_roots": [],
    },
}


def config_path():
    return os.path.join(BASE_DIR, "config.json")


def load_config():
    """加载配置（文件 + 默认值合并，文件优先）"""
    cfg = json.loads(json.dumps(DEFAULTS))  # 深拷贝
    try:
        with open(config_path(), "r", encoding="utf-8") as f:
            user = json.load(f)
        _deep_merge(cfg, user)
    except FileNotFoundError:
        # 首次运行自动生成默认配置，方便用户修改
        try:
            with open(config_path(), "w", encoding="utf-8") as f:
                json.dump(DEFAULTS, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    except Exception as e:
        print(f"⚠️ 配置文件解析失败，使用默认值: {e}")
    return cfg


def _deep_merge(base, override):
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def get_version():
    cfg = load_config()
    return cfg.get("version", DEFAULTS["version"])