from app.extensions import db
from datetime import datetime

class UserModel(db.Model):
    __tablename__ = 'user'  # 定义表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    #新增用户头像字段
    avatar = db.Column(db.String(128), nullable=True)