# app/utils/decorators.py
from functools import wraps
from flask import session, g, request
from app.modules.auth.models import UserModel
from app.utils.exception_handler import APIException

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            raise APIException(message="请先登录", status_code=401, error_code=2001)
        
        user = UserModel.query.get(user_id)
        if not user:
            raise APIException(message="用户不存在或已注销", status_code=404, error_code=3001)
        g.user = user
        return func(*args, **kwargs)
    return wrapper

def permission_required(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(g, 'user'):
                raise APIException("服务器内部错误：用户状态丢失", status_code=500, error_code=1001)
            
            data = request.get_json()
            resource_id = data.get('id')
            if not resource_id:
                raise APIException("请求参数错误，缺少资源ID", status_code=400, error_code=1001)

            resource = model.query.get(resource_id)
            if not resource:
                raise APIException("操作的资源不存在", status_code=404, error_code=3001)
            
            if resource.user_id != g.user.id:
                raise APIException("权限不足，无法操作他人资源", status_code=403, error_code=4001)
            
            g.resource = resource
            return func(*args, **kwargs)
        return wrapper
    return decorator
