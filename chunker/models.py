"""Chunk 数据结构"""
from dataclasses import dataclass


@dataclass
class Chunk:
    """知识库的最小检索单元。

    字段说明:
        text        块内容（要交给 Embedding 的原文）
        source_file 来源文件相对路径，如 "README.md"、"app/core.py"
        start_line  起始行号（从 1 开始）
        end_line    结束行号（含）
        chunk_type  块类型："doc"（文档）或 "code"（代码）
        language    编程语言（doc 块为 None）
    """
    text: str
    source_file: str
    start_line: int
    end_line: int
    chunk_type: str
    language: str | None = None
