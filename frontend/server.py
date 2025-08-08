#!/usr/bin/env python3
"""
Shrimp Search 前端服务器
简单的HTTP服务器用于本地开发和测试
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

class ShrimpSearchHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        # 添加CORS头部
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # 如果请求根路径，重定向到index.html
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        # 自定义日志格式
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """启动服务器"""
    PORT = 8080
    
    # 检查端口是否被占用
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', PORT)) == 0:
            print(f"端口 {PORT} 已被占用，尝试使用其他端口...")
            PORT = 8081
    
    try:
        with socketserver.TCPServer(("", PORT), ShrimpSearchHandler) as httpd:
            print("="*60)
            print("🦐 Shrimp Search 前端服务器")
            print("="*60)
            print(f"服务器地址: http://localhost:{PORT}")
            print(f"服务器目录: {Path(__file__).parent}")
            print("按 Ctrl+C 停止服务器")
            print("="*60)
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("✅ 已自动打开浏览器")
            except Exception as e:
                print(f"⚠️ 无法自动打开浏览器: {e}")
                print(f"请手动访问: http://localhost:{PORT}")
            
            print("\n🚀 服务器启动成功！")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()