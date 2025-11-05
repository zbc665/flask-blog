# app/utils/exception_handler.py

from flask import jsonify, current_app

from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import traceback

class APIException(Exception):
    """
    自定义的 API 异常类。
    用于在业务逻辑中主动抛出可预知的错误。
    """
    def __init__(self, message, status_code=400, error_code=None):
        """
        初始化 APIException 实例。
        """
        super().__init__()
        self.message = message  # 错误信息
        self.status_code = status_code  # HTTP 状态码
        self.error_code = error_code  # 业务错误码

    def to_dict(self):
        """
        将异常信息转换为字典，便于序列化为 JSON 响应。

        :return: 包含错误信息的字典
        """
        return {
            "status": "error",  # 状态标识
            "message": self.message,  # 错误信息
            "error_code": self.error_code  # 业务错误码
        }

def init_error_handlers(app):
    # 注册自定义 APIException 异常的处理函数
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        # 记录业务异常日志，直接输出到终端
        current_app.logger.info(f"业务异常: {e.message}")
        # 将异常信息转换为 JSON 响应
        response = jsonify(e.to_dict())
        # 设置 HTTP 状态码
        response.status_code = e.status_code
        # 返回响应
        return response

    # 注册 SQLAlchemyError 数据库异常的处理函数
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(e):
        # 捕获数据库相关异常，记录详细错误日志（包括堆栈信息）
        current_app.logger.error(f"数据库错误: {str(e)}\n{traceback.format_exc()}")
        # 返回统一的数据库错误响应，状态码 500
        return jsonify({"status": "error", "message": "服务器数据库操作失败"}), 500
    
    # 注册 HTTPException HTTP 异常的处理函数
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        # 捕获 HTTP 异常（如 404、405），记录警告日志
        current_app.logger.warning(f"HTTP 异常: {e.code} {e.name} - {e.description}")
        # 返回 HTTP 异常的描述信息和对应状态码
        return jsonify({"status": "error", "message": e.description}), e.code

    # 注册 Exception 未知异常的处理函数
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        # 捕获所有未处理的异常，记录详细错误日志（包括堆栈信息）
        current_app.logger.error(f"未捕获的异常: {str(e)}\n{traceback.format_exc()}")
        # 返回统一的未知错误响应，状态码 500
        return jsonify({"status": "error", "message": "服务器内部发生未知错误"}), 500