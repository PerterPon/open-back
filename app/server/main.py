#!/usr/bin/env python3
"""
主 HTTP 服务器文件
负责启动 Flask 应用程序，集成配置管理器
"""

import os
import sys
from flask import Flask
from flask_cors import CORS

# 动态获取项目根目录，支持任意部署环境
current_file = os.path.abspath(__file__)
# 从 app/server/main.py 向上找到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
sys.path.insert(0, project_root)

# 调试信息（可选）
# print(f"当前文件：{current_file}")
# print(f"项目根目录：{project_root}")
# print(f"Python 路径：{sys.path[:3]}")

from core.config.index import get_config
from app.server.routes import register_routes


def create_app() -> Flask:
    """创建并配置 Flask 应用程序"""
    app = Flask(__name__)
    
    # 配置 CORS 跨域支持
    CORS(app, 
         origins="*",  # 允许所有域名跨域访问
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的 HTTP 方法
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],  # 允许的请求头
         supports_credentials=True  # 支持携带凭证
    )
    
    # 注册所有路由
    register_routes(app)
    
    return app


def main():
    """主函数，启动 HTTP 服务器"""
    try:
        # 获取配置
        config = get_config()
        server_config = config.get('server', {})
        port = server_config.get('port', 8081)
        
        # 创建应用
        app = create_app()
        
        print(f"🚀 正在启动 HTTP 服务器...")
        print(f"📡 监听端口：{port}")
        print(f"🌐 访问地址：http://localhost:{port}")
        print(f"📝 测试接口：http://localhost:{port}/test")
        print("按 Ctrl+C 停止服务器")
        
        # 启动服务器
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,  # 关闭 debug 模式以避免重启问题
            use_reloader=False  # 禁用重载器
        )
        
    except Exception as e:
        print(f"❌ 启动服务器失败：{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
