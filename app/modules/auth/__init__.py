# app/modules/auth/__init__.py
from flask import Blueprint

# 1. 创建蓝图对象
auth = Blueprint('auth', __name__)

# 2. 导入 routes 文件，这样在创建蓝图时，相关的路由就会被注册
#    这个导入必须在蓝图创建之后，以避免循环导入的问题
from . import routes
