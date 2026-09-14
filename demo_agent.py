"""Phase 6 演示：使用本地模拟模型运行 Agent 项目概览任务。"""
from __future__ import annotations

import argparse
from typing import Any

from agent.agent import Agent
from llm.tool_definitions import build_default_executor


def make_demo_model(repo_path: str):
    """返回一个两步模型：先分析项目，再根据结果给出概览。"""
    called = False

    def model(messages: list[dict[str, Any]], definitions: list[dict[str, Any]]):
        nonlocal called
        if not called:
            called = True
            return {
                "type": "tool_call",
                "name": "analyze_project",
                "arguments": {"repo_path": repo_path},
            }

        analysis = messages[-1].get("content", {})
        if isinstance(analysis, dict):
            return {
                "type": "final",
                "content": (
                    f"项目 {analysis.get('name', '未知')} 使用 "
                    f"{analysis.get('main_language', '未知语言')}，"
                    f"共有 {analysis.get('file_count', 0)} 个文件。"
                ),
            }
        return {"type": "final", "content": "无法读取项目分析结果。"}

    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 GitMentor Agent 演示")
    parser.add_argument("repo", nargs="?", default=".", help="本地仓库路径")
    args = parser.parse_args()

    agent = Agent(build_default_executor())
    result = agent.run(
        "请分析这个项目并给出项目概览。",
        make_demo_model(args.repo),
    )
    print(f"任务: {result.task}")
    print(f"执行步数: {result.steps}")
    print(f"答案: {result.answer}")


if __name__ == "__main__":
    main()
