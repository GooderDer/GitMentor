"""本地 Embedding 封装。

Embedding 的职责是把一段文字映射成向量；向量如何保存和检索由
``vectorstore.store`` 负责。这里使用 sentence-transformers，因此不需要 API key。
"""
from __future__ import annotations

from typing import Protocol, Sequence


class Embedder(Protocol):
    """向量化能力的最小接口，便于 VectorStore 解耦具体模型。"""

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """返回与输入文本顺序一致的向量列表。"""


class LocalEmbedder:
    """使用 SentenceTransformer 在本地生成多语言文本向量。

    默认模型支持中文和英文。模型会延迟到第一次调用 ``embed_texts`` 时加载，
    这样导入模块不会立刻触发模型下载，也方便单元测试注入自己的 Embedder。
    """

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name 不能为空。")
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "缺少 sentence-transformers，请运行 "
                    "`python -m pip install -r requirements.txt`。"
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """批量生成向量；空输入返回空列表。"""
        if not texts:
            return []
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("texts 中不能包含空文本或非字符串值。")

        vectors = self._get_model().encode(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, query: str) -> list[float]:
        """生成单个查询向量，供 VectorStore.search 使用。"""
        vectors = self.embed_texts([query])
        return vectors[0]
