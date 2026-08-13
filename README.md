# OpsAtlas｜设备运维 RAG 知识库

OpsAtlas 是一个面向设备运维场景的 RAG（检索增强生成）知识库应用。

项目使用虚构的 AstraSort AS-200 自动分拣设备资料作为 Demo 数据，支持将报警代码、操作手册、巡检 SOP 等文档入库。用户提问时，系统先检索知识库中的相关资料，再调用 DeepSeek 基于参考资料生成回答，并展示来源文件、章节和 PDF 页码。

> Demo 文档均为虚构资料，仅用于项目演示，不包含企业敏感数据。

## 项目亮点

- 支持 Markdown、TXT、文本型 PDF 的读取、上传和批量入库；
- PDF 按页解析，保留文件名、章节标题、页码等来源元数据；
- 使用 `BAAI/bge-small-zh-v1.5` 将文本转换为 512 维向量；
- 使用 Milvus 实现 Top-K 语义检索；
- 使用相似度阈值过滤无关资料，资料不足时不调用 LLM，避免编造；
- 使用 DeepSeek 根据检索资料生成受约束回答；
- 支持答案来源溯源，显示文件名、Chunk、相似度、PDF 页码；
- 提供 FastAPI 问答、入库、上传接口和网页问答页；
- 使用 Docker Compose 编排 FastAPI、Milvus、etcd、MinIO；
- 包含日志、统一异常处理和 DeepSeek 临时错误重试。

## RAG 流程

```text
Markdown / TXT / PDF 文档
        ↓
文档解析（PDF 保留页码）
        ↓
按标题进行语义切分
        ↓
BGE Embedding 向量化
        ↓
向量 + 正文 + 来源元数据写入 Milvus


用户问题
        ↓
同一 Embedding 模型生成问题向量
        ↓
Milvus Top-K 检索
        ↓
相似度阈值过滤
        ↓
参考资料 + 用户问题组成 Prompt
        ↓
DeepSeek 生成回答
        ↓
答案 + 文件来源 + Chunk + PDF 页码
```

## 技术栈

| 模块 | 技术 |
|---|---|
| 后端 | Python、FastAPI、Pydantic、Uvicorn |
| 文档处理 | pathlib、pypdf |
| 向量化 | sentence-transformers、BAAI/bge-small-zh-v1.5 |
| 向量数据库 | Milvus |
| 大模型 | DeepSeek API |
| 前端 | HTML、CSS、JavaScript、Fetch、FormData |
| 部署 | Docker、Docker Compose |
| 工程化 | `.env`、日志、异常处理、重试、Git / GitHub |

## 项目结构

```text
OpsAtlas/
├─ data/
│  └─ raw/                    # 原始知识文档
├─ docs/
│  └─ test_cases.md           # 测试问题与验证结果
├─ scripts/
│  └─ create_demo_pdf.py      # Demo PDF 生成脚本
├─ src/
│  ├─ document_loader.py      # MD / TXT / PDF 读取
│  ├─ text_splitter.py        # 语义切分与 Chunk 元数据
│  ├─ embedding.py            # 文本转向量
│  ├─ milvus_client.py        # Milvus 连接与 Collection 管理
│  ├─ ingest.py               # 批量入库总流程
│  ├─ retriever.py            # Top-K 检索与阈值过滤
│  ├─ prompt_builder.py       # RAG Prompt 构建
│  ├─ deepseek_client.py      # DeepSeek 调用与重试
│  ├─ rag_chat.py             # RAG 问答总流程
│  ├─ logger_config.py        # 统一日志
│  ├─ main.py                 # FastAPI 接口
│  └─ static/                 # 网页问答与上传页面
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ .env.example
```

## 快速启动

### 1. 配置环境变量

复制 `.env.example` 为 `.env`，填写自己的 DeepSeek API Key：

```ini
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
DEEPSEEK_MODEL=deepseek-v4-flash
```

`.env` 不应提交到 GitHub。

### 2. 启动服务

```powershell
docker compose up -d --build
```

首次启动需要下载 Python 依赖、CPU 版 PyTorch 和 Embedding 模型，耗时较长。

后续启动：

```powershell
docker compose up -d
```

查看状态：

```powershell
docker compose ps
```

停止服务：

```powershell
docker compose down
```

### 3. 打开应用

```text
http://127.0.0.1:8000
```

Swagger 接口文档：

```text
http://127.0.0.1:8000/docs
```

## 核心接口

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/health` | 服务健康检查 |
| `POST` | `/ask` | 提交问题，返回答案与引用来源 |
| `POST` | `/ingest` | 重新入库 `data/raw` 中全部资料 |
| `POST` | `/upload` | 上传 `.md`、`.txt`、`.pdf` 后自动入库 |

`POST /ask` 请求示例：

```json
{
  "question": "E205 输送带电机过热应如何处理？"
}
```

## 已验证场景

完整测试记录见 [docs/test_cases.md](docs/test_cases.md)。

- E101 扫码器通信异常检索；
- E205 输送带电机过热处理；
- 无资料问题的阈值兜底；
- PDF 第 2 页引用溯源；
- 网页上传资料后自动入库。

## 异常处理策略

- 未检索到达到阈值的资料：直接返回“根据当前知识库资料无法确定”；
- Milvus 不可用：接口返回 `503`，后端记录完整异常；
- DeepSeek 服务繁忙、网络异常或限流：最多自动重试 2 次；
- 上传不支持的文件类型：接口返回 `400`；
- API Key 通过 `.env` 注入，不写入镜像、不提交 GitHub。

## 后续优化方向

- Rerank，优化 Top-K 资料排序；
- 混合检索；
- 长文本 Chunk overlap；
- 自动化测试与评测集；
- 多轮对话历史；
- 文档版本、权限和知识库管理。