"""Phase 4：验证检索上下文和无模型问答流程。"""
from chunker.models import Chunk
from rag.qa import RetrievalQA
from rag.retriever import Retriever
from vectorstore.store import SearchResult


class FakeVectorStore:
    """只实现 Retriever 所需的 search 方法，避免测试依赖真实 Chroma。"""

    def __init__(self, results):
        self.results = results
        self.last_query = None
        self.last_top_k = None

    def search(self, query, top_k=5):
        self.last_query = query
        self.last_top_k = top_k
        return self.results[:top_k]


def test_retriever_formats_context_and_sources():
    results = [
        SearchResult(
            Chunk("项目入口在 main.py。", "README.md", 1, 2, "doc"),
            0.1,
        ),
        SearchResult(
            Chunk("main 函数启动分析流程。", "main.py", 4, 8, "code", "Python"),
            0.2,
        ),
    ]
    store = FakeVectorStore(results)
    context = Retriever(store, top_k=2).retrieve("项目入口在哪里？")

    assert store.last_query == "项目入口在哪里？"
    assert "[片段 1 | 来源: README.md:1-2]" in context.context_text
    assert "[片段 2 | 来源: main.py:4-8]" in context.context_text
    assert context.sources == ["README.md:1-2", "main.py:4-8"]


def test_retrieval_qa_returns_context_without_llm():
    chunk = Chunk("GitMentor 分析代码仓库。", "README.md", 1, 1, "doc")
    qa = RetrievalQA(Retriever(FakeVectorStore([SearchResult(chunk, 0.0)])))

    result = qa.ask("这个项目做什么？")

    assert result.question == "这个项目做什么？"
    assert "GitMentor 分析代码仓库" in result.answer
    assert result.sources == ["README.md:1-1"]
