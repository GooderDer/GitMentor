"""GitMentor 内置工具的定义与注册。"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from analyzer import analyze_repository
from llm.tool_executor import ToolDefinition, ToolExecutor
from tools.file_read import read_file
from tools.file_search import search_files


def analyze_project(repo_path: str) -> dict[str, Any]:
    """分析项目并返回可直接交给模型的普通字典。"""
    return asdict(analyze_repository(repo_path))


def build_default_executor() -> ToolExecutor:
    """创建并注册 GitMentor 的内置工具。"""
    executor = ToolExecutor()
    executor.register(
        ToolDefinition(
            name="search_files",
            description="在仓库中按 glob 模式搜索文件",
            function=search_files,
            parameters={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "pattern": {"type": "string", "default": "*"},
                },
                "required": ["repo_path"],
            },
        )
    )
    executor.register(
        ToolDefinition(
            name="read_file",
            description="读取仓库内指定文件并返回带行号的内容",
            function=read_file,
            parameters={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "relative_path": {"type": "string"},
                    "max_chars": {"type": "integer"},
                },
                "required": ["repo_path", "relative_path"],
            },
        )
    )
    executor.register(
        ToolDefinition(
            name="analyze_project",
            description="分析仓库语言、依赖、README 和入口文件",
            function=analyze_project,
            parameters={
                "type": "object",
                "properties": {"repo_path": {"type": "string"}},
                "required": ["repo_path"],
            },
        )
    )
    return executor
