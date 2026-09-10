"""Phase 4 端到端演示：对本地仓库执行一次无模型 RAG 检索。"""
from __future__ import annotations

import argparse
from pathlib import Path

from analyzer import analyze_repository
from chunker import split_code_file, split_markdown_file
from rag import RetrievalQA, Retriever
from vectorstore import ChromaVectorStore, LocalEmbedder


def build_chunks(repo_path: Path):
    """根据分析结果读取 README 和已识别的代码文件。"""
    info = analyze_repository(repo_path)
    chunks = []
    if info.readme:
        chunks.extend(split_markdown_file(repo_path / info.readme, repo_path))
    for files in info.source_files.values():
        for relative_file in files:
            path = repo_path / relative_file
            relative_parts = Path(relative_file).parts
            if "tests" in relative_parts or path.name.startswith("demo_"):
                continue
            if path.suffix.lower() in {".md", ".rst", ".txt"}:
                continue
            chunks.extend(split_code_file(path, repo_path))
    return info, chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 GitMentor 本地 RAG 检索演示")
    parser.add_argument("repo", nargs="?", default=".", help="本地仓库路径，默认是当前目录")
    parser.add_argument("question", nargs="?", default="这个项目的核心功能是什么？")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    info, chunks = build_chunks(repo_path)
    if not chunks:
        raise SystemExit("没有找到可检索的 README 或代码 Chunk。")

    store = ChromaVectorStore(LocalEmbedder(), collection_name="gitmentor_demo")
    store.add_chunks(chunks)
    result = RetrievalQA(Retriever(store, top_k=3)).ask(args.question)

    print(f"仓库: {info.name}")
    print(f"Chunk 数量: {len(chunks)}")
    print(f"\n问题: {result.question}\n")
    print(result.answer)
    print("\n引用来源:")
    for source in result.sources:
        print(f"- {source}")


if __name__ == "__main__":
    main()
