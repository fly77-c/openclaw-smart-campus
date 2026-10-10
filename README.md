# OpenClaw Smart Campus 🦞

> 一个跨系统的 AI 控制平台：手机 App 远程查看电脑摄像头，虚拟机里的 AI 通过自然语言控制本地 Windows 电脑执行命令。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📹 **双源视频监控** | 手机 App 支持「手机摄像头」和「电脑摄像头」双视图切换 |
| 🌐 **公网访问** | 通过 Cloudflare Tunnel，手机用流量也能看电脑摄像头 |
| 🖥️ **AI 控制电脑** | 虚拟机里的 OpenClaw AI 通过 HTTP 调用本地 Agent，执行命令、读写文件、截屏 |
| 🔒 **三层安全** | IP 白名单 + Token 验证 + 命令白名单 |
| 🎛️ **智能切换** | 工作台在线时显示「电脑视图」按钮，离线时自动隐藏 |

---

## 🏗️ 架构图

```
┌─────────────────────────────────────────────────────────┐
│                     📱 Android App                       │
│   ┌──────────────┐        ┌──────────────┐              │
│   │  手机视图     │  切换  │  电脑视图     │              │
│   │  (CameraX)   │ ←───→ │  (WebView)   │              │
│   └──────────────┘        └──────┬───────┘              │
└──────────────────────────────────┼──────────────────────┘
                                   │ HTTP
                    ┌──────────────┴──────────────┐
                    │                             │
          ┌─────────▼─────────┐         ┌─────────▼─────────┐
          │  Cloudflare Tunnel│         │  Windows Agent    │
          │  (公网访问摄像头)  │         │  (端口 5000)      │
          └─────────┬─────────┘         └─────────┬─────────┘
                    │                             │
          ┌─────────▼─────────┐         ┌─────────▼─────────┐
          │ camera_stream.py  │         │   agent.py        │
          │ (端口 5020)       │         │   main.py         │
          └─────────┬─────────┘         └─────────┬─────────┘
                    │                             │
          ┌─────────▼─────────┐         ┌─────────▼─────────┐
          │  电脑摄像头        │         │  Windows 系统命令  │
          └───────────────────┘         └───────────────────┘
                                                ▲
                                                │ HTTP
                                      ┌─────────┴─────────┐
                                      │  OpenClaw (VM)    │
                                      │  + DeepSeek AI    │
                                      └───────────────────┘
```

---

## 📁 项目结构

```
openclaw-smart-campus/
├── README.md                    # 本文件
├── LICENSE                      # MIT 协议
├── .gitignore                   # Git 忽略规则
│
├── android-app/                 # 📱 Android 客户端
│   └── app/src/main/
│       ├── java/com/example/myapplication2/
│       │   └── MonitorActivity.java   # 监控页（双视图切换）
│       └── res/layout/
│           └── activity_monitor.xml   # 横屏 3:1 布局
│
├── windows-agent/               # 🖥️ Windows 执行器
│   ├── agent/
│   │   └── agent.py             # 加固版（简单命令执行）
│   ├── core/                    # 核心模块
│   │   ├── config.py            # 配置管理
│   │   ├── security.py          # Token 认证
│   │   ├── executor.py          # 命令执行
│   │   ├── files.py             # 文件操作
│   │   ├── apps.py              # 应用启动
│   │   ├── screen.py            # 截屏
│   │   ├── processes.py         # 进程管理
│   │   ├── ai_bridge.py         # AI 算力桥
│   │   └── system.py            # 系统信息
│   ├── main.py                  # 完整版执行器（v2.0）
│   ├── camera_stream.py         # 摄像头推流
│   ├── config.json              # 配置文件
│   ├── requirements.txt         # Python 依赖
│   └── start.bat                # 启动脚本
│
└── docs/                        # 📚 文档
    ├── architecture.md          # 架构说明
    ├── deployment.md            # 部署手册
    └── security.md              # 安全说明
```

---

## 🚀 快速开始

### 前置要求

| 组件 | 要求 |
|------|------|
| Windows | 10/11 |
| Python | 3.10+ |
| Android Studio | 最新版 |
| 虚拟机 | Ubuntu 20.04+（跑 OpenClaw） |
| 手机 | Android 7.0+ |

---

### 第一步：部署 Windows Agent

```bash
# 1. 克隆仓库
git clone https://github.com/fly77-c/OpenClaw-Smart-Campus.git
cd OpenClaw-Smart-Campus/windows-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 修改配置（重要！）
# 编辑 config.json，改成你自己的：
#   - auth_token：随机字符串
#   - host：改成你的局域网 IP 或 0.0.0.0

# 4. 启动
python main.py
```

---

### 第二步：启动摄像头推流

```bash
python camera_stream.py
```

默认监听 `http://0.0.0.0:5020`。

---

### 第三步：配置 Cloudflare 隧道（公网访问）

```bash
# 安装 cloudflared
winget install Cloudflare.cloudflared

# 启动隧道（把 5020 暴露到公网）
cloudflared tunnel --url http://localhost:5020
```

会输出一个公网地址：

```
https://random-name-xxxx.trycloudflare.com
```

**复制这个地址**，手机用流量也能访问。

---

### 第四步：配置 OpenClaw（虚拟机）

```bash
# 在 Ubuntu 虚拟机里
openclaw onboard  # 选 DeepSeek
openclaw gateway start
```

---

### 第五步：编译 Android App

1. 用 **Android Studio** 打开 `android-app/`
2. 修改 `MonitorActivity.java` 里的 `STATUS_URL`：
   ```java
   private static final String STATUS_URL = "http://你的局域网IP:5000/status";
   ```
3. 编译安装到手机

---

## 📱 使用

| 操作 | 效果 |
|------|------|
| 打开 App → 监控页 | 自动显示手机摄像头 |
| 工作台在线时 | 右上角出现「电脑视图」按钮 |
| 点「电脑视图」 | 切换到电脑摄像头（输入框填公网地址） |
| 点「手机视图」 | 切回手机摄像头 |

---

## 🔒 安全说明

⚠️ **本项目仅供学习和内网使用，请勿直接暴露到公网。**

生产环境请务必：

1. **修改默认 Token**：`config.json` 里的 `auth_token` 改成 32 位随机字符串
2. **限制 IP 白名单**：只允许虚拟机 IP 访问
3. **使用 HTTPS**：Cloudflare Tunnel 自带 HTTPS
4. **加访问认证**：Cloudflare Access 或 Basic Auth
5. **定期更换 Token**

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| Android App | Java, CameraX, WebView |
| Windows Agent | Python, Flask, OpenCV |
| AI 调度 | OpenClaw, DeepSeek |
| 内网穿透 | Cloudflare Tunnel |
| 通信协议 | HTTP, RESTful, MJPEG |

---

## 📚 文档

- [架构说明](docs/architecture.md)
- [部署手册](docs/deployment.md)
- [安全说明](docs/security.md)

---

## 🤝 贡献

欢迎提 Issue 和 PR！

---

## 📄 开源协议

[MIT License](LICENSE)

---

## 🙏 致谢

- [OpenClaw](https://openclaw.ai/) - AI Agent 框架
- [DeepSeek](https://platform.deepseek.com/) - 大模型 API
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/) - 内网穿透
- [CameraX](https://developer.android.com/training/camerax) - Android 相机库

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**