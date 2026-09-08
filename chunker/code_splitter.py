"""代码切分：优先按 Python 的类和函数边界生成语义完整的 Chunk。"""
from __future__ import annotations

import ast
from pathlib import Path

from chunker.models import Chunk


def split_code(text: str, source_file: str, max_chars: int = 800) -> list[Chunk]:
    """按语言选择切分策略；Python 按 AST，其余代码按行切分。"""
    if not text.strip():
        return []
    if Path(source_file).suffix.lower() == ".py":
        python_chunks = _split_python(text, source_file)
        if python_chunks:
            return python_chunks
    return _split_by_lines(text, source_file, max_chars)


def split_code_file(path: str | Path, project_root: str | Path | None = None) -> list[Chunk]:
    """读取一个代码文件并切分；来源路径相对于 project_root（若提供）。"""
    file_path = Path(path)
    source_file = file_path.relative_to(project_root).as_posix() if project_root else file_path.as_posix()
    return split_code(file_path.read_text(encoding="utf-8"), source_file)


def _split_python(text: str, source_file: str) -> list[Chunk]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.splitlines()
    chunks: list[Chunk] = []
    for node in tree.body:
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        start_line = min([node.lineno, *(item.lineno for item in node.decorator_list)])
        end_line = node.end_lineno or start_line
        block = "\n".join(lines[start_line - 1:end_line]).strip()
        if block:
            chunks.append(Chunk(block, source_file, start_line, end_line, "code", "Python"))
    return chunks


def _split_by_lines(text: str, source_file: str, max_chars: int) -> list[Chunk]:
    if max_chars <= 0:
        raise ValueError("max_chars 必须大于 0")
    lines = text.splitlines()
    chunks: list[Chunk] = []
    current: list[str] = []
    current_length = 0
    start_line = 1
    for line_number, line in enumerate(lines, start=1):
        added_length = len(line) + (1 if current else 0)
        if current and current_length + added_length > max_chars:
            chunks.append(_make_chunk(current, source_file, start_line, line_number - 1))
            current, current_length, start_line = [], 0, line_number
        current.append(line)
        current_length += len(line) + (1 if len(current) > 1 else 0)
    if current:
        chunks.append(_make_chunk(current, source_file, start_line, len(lines)))
    return [chunk for chunk in chunks if chunk.text]


def _make_chunk(lines: list[str], source_file: str, start_line: int, end_line: int) -> Chunk:
    return Chunk("\n".join(lines).strip(), source_file, start_line, end_line, "code")
