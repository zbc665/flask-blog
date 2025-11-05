# app/modules/__init__.py

def register_blueprints(app):
    """
    一个用于集中注册所有模块蓝图的函数。
    当有新模块时，只需在这里导入并注册即可。
    :param app: Flask app 对象
    """
    # 从各个模块中导入蓝图对象
    from .auth import auth
    # --- 新增 ---
    from .example import example
    # --- 结束 ---
    
    # 假设未来有 message 模块
    # from .message import message

    # 将蓝图注册到 app，并指定 URL 前缀
    app.register_blueprint(auth, url_prefix='/api/auth')
    # --- 新增 ---
    app.register_blueprint(example, url_prefix='/api/example')
    # --- 结束 ---
    
    # app.register_blueprint(message, url_prefix='/api/message')
