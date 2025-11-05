import os

# os.path.abspath(__file__) 获取 config.py 文件的绝对路径
# os.path.dirname(...) 获取该文件所在的目录路径
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """基础配置类"""
    # 'SQLALCHEMY_DATABASE_URI': Flask-SQLAlchemy的配置项，用于指定数据库连接字符串。
    # 我们使用 SQLite，数据库文件将存放在项目根目录下的 data.sqlite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    # 关闭不必要的追踪，以优化性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-is-hard-to-guess'

    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
