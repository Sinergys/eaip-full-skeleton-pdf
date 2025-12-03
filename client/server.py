#!/usr/bin/env python3
"""
Простой HTTP сервер для обслуживания HTML интерфейса загрузки файлов
Запуск: python server.py
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Добавляем CORS заголовки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Улучшенное логирование
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/upload.html"
        print("=" * 60)
        print("🌐 HTTP сервер запущен!")
        print("=" * 60)
        print("📤 Интерфейс загрузки файлов:")
        print(f"   {url}")
        print("")
        print("📚 Другие интерфейсы:")
        print("   Swagger UI: http://localhost:8001/docs")
        print("   Grafana: http://localhost:3000")
        print("")
        print("⚠️  Нажмите Ctrl+C для остановки сервера")
        print("=" * 60)
        
        # Автоматически открыть браузер
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️  Не удалось открыть браузер: {e}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Сервер остановлен")

if __name__ == "__main__":
    main()

