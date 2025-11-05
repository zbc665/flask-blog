# app/modules/example/__init__.py
from flask import Blueprint

# 1. 创建一个名为 'example' 的蓝图对象
#    '__name__' 是必须的参数，Flask 用它来定位模块
example = Blueprint('example', __name__)

# 2. 导入 routes 文件
#    这行代码必须放在蓝图创建之后，以防止循环导入
#    当 app 注册这个蓝图时，routes.py 中定义的路由就会被加载
from . import routes
