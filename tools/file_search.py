"""Tool Calling 的第一个工具：在仓库中按文件名查找文件。"""
from __future__ import annotations

from pathlib import Path

from analyzer.repo_analyzer import IGNORED_DIRS


def search_files(repo_path: str | Path, pattern: str = "*") -> list[str]:
    """返回匹配 glob pattern 的项目相对路径。

    ``pattern`` 只匹配文件名或相对路径，例如 ``"*.py"``、``"**/README.md"``。
    结果排序后返回，保证工具输出稳定、易测试。
    """
    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"仓库目录不存在: {root}")
    if not pattern or pattern.strip() == "":
        raise ValueError("pattern 不能为空。")

    matches: list[str] = []
    for path in root.glob(pattern):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        matches.append(relative.as_posix())
    return sorted(matches)
