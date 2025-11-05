from flask import jsonify

def SuccessResponse(data=None, message="操作成功"):
    """
    生成一个标准的成功 API 响应。
    """
    response_body = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response_body['data'] = data
    
    return jsonify(response_body), 200
