#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 本地执行器（Windows Agent）— 加固版
只允许特定 IP 访问，Token 验证，命令白名单

⚠️ 使用前请修改下面「配置区域」的内容
"""

from flask import Flask, request, jsonify
import subprocess
import logging
import sys
from datetime import datetime

# ========== 配置区域（请根据你的环境修改） ==========
PORT = 5000

# 安全令牌：改成你自己的随机字符串（建议 32 位以上）
AUTH_TOKEN = "your-secret-token-here"

# IP 白名单：只允许这些 IP 访问（虚拟机 + 手机）
ALLOWED_IPS = [
    "192.168.1.100",   # 虚拟机 IP（改成你自己的）
    "192.168.1.101",   # 手机 IP（改成你自己的）
]

# 命令白名单：只允许执行这些命令
ALLOWED_COMMANDS = [
    "calc", "notepad", "explorer", "echo", "dir", "type",
    "start", "tasklist", "ipconfig", "whoami", "hostname"
]

# 监听地址：宿主机在 VMware 虚拟网卡上的 IP（改成你自己的）
LISTEN_HOST = "192.168.1.1"
# =================================================

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@app.before_request
def check_ip():
    """IP 白名单检查（在最前面拦截）"""
    client_ip = request.remote_addr
    if client_ip not in ALLOWED_IPS:
        logger.warning(f"🚫 拒绝未授权 IP: {client_ip}")
        return jsonify({'error': 'IP 不在白名单中'}), 403


@app.route('/exec', methods=['POST'])
def execute_command():
    """执行命令接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的 JSON 请求'}), 400

        # Token 验证
        token = data.get('token', '')
        if token != AUTH_TOKEN:
            logger.warning(f"❌ Token 错误，IP: {request.remote_addr}")
            return jsonify({'error': '未授权访问'}), 401

        cmd = data.get('cmd', '').strip()
        if not cmd:
            return jsonify({'error': '命令不能为空'}), 400

        # 命令白名单检查
        cmd_name = cmd.split()[0].lower() if cmd.split() else ''
        if cmd_name not in ALLOWED_COMMANDS:
            logger.warning(f"🚫 命令不在白名单: {cmd_name}")
            return jsonify({'error': f'命令 "{cmd_name}" 不在白名单中'}), 403

        logger.info(f"📥 执行命令: {cmd} (来源: {request.remote_addr})")

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            encoding='gbk', timeout=60
        )

        response = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'code': result.returncode
        }

        if result.returncode != 0:
            logger.warning(f"⚠️ 命令异常退出码: {result.returncode}")
        else:
            logger.info(f"✅ 命令执行成功")

        return jsonify(response)

    except subprocess.TimeoutExpired:
        logger.error("⏰ 命令执行超时")
        return jsonify({'error': '命令执行超时'}), 408
    except Exception as e:
        logger.error(f"❌ 执行异常: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'online',
        'version': '1.1.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'OpenClaw Windows Agent (Hardened)',
        'endpoints': {
            '/exec': 'POST - 执行命令',
            '/health': 'GET - 健康检查'
        }
    })


if __name__ == '__main__':
    if sys.platform != 'win32':
        logger.warning("⚠️ 此程序专为 Windows 设计")

    # 启动前检查：是否还是默认 Token
    if AUTH_TOKEN == "your-secret-token-here":
        logger.error("❌ 请先修改 AUTH_TOKEN！")
        sys.exit(1)

    logger.info("=" * 50)
    logger.info("🚀 OpenClaw Windows Agent (加固版) 启动中...")
    logger.info(f"📡 监听端口: {PORT}")
    logger.info(f"🔑 Token: {AUTH_TOKEN[:6]}...")
    logger.info(f"🛡️ 允许 IP: {ALLOWED_IPS}")
    logger.info(f"📋 命令白名单: {ALLOWED_COMMANDS}")
    logger.info("=" * 50)

    try:
        app.run(host=LISTEN_HOST, port=PORT, debug=False, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ 端口 {PORT} 被占用")
        else:
            raise
    except KeyboardInterrupt:
        logger.info("🛑 服务已停止")