"""使用 Chroma 保存并检索 Chunk。"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Sequence

from chunker.models import Chunk
from vectorstore.embedder import Embedder


@dataclass(frozen=True)
class SearchResult:
    """一次命中的 Chunk 以及 Chroma 返回的距离（越小越相似）。"""

    chunk: Chunk
    distance: float


class ChromaVectorStore:
    """把项目的 Chunk 映射到 Chroma collection。"""

    def __init__(
        self,
        embedder: Embedder,
        collection_name: str = "gitmentor_chunks",
        persist_directory: str | Path | None = None,
    ) -> None:
        self.embedder = embedder
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "缺少 chromadb，请运行 `python -m pip install -r requirements.txt`。"
            ) from exc

        if persist_directory is None:
            client = chromadb.Client()
        else:
            client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: Sequence[Chunk]) -> None:
        """向量化并保存一批 Chunk。空列表不产生任何操作。"""
        if not chunks:
            return
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)
        if len(embeddings) != len(chunks):
            raise ValueError("向量数量必须与 Chunk 数量一致。")

        self.collection.upsert(
            ids=[self._chunk_id(chunk, index) for index, chunk in enumerate(chunks)],
            documents=texts,
            embeddings=embeddings,
            metadatas=[self._metadata(chunk) for chunk in chunks],
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """将问题向量化，返回距离最近的若干 Chunk。"""
        if not query.strip():
            raise ValueError("query 不能为空。")
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0。")
        count = self.collection.count()
        if count == 0:
            return []

        result = self.collection.query(
            query_embeddings=self.embedder.embed_texts([query]),
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]
        return [
            SearchResult(self._to_chunk(document, metadata), float(distance))
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]

    @staticmethod
    def _metadata(chunk: Chunk) -> dict[str, str | int]:
        """把 Chunk 字段转换成 Chroma 支持的 metadata。"""
        return {
            "source_file": chunk.source_file,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "chunk_type": chunk.chunk_type,
            "language": chunk.language or "",
        }

    @staticmethod
    def _to_chunk(text: str, metadata: dict[str, str | int]) -> Chunk:
        return Chunk(
            text=text,
            source_file=str(metadata["source_file"]),
            start_line=int(metadata["start_line"]),
            end_line=int(metadata["end_line"]),
            chunk_type=str(metadata["chunk_type"]),
            language=str(metadata["language"]) or None,
        )

    @staticmethod
    def _chunk_id(chunk: Chunk, index: int) -> str:
        raw = f"{chunk.source_file}:{chunk.start_line}:{chunk.end_line}:{index}:{chunk.text}"
        return sha256(raw.encode("utf-8")).hexdigest()
