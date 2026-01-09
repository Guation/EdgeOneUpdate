#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"

import json, threading, time
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from .edgeone_api import update_record
from logging import debug, info, warning, error

class Config:
    ip = "8.8.8.8"
    port = 80
    update_time = 0
    timer = threading.Timer(0, time.sleep, (0,))

class JSONRequestHandler(http.server.BaseHTTPRequestHandler):
    def __update(self, count):
        debug("ip=%s, port=%s", Config.ip, Config.port)
        try:
            update_record(Config.ip, Config.port)
        except ValueError:
            if count > 0:
                error("更新错误，60s后重试", stack_info=True)
                Config.timer = threading.Timer(60, self.__update, (count - 1,))
                Config.timer.start()
            else:
                error("更新错误", stack_info=True)

    def _update(self):
        Config.timer.cancel()
        Config.timer = threading.Timer(30, self.__update, (10,))
        Config.timer.start()

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        self._set_headers(200)
        self.wfile.write("https://github.com/Guation/EdgeOneUpdate".encode('utf-8'))
    
    def do_POST(self):
        # parsed_path = urlparse(self.path)
        content_type = self.headers.get('Content-Type', '')
        if content_type != 'application/json':
            self._set_headers(400)
            response = {
                "error": "无效的内容类型，请使用application/json",
                "status": "error"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            debug(json_data)
            if json_data["type"] == "A":
                Config.ip = json_data["data"]
                self._update()
            elif json_data["type"] == "SRV":
                Config.port = json_data["port"]
                self._update()
            response = {
                "error": "",
                "status": "success"
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except json.JSONDecodeError:
            self._set_headers(400)
            response = {
                "error": "无效的JSON数据",
                "status": "error"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(ip: str, port: int):
    with socketserver.TCPServer((ip, port), JSONRequestHandler) as httpd:
        info(f"服务器运行在 http://{ip}:{port}")
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            info("服务器已停止")
