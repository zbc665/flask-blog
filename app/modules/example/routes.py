# app/modules/example/routes.py
import os
from flask import request, g, current_app, send_from_directory
from sqlalchemy.orm import joinedload # 用于优化关联查询
from sqlalchemy import or_ # 用于实现 OR 条件查询

# 导入蓝图对象
from . import example
# 导入数据库模型
from .models import ExampleCategory, ExampleItem
from app.modules.auth.models import UserModel
# 导入数据库会话和扩展
from app.extensions import db
# 导入自定义装饰器、异常和响应处理器
from app.utils.decorators import login_required, permission_required
from app.utils.exception_handler import APIException
from app.utils.response_handler import SuccessResponse

# === 分类接口 (Category Routes) ===

@example.route('/category/create', methods=['POST'])
@login_required # 演示：需要登录才能创建分类
def create_category():
    """
    [C] Create: 创建一个新的示例分类
    """
    data = request.get_json()
    name = data.get('name')

    if not name:
        raise APIException("分类名称不能为空", status_code=400)
    
    # 检查分类名是否已存在
    if ExampleCategory.query.filter_by(name=name).first():
        raise APIException("分类名称已存在", status_code=400)
    
    new_category = ExampleCategory(name=name)
    db.session.add(new_category)
    db.session.commit()
    
    return SuccessResponse(
        message="分类创建成功", 
        data={'id': new_category.id, 'name': new_category.name}
    )

@example.route('/category/list', methods=['GET'])
def list_categories():
    """
    [R] Read: 获取所有示例分类的列表
    """
    categories = ExampleCategory.query.all()
    
    # 将分类列表转换为字典列表
    category_list = [
        {'id': category.id, 'name': category.name,"items":category.items.count()} 
        for category in categories
    ]
    
    return SuccessResponse(data=category_list, message="分类列表获取成功")

# === 示例项目接口 (Item Routes) ===

@example.route('/item/create', methods=['POST'])
@login_required # 必须登录才能创建
def create_item():
    """
    [C] Create: 创建一个新的示例项目
    """
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    category_id = data.get('category_id')
    
    if not name or not category_id:
        raise APIException("项目名称和分类ID均不能为空", status_code=400)
        
    # 验证分类是否存在
    category = ExampleCategory.query.get(category_id)
    if not category:
        raise APIException("指定的分类不存在", status_code=404)
    
    # 创建新项目，并关联当前登录的用户 (g.user 由 @login_required 装饰器提供)
    new_item = ExampleItem(
        name=name,
        description=description,
        category_id=category_id,
        user_id=g.user.id  # 关联创建者
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    # 使用 to_dict() 辅助方法返回新创建的项目数据
    return SuccessResponse(data=new_item.to_dict(), message="项目创建成功")


@example.route('/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """
    [R] Read: 获取单个示例项目的详细信息
    演示：关联查询
    """
    # .options(joinedload(...)) 是一个查询优化
    # 它告诉 SQLAlchemy 在同一次查询中（使用 JOIN）同时加载 author 和 category
    # 这样可以避免后续访问 item.author 或 item.category 时触发额外的 N+1 查询
    item = ExampleItem.query.options(
        joinedload(ExampleItem.author),
        joinedload(ExampleItem.category)
    ).get(item_id)
    
    if not item:
        raise APIException("项目不存在", status_code=404)
        
    # 使用 to_dict() 辅助方法返回包含关联数据的项目详情
    return SuccessResponse(data=item.to_dict(), message="项目详情获取成功")

@example.route('/item/update', methods=['POST'])
@login_required
@permission_required(ExampleItem) # <-- 使用权限装饰器
def update_item():
    """
    [U] Update: 更新一个已存在的示例项目
    演示：使用装饰器进行权限检查
    """
    data = request.get_json()
    # 经过 @permission_required 装饰器后, item 对象已经存在于 g.resource 中
    item = g.resource
        
    # 更新数据 (只更新传入的字段)
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']
    if 'category_id' in data:
        # 检查新分类是否存在
        if not ExampleCategory.query.get(data['category_id']):
            raise APIException("指定的新分类不存在", status_code=404)
        item.category_id = data['category_id']
        
    db.session.commit()
    
    return SuccessResponse(data=item.to_dict(), message="项目更新成功")

@example.route('/item/delete', methods=['POST'])
@login_required
@permission_required(ExampleItem)
def delete_item():
    """
    [D] Delete: 删除一个示例项目
    演示：使用装饰器进行权限检查
    """
    # 经过 @permission_required 装饰器后, item 对象已经存在于 g.resource 中
    item = g.resource
        
    db.session.delete(item)
    db.session.commit()
    
    return SuccessResponse(message="项目删除成功")


@example.route('/item/list', methods=['GET'])
def list_items():
    """
    [R] Read: 获取示例项目列表（带分页、搜索、过滤）
    演示：分页、搜索、多条件过滤、关联查询优化
    """
    # 1. 获取分页参数
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
    except TypeError:
        raise APIException('分页参数格式不正确', status_code=400)
    
    # 2. 获取过滤和搜索参数
    search_keyword = request.args.get('search', '', type=str)
    category_id = request.args.get('category_id', None, type=int)
    user_id = request.args.get('user_id', None, type=int)

    # 3. 构建基础查询
    #    使用 joinedload 优化，一次性加载 author 和 category
    base_query = ExampleItem.query.options(
        joinedload(ExampleItem.author),
        joinedload(ExampleItem.category)
    )
    # 4. 应用过滤条件
    if search_keyword:
        # 演示: 搜索名称或描述
        base_query = base_query.filter(
            or_(
                ExampleItem.name.like(f'%{search_keyword}%'),
                ExampleItem.description.like(f'%{search_keyword}%')
            )
        )
        
    if category_id:
        # 演示: 按分类ID过滤
        base_query = base_query.filter(ExampleItem.category_id == category_id)
        
    if user_id:
        # 演示: 按用户ID过滤
        base_query = base_query.filter(ExampleItem.user_id == user_id)

    # 5. 应用排序（例如按时间戳降序）
    base_query = base_query.order_by(ExampleItem.timestamp.desc())

    # 6. 执行分页查询
    pagination = base_query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # 7. 格式化查询结果
    items_list = [item.to_dict() for item in pagination.items]
    
    # 8. 组装分页元数据
    pagination_data = {
        'total_pages': pagination.pages,   # 总页数
        'current_page': pagination.page,  # 当前页码
        'per_page': pagination.per_page,   # 每页数量
        'total_count': pagination.total,   # 总条目数
        'has_next': pagination.has_next,   # 是否有下一页
        'has_prev': pagination.has_prev,   # 是否有上一页
    }
    
    # 9. 组合返回数据
    response_data = {
        'list': items_list,
        'pagination': pagination_data
    }
    
    return SuccessResponse(data=response_data, message="项目列表获取成功")

# === 文件上传接口 (File Upload Routes) ===

@example.route('/item/upload-file', methods=['POST'])
@login_required
def upload_item_file():
    """
    演示：文件上传
    为某个已存在的 Item 上传一个文件
    """
    # 文件上传通常使用 'multipart/form-data'
    # 'item_id' 存在 request.form 中
    item_id = request.form.get('item_id')
    # 'file' 存在 request.files 中
    file_obj = request.files.get('file')
    
    if not item_id or not file_obj:
        raise APIException("必须提供 item_id 和 file", status_code=400)
    
    item = ExampleItem.query.get(item_id)
    if not item:
        raise APIException("项目不存在", status_code=404)
        
    # 权限检查：必须是项目所有者
    if item.user_id != g.user.id:
        raise APIException("权限不足，无法为他人的项目上传文件", status_code=403)

    # --- 文件保存逻辑 (类似 auth/routes.py 中的 upload-avatar) ---
    
    # 1. 检查文件扩展名
    original_filename = file_obj.filename
    _, ext = os.path.splitext(original_filename)
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt']
    if ext.lower() not in allowed_extensions:
        raise APIException(f"不支持的文件格式，仅支持: {', '.join(allowed_extensions)}", status_code=400)
    
    # 2. 准备保存路径和新文件名
    upload_dir = current_app.config['UPLOAD_FOLDER']
    # 创建一个唯一的文件名，例如: example_item_1_user_2_file.pdf
    new_filename = f"example_item_{item.id}_user_{g.user.id}_file{ext}"
    save_path = os.path.join(upload_dir, new_filename)

    # 3. 保存文件
    file_obj.save(save_path)
    
    # 4. 生成文件的访问 URL (假设部署在 127.0.0.1:5000)
    #    注意: '/api/example' 是蓝图前缀, '/uploads/...' 是此路由
    file_url = f'http://127.0.0.1:5000/api/example/uploads/{new_filename}'

    # 5. 更新数据库中的 file_url 字段
    item.file_url = file_url
    db.session.commit()
    
    return SuccessResponse(
        message="文件上传成功",
        data={'file_url': file_url, 'item_id': item.id}
    )

@example.route('/uploads/<path:filename>')
def serve_example_file(filename):
    """
    提供对上传文件的公开访问
    """
    # 从配置的 UPLOAD_FOLDER 目录中安全地提供文件
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
