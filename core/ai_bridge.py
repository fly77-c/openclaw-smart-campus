# -*- coding: utf-8 -*-
"""
AI 桥：借用 OpenClaw 的算力
--------------------------------
Windows 本地程序通过 SSH 隧道访问虚拟机里的 OpenClaw gateway，
调用其 OpenAI 兼容接口 /v1/chat/completions 完成：
  - 智能问答 / 代码生成 / 日志分析 / 任务规划 等

前置条件（见 README）：
 # SSH 隧道:  ssh -L 18789:127.0.0.1:18789 user@YOUR_VM_IP
  2. VM 上已启用 gateway 的 chatCompletions 端点：
     openclaw config set gateway.http.endpoints.chatCompletions.enabled true
"""

import requests


class AIBridge:
    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.base_url = (cfg.get("base_url") or "http://127.0.0.1:18789").rstrip("/")
        self.model = cfg.get("model") or "openclaw"   # "openclaw" = 默认 agent
        self.auth_token = cfg.get("auth_token") or ""
        self.timeout = int(cfg.get("timeout") or 120)

    # ---------- 内部 ----------
    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.auth_token:
            h["Authorization"] = f"Bearer {self.auth_token}"
        return h

    def _chat(self, messages, model=None, temperature=0.7):
        """调用 OpenAI 兼容端点，返回 (ok, reply_or_error)"""
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        except requests.exceptions.ConnectionError:
            return False, "无法连接 OpenClaw gateway：请确认 SSH 隧道已建立（ssh -L 18789:127.0.0.1:18789 pan@192.168.88.130）"
        except requests.exceptions.Timeout:
            return False, f"请求 OpenClaw 超时（{self.timeout}s）"
        except Exception as e:
            return False, f"请求异常: {e}"

        if resp.status_code == 404:
            return False, ("OpenClaw 的 chatCompletions 端点未启用。请在 VM 上执行：\n"
                           "  openclaw config set gateway.http.endpoints.chatCompletions.enabled true\n"
                           "  openclaw gateway restart")
        if resp.status_code == 401:
            return False, "OpenClaw 认证失败：config.json 中 openclaw.auth_token 需与 gateway 认证一致"
        if resp.status_code != 200:
            return False, f"OpenClaw 返回 HTTP {resp.status_code}: {resp.text[:300]}"

        try:
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            return True, reply
        except Exception as e:
            return False, f"解析 OpenClaw 响应失败: {e}"

    # ---------- 对外 ----------
    def ask(self, prompt, system=None, model=None):
        """单轮问答。返回 (ok, reply_or_error)"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self._chat(messages, model=model)

    def chat(self, messages, model=None):
        """多轮对话（调用方维护 messages 历史）"""
        return self._chat(messages, model=model)

    def status(self):
        """连通性自检：gateway 可达性 + chatCompletions 是否启用"""
        out = {
            "base_url": self.base_url,
            "model": self.model,
            "gateway_reachable": False,
            "chat_completions_enabled": False,
            "detail": "",
        }
        try:
            r = requests.get(f"{self.base_url}/", timeout=5)
            out["gateway_reachable"] = r.status_code == 200
        except Exception:
            out["detail"] = "SSH 隧道未建立或 gateway 未启动"
            return out
        # 轻量探测：GET /v1/models 在端点启用时返回 JSON（不触发 agent 冷启动）
        try:
            r = requests.get(f"{self.base_url}/v1/models", timeout=8)
            ctype = r.headers.get("Content-Type", "")
            if r.status_code == 200 and "application/json" in ctype:
                out["chat_completions_enabled"] = True
            else:
                out["detail"] = "chatCompletions 端点未启用（见 README 开启步骤）"
        except Exception as e:
            out["detail"] = f"探测异常: {e}"
        return out
