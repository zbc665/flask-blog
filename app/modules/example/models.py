# app/modules/example/models.py
from app.extensions import db
from datetime import datetime
# 导入 UserModel，用于建立外键关联
from app.modules.auth.models import UserModel 

"""
示例模块的数据库模型定义
我们将创建两个模型：
1. ExampleCategory: 示例分类（演示一对多关系中的 "一"）
2. ExampleItem: 示例项目（演示一对多关系中的 "多"）

关系：
- 一个 User (用户) 可以拥有多个 ExampleItem (示例项目) [一对多]
- 一个 ExampleCategory (分类) 可以包含多个 ExampleItem (示例项目) [一对多]
"""

class ExampleCategory(db.Model):
    """
    示例分类模型
    """
    __tablename__ = 'example_category' # 定义表名
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # 定义关系：一个 Category 有多个 Item
    # 'items' 是反向引用的名称，允许我们通过 category.items 访问所有关联的 ExampleItem
    # lazy='dynamic' 表示关联的对象（items）将作为查询对象返回，而不是直接加载，这在大数据量时更高效
    items = db.relationship('ExampleItem', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<ExampleCategory {self.name}>'

class ExampleItem(db.Model):
    """
    示例项目模型
    """
    __tablename__ = 'example_item' # 定义表名
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    
    # 用于演示文件上传，存储文件的访问 URL
    file_url = db.Column(db.String(255), nullable=True)
    
    # --- 外键定义 ---
    
    # 关联到 ExampleCategory (分类)
    category_id = db.Column(db.Integer, db.ForeignKey('example_category.id'), nullable=False)
    # backref 会自动生成另一侧属性，所以不需要再定义 category 关系
    # category =   db.relationship('ExampleCategory', backref=db.backref('items', lazy='dynamic'))
    
    # 关联到 User (用户)
    #    db.ForeignKey('user.id') 'user' 是表名, 'id' 是 user 表的主键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # --- 关系定义 ---
    # 'author' 是反向引用的名称，允许我们通过 item.author 访问关联的 UserModel
    # 我们在 UserModel 中并没有定义 db.relationship，所以这里的 backref='example_items' 会在 UserModel 上动态添加一个 'example_items' 属性
    # 这样我们就可以通过 user.example_items 访问该用户所有的 ExampleItem
    author = db.relationship('UserModel', backref=db.backref('example_items', lazy='dynamic'))

    def to_dict(self):
        """
        辅助方法：将模型对象转换为字典，方便 API 返回
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(), # 转换为 ISO 格式字符串
            'file_url': self.file_url,
            'user_id': self.user_id,
            'category_id': self.category_id,
            # 演示如何从关系中获取数据
            'author_username': self.author.username if self.author else '未知用户',
            'category_name': self.category.name if self.category else '未分类'
        }

    def __repr__(self):
        return f'<ExampleItem {self.name}>'
