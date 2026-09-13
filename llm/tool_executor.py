"""Tool Calling 的本地执行层，不依赖具体 LLM SDK。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolDefinition:
    """一个可被模型选择的工具及其描述。"""

    name: str
    description: str
    function: Callable[..., Any]
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    """工具调用后的统一结果格式。"""

    name: str
    ok: bool
    result: Any = None
    error: str | None = None


class ToolExecutor:
    """注册工具，并执行模型返回的工具调用。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """注册工具；同名工具会被拒绝，避免意外覆盖。"""
        if not tool.name.strip():
            raise ValueError("工具名称不能为空。")
        if tool.name in self._tools:
            raise ValueError(f"工具已注册: {tool.name}")
        self._tools[tool.name] = tool

    def definitions(self) -> list[dict[str, Any]]:
        """返回可以提供给模型的工具描述。"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]

    def execute(self, name: str, arguments: dict[str, Any] | str | None = None) -> ToolResult:
        """执行一次工具调用；arguments 也支持 JSON 字符串。"""
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(name=name, ok=False, error=f"未知工具: {name}")
        try:
            parsed_arguments = self._parse_arguments(arguments)
            value = tool.function(**parsed_arguments)
            return ToolResult(name=name, ok=True, result=value)
        except (TypeError, ValueError, OSError) as exc:
            return ToolResult(name=name, ok=False, error=str(exc))

    @staticmethod
    def _parse_arguments(arguments: dict[str, Any] | str | None) -> dict[str, Any]:
        if arguments is None:
            return {}
        if isinstance(arguments, str):
            parsed = json.loads(arguments)
            if not isinstance(parsed, dict):
                raise ValueError("工具参数 JSON 必须是对象。")
            return parsed
        if not isinstance(arguments, dict):
            raise ValueError("工具参数必须是字典或 JSON 对象字符串。")
        return arguments
