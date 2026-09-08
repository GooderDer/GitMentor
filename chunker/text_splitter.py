"""文档切分：把 README 之类的长文本切成若干块"""
from pathlib import Path

from chunker.models import Chunk


def split_markdown(
    text: str,
    source_file: str = "README.md",
    max_chars: int = 500,
    overlap_lines: int = 2,
) -> list[Chunk]:
    """按行把 markdown 文本切成若干块。

    思路:
        1. 逐行累积，当字符数接近 max_chars 就"封口"成一个块；
        2. 新块开头带上上一块最后 overlap_lines 行，避免一句关键的话
           正好被从中间切断（这就是"overlap 重叠"的作用）。

    注意:
        单行超过 max_chars 时该行会原样保留（不做硬截断），这是可接受的
        极端情况。
    """
    if max_chars <= 0:
        raise ValueError("max_chars 必须大于 0")
    if overlap_lines < 0:
        raise ValueError("overlap_lines 不能小于 0")

    lines = text.splitlines()
    if not lines:
        return []

    chunks = []
    current = []          # 当前块里累积的行
    current_chars = 0     # 当前块的字符数
    start_line = 1        # 当前块的起始行号

    for idx, line in enumerate(lines, start=1):
        # 当前块不为空，且再加入这一行会超长 -> 封口
        if current and current_chars + len(line) > max_chars:
            _append_doc_chunk(chunks, current, source_file, start_line, idx - 1)
            # overlap：把末尾 overlap_lines 行带进下一块开头
            overlap = current[-overlap_lines:]
            current = list(overlap)
            current_chars = sum(len(l) for l in current)
            start_line = idx - len(current)

        current.append(line)
        current_chars += len(line)

    if current:
        _append_doc_chunk(chunks, current, source_file, start_line, len(lines))

    return chunks


def _append_doc_chunk(
    chunks: list[Chunk], lines: list[str], source_file: str, start_line: int, end_line: int
) -> None:
    text = "\n".join(lines).strip()
    if text:
        chunks.append(Chunk(text, source_file, start_line, end_line, "doc"))


def split_markdown_file(path: str | Path, project_root: str | Path | None = None) -> list[Chunk]:
    """读取 Markdown 文件并切分；来源路径相对于 project_root（若提供）。"""
    file_path = Path(path)
    source_file = file_path.relative_to(project_root).as_posix() if project_root else file_path.as_posix()
    return split_markdown(file_path.read_text(encoding="utf-8"), source_file)
