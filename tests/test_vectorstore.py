"""Phase 3：验证向量存储与来源 metadata。"""
import pytest

pytest.importorskip("chromadb")

from chunker.models import Chunk
from vectorstore.store import ChromaVectorStore


class TopicEmbedder:
    """测试替身：把仓库主题和烹饪主题映射到不同坐标。"""

    def embed_texts(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            is_repository = any(
                word in lowered for word in ("仓库", "项目", "代码库", "repository")
            )
            is_cooking = any(
                word in lowered for word in ("烹饪", "菜谱", "食材")
            )
            vectors.append([float(is_repository), float(is_cooking), 0.1])
        return vectors


def test_search_returns_related_chunk_and_metadata(tmp_path):
    store = ChromaVectorStore(
        TopicEmbedder(),
        collection_name="vectorstore_search_test",
        persist_directory=tmp_path,
    )
    chunks = [
        Chunk(
            "GitMentor 用于分析代码仓库并帮助学习项目结构。",
            "README.md",
            1,
            1,
            "doc",
        ),
        Chunk("这里介绍烹饪食材和家常菜谱。", "cook.md", 1, 1, "doc"),
    ]
    store.add_chunks(chunks)

    results = store.search("这个项目主要做什么？", top_k=1)

    assert len(results) == 1
    assert results[0].chunk.source_file == "README.md"
    assert results[0].chunk.start_line == 1
    assert "代码仓库" in results[0].chunk.text


def test_empty_store_and_invalid_arguments(tmp_path):
    store = ChromaVectorStore(
        TopicEmbedder(),
        collection_name="vectorstore_validation_test",
        persist_directory=tmp_path,
    )

    assert store.search("项目是什么？") == []
    with pytest.raises(ValueError, match="不能为空"):
        store.search("   ")
    with pytest.raises(ValueError, match="top_k"):
        store.search("项目是什么？", top_k=0)
