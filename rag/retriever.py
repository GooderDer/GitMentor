"""RAG 的检索层：问题 -> 相关 Chunk -> 可放入 prompt 的上下文。"""
from __future__ import annotations

from dataclasses import dataclass

from vectorstore.store import ChromaVectorStore, SearchResult


@dataclass(frozen=True)
class RetrievalContext:
    """给生成模型使用的检索结果及格式化上下文。"""

    results: list[SearchResult]
    context_text: str

    @property
    def sources(self) -> list[str]:
        """返回去重后的来源文件和行号，保持检索顺序。"""
        seen: set[str] = set()
        sources: list[str] = []
        for result in self.results:
            chunk = result.chunk
            source = f"{chunk.source_file}:{chunk.start_line}-{chunk.end_line}"
            if source not in seen:
                seen.add(source)
                sources.append(source)
        return sources


class Retriever:
    """对 VectorStore 做一层面向 RAG 的封装。"""

    def __init__(self, vector_store: ChromaVectorStore, top_k: int = 5) -> None:
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0。")
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, question: str, top_k: int | None = None) -> RetrievalContext:
        """检索问题相关 Chunk，并生成带来源标记的上下文文本。"""
        limit = self.top_k if top_k is None else top_k
        results = self.vector_store.search(question, top_k=limit)
        sections = []
        for index, result in enumerate(results, start=1):
            chunk = result.chunk
            source = f"{chunk.source_file}:{chunk.start_line}-{chunk.end_line}"
            sections.append(f"[片段 {index} | 来源: {source}]\n{chunk.text}")
        return RetrievalContext(results, "\n\n".join(sections))
