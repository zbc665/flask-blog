# 1. 使用一个轻量级的 Python 官方镜像作为基础
FROM python:3.12-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件到工作目录
COPY requirements.txt .

# 4. 安装依赖 (现在会自动安装 Flask 和 Gunicorn)
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制所有应用代码到工作目录
COPY . .

# 6. 暴露 Flask 应用运行的端口
EXPOSE 5000

# 7. (新) 生产环境启动命令
#
# gunicorn -w 4 -b 0.0.0.0:5000 app:app
#
# -w 4: 启动 4 个 "worker" 进程来并发处理请求。这是一个常见的起点。
# -b 0.0.0.0:5000: 绑定 (bind) 到所有 IP 的 5000 端口。
# app:app: 运行 'app.py' 文件中的 'app' 实例。
#
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
