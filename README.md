# OpsAtlas

> 面向企业运维场景的可配置知识库问答平台。

OpsAtlas 以设备运维文档为首个 Demo 场景，支持将企业的操作规程、巡检 SOP、故障代码手册等资料转化为可检索的知识库，并基于检索结果生成带来源引用的回答。

## 项目状态

🚧 开发中。

## 目标能力

- 支持 Markdown、TXT 和文本型 PDF 多文档入库
- 保留文件名、页码、章节等来源元数据
- 使用向量检索、相似度阈值与 Rerank 召回相关资料
- 基于 DeepSeek 生成有引用来源的答案
- 提供 FastAPI 问答与文档入库接口
- 提供简单网页问答界面
- 使用 Docker 完成本地部署

## 业务场景

用户可以询问：

- 报警代码 E101 表示什么？
- 设备启动前需要检查哪些项目？
- 设备过热时应如何排查？
- 某项保养的周期是多久？

系统仅依据已入库文档回答；当检索不到可靠资料时，会返回“知识库中没有相关信息”。

## 规划架构

```text
运维文档（PDF / Markdown / TXT）
        ↓
文档解析与语义切分
        ↓
Embedding 向量化
        ↓
Milvus 向量数据库

用户问题
        ↓
向量检索 → Rerank → 阈值过滤
        ↓
参考资料 + 问题 → DeepSeek
        ↓
答案 + 文件来源 + 页码/章节
```

## 计划技术栈

- Python
- FastAPI
- DeepSeek API
- Sentence Transformers
- Milvus
- Docker
- HTML / JavaScript

## 开发原则

- Demo 文档均为虚构设备运维资料，不使用企业敏感数据
- API Key 仅保存在本地 `.env`，不会提交到 GitHub
- 所有回答展示可追溯来源
