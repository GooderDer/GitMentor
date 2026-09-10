"""无生成模型的 RAG 问答层：返回检索上下文与可靠的来源引用。"""
from __future__ import annotations

from dataclasses import dataclass

from rag.retriever import Retriever


@dataclass(frozen=True)
class QAResult:
    """一次问答的结果；后续接入 LLM 时可复用此结构。"""

    question: str
    answer: str
    sources: list[str]


class RetrievalQA:
    """先完成检索，再把上下文原样作为答案返回。"""

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    def ask(self, question: str, top_k: int | None = None) -> QAResult:
        """检索问题相关内容，返回上下文和引用，不调用任何在线 API。"""
        context = self.retriever.retrieve(question, top_k=top_k)
        answer = context.context_text or "没有找到与问题相关的仓库内容。"
        return QAResult(
            question=question,
            answer=answer,
            sources=context.sources,
        )
