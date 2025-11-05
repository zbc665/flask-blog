# app/auth.py
from flask import Blueprint, request, jsonify, session,current_app,send_from_directory,g
from werkzeug.security import generate_password_hash, check_password_hash
from .models import UserModel
from app.extensions import db
from app.utils.exception_handler import APIException # <-- 导入自定义异常
from app.utils.response_handler import SuccessResponse # <-- 导入成功响应函数
from sqlalchemy import or_ # <--- 新增这一行
import os # 需要 os 模块来拼接路径
from app.utils.decorators import login_required

# auth = Blueprint('auth', __name__)
from . import auth

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        # return jsonify({"status": "error", "message": "用户名和密码不能为空"}), 400
        raise APIException(message="用户名和密码不能为空", status_code=400, error_code=1001)

    if UserModel.query.filter_by(username=username).first():
        # return jsonify({"status": "error", "message": "用户名已存在"}), 400
        raise APIException(message="用户名已存在", status_code=400, error_code=2003)
    
    new_user = UserModel(
        username=username,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    # return jsonify({"status": "success", "message": "注册成功"})
    return SuccessResponse(message="注册成功")

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise APIException("用户名和密码不能为空", status_code=400,error_code=1001)

    user = UserModel.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        raise APIException("用户名或密码错误", status_code=401,error_code=2002)
        
    session['user_id'] = user.id
    user_data = {"id": user.id, "username": user.username}
    # 使用新的辅助函数返回成功响应
    return SuccessResponse(data=user_data, message="登录成功")

@auth.route('/logout', methods=['POST'])
def logout():
    session.clear()
    # return jsonify({"status": "success", "message": "已成功登出"})
    return SuccessResponse(message="已成功登出")

@auth.route('/status', methods=['GET'])
def status():
    user_id = session.get('user_id')
    if user_id:
        # TODO: 根据 user_id 查询用户 (1 行代码)
        user = UserModel.query.get(user_id)
        if user:
            # return jsonify({
            #     "logged_in": True,
            #     "user": {"id": user.id, "username": user.username}
            # })
            return SuccessResponse(data={
                "logged_in": True,
                "user": {"id": user.id, "username": user.username,"avatar":user.avatar}
            },message="已登录")
        raise APIException("用户已删除", status_code=404,error_code=3001)
    # return jsonify({"logged_in": False})
    return SuccessResponse(data={
        "logged_in": False,
    },message="未登录")

@auth.route('/users', methods=['GET'])
def list_users():
    # 1.从路由获取分页参数
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
    except TypeError:
        raise APIException('分页参数格式不正确', status_code=400, error_code=1002)
    
    # 2.从路由获取查询参数
    search_keyword = request.args.get('search', '', type=str)
    
    # 3.从进行数据库查询
    base_query = UserModel.query
    # 添加过滤条件
    base_query = base_query.filter(
            or_(
            UserModel.username.like(f'%{search_keyword}%')
        )
    )
    # 使用 base_query 进行分页查询
    pagination = base_query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

    # 4.处理数据
    users=[]
    for user in pagination.items:
        users.append({
            "id": user.id,
            "username": user.username
        })

    # 思路：从 pagination 对象中提取分页元数据
    pagination_data = {
        'total_pages': pagination.pages,   # 总页数
        'current_page': pagination.page,  # 当前页码
        'per_page': pagination.per_page,   # 每页数量
        'total_count': pagination.total,   # 总条目数
        'has_next': pagination.has_next,   # 是否有下一页
        'has_prev': pagination.has_prev,   # 是否有上一页
    }

    # 思路：将列表数据和分页数据组合在一起返回给前端
    response_data = {
        'list': users,         # 当前页的列表
        'pagination': pagination_data # 分页信息
    }

    return SuccessResponse(data=response_data,message="用户列表获取成功")

@auth.route('/upload-simple', methods=['POST'])
def upload_simple():
    """
    一个最简化的文件上传演示接口。
    """
    
    # 1. 从 request.files 中获取文件对象
    #    'file' 是我们与前端约定好的 key (键名)
    #    (假设前端使用 Postman 或表单 <input type="file" name="file">)
    file_obj = request.files['file']

    # 2. 获取原始文件名
    #    例如: "my_photo.jpg"
    original_filename = file_obj.filename

    # 3. 准备保存路径
    #    从配置中获取目标文件夹
    upload_dir = current_app.config['UPLOAD_FOLDER']
    #    使用 os.path.join 将文件夹路径和文件名拼接起来
    save_path = os.path.join(upload_dir, original_filename)

    # 4. 执行保存动作
    file_obj.save(save_path)
    
    # 5. 返回成功响应
    return SuccessResponse(
        message="文件上传成功",
        data={
            'saved_filename': original_filename,
            'saved_path_on_server': save_path
        }
    )

@auth.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """
    这是一个用于上传用户头像的接口示例。
    """
    print(f"当前登录用户ID: {g.user.id}")
    # 从 request.files 中获取文件对象
    file_obj = request.files['file']

    # 获取原始文件名
    original_filename = file_obj.filename

    # 提取文件扩展名
    _, ext= os.path.splitext(original_filename)

    if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
        raise APIException("不支持的文件格式，仅支持 jpg, jpeg, png, gif 格式", status_code=400, error_code=1003)
    
    # 准备保存路径
    upload_dir = current_app.config['UPLOAD_FOLDER']
    # 定义新的文件名，格式为 user_<用户ID>_avatar.<扩展名>
    new_filename = f"user_{g.user.id}_avatar{ext}"

    # 使用 os.path.join 将文件夹路径和文件名拼接起来
    save_path = os.path.join(upload_dir, new_filename)

    # 执行保存动作
    file_obj.save(save_path)
    g.user.avatar = f'http://127.0.0.1:5000/api/auth/uploads/{new_filename}'
    db.session.commit()

    # 返回成功响应
    return SuccessResponse(
        message="文件上传成功",
        data={
            'saved_filename': new_filename,
            'saved_path_on_server': save_path
        }
    )


# 添加一个用于提供上传文件的路由
@auth.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    # 使用 send_from_directory 函数安全地从指定目录提供文件
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)