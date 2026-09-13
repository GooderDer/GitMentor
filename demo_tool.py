"""Phase 5 演示：不接入 LLM，手动模拟模型发出的工具调用。"""
from __future__ import annotations

import argparse

from llm.tool_definitions import build_default_executor


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 GitMentor Tool Calling 演示")
    parser.add_argument("repo", nargs="?", default=".", help="本地仓库路径")
    args = parser.parse_args()

    executor = build_default_executor()
    calls = [
        ("analyze_project", {"repo_path": args.repo}),
        ("search_files", {"repo_path": args.repo, "pattern": "**/*.py"}),
        (
            "read_file",
            {"repo_path": args.repo, "relative_path": "README.md", "max_chars": 1200},
        ),
    ]
    for name, arguments in calls:
        result = executor.execute(name, arguments)
        print(f"\n工具: {name}\n成功: {result.ok}")
        print(result.result if result.ok else result.error)


if __name__ == "__main__":
    main()
