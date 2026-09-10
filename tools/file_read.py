"""Tool Calling 的文件读取工具，限制访问范围在仓库根目录内。"""
from __future__ import annotations

from pathlib import Path


def read_file(
    repo_path: str | Path,
    relative_path: str,
    *,
    max_chars: int | None = None,
) -> str:
    """读取仓库内文件并附加行号，拒绝路径越界。

    ``relative_path`` 必须是相对于仓库根目录的路径，例如 ``"src/main.py"``。
    ``max_chars`` 可限制返回长度，避免把超大文件一次性塞进模型上下文。
    """
    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"仓库目录不存在: {root}")
    if not relative_path or not relative_path.strip():
        raise ValueError("relative_path 不能为空。")
    if max_chars is not None and max_chars <= 0:
        raise ValueError("max_chars 必须大于 0。")

    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("禁止读取仓库目录之外的文件。") from exc
    if not candidate.is_file():
        raise FileNotFoundError(f"文件不存在: {relative_path}")

    text = candidate.read_text(encoding="utf-8")
    if max_chars is not None:
        text = text[:max_chars]
    numbered_lines = [
        f"{line_number:4}: {line}" for line_number, line in enumerate(text.splitlines(), start=1)
    ]
    return "\n".join(numbered_lines)
