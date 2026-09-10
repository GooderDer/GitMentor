# GitMentor

GitMentor 是一个帮助开发者理解代码仓库的学习型工具。它从仓库分析开始，
逐步构建文档与代码切分、向量检索和 RAG 问答能力。

## 当前功能

- 分析本地仓库：识别主要编程语言、README、依赖文件和入口文件
- 切分文档与代码：README 按文本块切分，Python 按函数和类切分
- 本地 Embedding：使用 `sentence-transformers` 将文本转换为 384 维向量
- 向量检索：使用 Chroma 保存向量和来源 metadata，并按语义搜索相关内容
- RAG 检索：把问题转换成查询，返回相关上下文、文件名和行号引用

## 架构

```text
Repository
    ↓
Repository Analyzer
    ↓
Chunker (Markdown / Python / other code)
    ↓
Local Embedding (SentenceTransformer)
    ↓
Chroma Vector Store
    ↓
Retriever
    ↓
RetrievalQA (context + sources)
```

## 快速开始

在 Windows PowerShell 中创建并激活虚拟环境：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

运行全部测试：

```powershell
python -m pytest -q
```

运行本地仓库的 RAG 检索演示：

```powershell
python demo_rag.py .
python demo_rag.py . "这个项目如何进行代码切分？"
```

第一次运行本地 Embedding 时会从 Hugging Face 下载模型；之后模型会被缓存。
整个流程不需要 OpenAI API Key，也不会消耗在线 API 额度。

## 项目结构

```text
analyzer/      仓库结构和语言分析
chunker/       文档与代码切分
vectorstore/  Embedding 与 Chroma 向量检索
rag/           RAG 检索和上下文组织
tools/         GitHub 仓库工具
tests/         单元测试
demo_rag.py   端到端检索演示
```

## 当前限制与后续计划

当前 `RetrievalQA` 返回的是检索到的上下文，而不是由生成模型总结的自然语言答案。
后续计划包括 Tool Calling、Agent Workflow、FastAPI 接口，以及一个可展示的完整应用。
