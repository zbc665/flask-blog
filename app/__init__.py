# app/__init__.py (最终完整代码)

from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, migrate
from app.modules.auth.models import UserModel

# 导入集中注册蓝图的函数
from .modules import register_blueprints

# 导入我们创建的所有工具函数
from .utils.exception_handler import init_error_handlers
from .utils.log_handler import register_logging
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. 首先初始化日志系统
    register_logging(app)
    
    # 2. 然后注册全局异常处理器
    init_error_handlers(app)

    # 3. 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # --- 新增：确保上传文件夹存在 ---
    # 从配置中读取 UPLOAD_FOLDER 的路径
    upload_folder = app.config['UPLOAD_FOLDER']
    
    # 检查路径是否存在
    if not os.path.exists(upload_folder):
        # 如果不存在，则创建这个文件夹
        os.makedirs(upload_folder)
    # --- 结束 ---

    # 使用集中注册蓝图的函数
    register_blueprints(app)


    CORS(app,supports_credentials=True)
    return app
