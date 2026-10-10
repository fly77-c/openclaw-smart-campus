#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 电脑摄像头推流服务
手机浏览器访问 http://电脑IP:5020 即可看到实时画面
"""

from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

# 打开电脑摄像头（0 = 默认摄像头）
camera = cv2.VideoCapture(0)

def generate_frames():
    """生成 MJPEG 视频流"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """手机访问的页面"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>电脑摄像头</title>
        <style>
            body { margin: 0; background: #1A1A1A; display: flex;
                   justify-content: center; align-items: center;
                   min-height: 100vh; flex-direction: column; }
            h2 { color: #4CAF50; font-family: sans-serif; }
            img { max-width: 100%; border-radius: 8px;
                  box-shadow: 0 0 20px rgba(33,150,243,0.5); }
        </style>
    </head>
    <body>
        <h2>📹 电脑摄像头实时画面</h2>
        <img src="/video_feed" />
    </body>
    </html>
    ''')

@app.route('/video_feed')
def video_feed():
    """视频流接口"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("🚀 摄像头推流服务启动中...")
    print("📱 本机访问：http://127.0.0.1:5020")
    print("📱 局域网访问：http://你的电脑IP:5020")
    app.run(host='0.0.0.0', port=5020, threaded=True)