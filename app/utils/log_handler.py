# app/utils/log_handler.py

import logging
from logging.handlers import RotatingFileHandler
import os

def register_logging(app):
    # 1. 创建 logs 文件夹
    log_dir = os.path.join(app.root_path, '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. 定义日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    )

    # 3. 创建文件处理器 (带轮转功能)
    log_path = os.path.join(log_dir, 'app.log')
    # maxBytes: 单个文件最大 5MB, backupCount: 保留最近 10 个文件
    file_handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=10)
    file_handler.setFormatter(formatter)

    # 4. 创建控制台处理器
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # 5. 从 app.logger 中移除默认的处理器，并添加我们自己的
    del app.logger.handlers[:]
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
