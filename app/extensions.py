from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 这里只进行实例化，不传入 app 对象
# app 对象将在工厂函数中与这些实例绑定
db = SQLAlchemy()
migrate = Migrate()