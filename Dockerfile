FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

# 先从普通 PyPI 安装 Torch 运行所需依赖，
# 避免 PyTorch CPU 下载源校验这些依赖时出错。
RUN pip install --no-cache-dir \
    filelock \
    typing-extensions \
    sympy \
    networkx \
    jinja2 \
    fsspec

# 只从 PyTorch CPU 源下载 torch 本体；--no-deps 表示不再去该源下载上面的依赖。
RUN pip install --no-cache-dir \
    torch==2.5.1+cpu \
    --no-deps \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]