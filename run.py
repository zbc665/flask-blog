from app import create_app

# 调用工厂函数，创建 app 实例
app = create_app()

# 这个文件是 FLASK_APP 环境变量指向的文件
# 当我们运行 `flask run` 时，Flask 会从这里找到 app 对象