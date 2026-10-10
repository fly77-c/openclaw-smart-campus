# -*- coding: utf-8 -*-
"""
安全认证：Token 校验装饰器。

Token 来源（任选其一）：
  1. JSON body:  {"token": "..."}
  2. Header:     X-Auth-Token: ...
  3. Header:     Authorization: Bearer ...
"""

import hmac
from functools import wraps

from flask import request, jsonify, current_app


def _check(token, expected):
    """恒定时间比较，防时序攻击"""
    if not token or not expected:
        return False
    return hmac.compare_digest(token.encode("utf-8"), expected.encode("utf-8"))


def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        cfg = current_app.config.get("EXEC_CFG", {})
        expected = cfg.get("auth_token", "")

        # 1. body
        body_token = None
        try:
            body_token = (request.get_json(silent=True) or {}).get("token")
        except Exception:
            pass
        # 2. header X-Auth-Token
        header_token = request.headers.get("X-Auth-Token")
        # 3. Authorization: Bearer xxx
        authz = request.headers.get("Authorization", "")
        bearer = authz[7:].strip() if authz.startswith("Bearer ") else None

        token = body_token or header_token or bearer
        if not _check(token, expected):
            current_app.logger.warning("❌ 未授权访问尝试 IP: %s", request.remote_addr)
            return jsonify({"error": "未授权访问，Token 错误"}), 401
        return fn(*args, **kwargs)
    return wrapper
