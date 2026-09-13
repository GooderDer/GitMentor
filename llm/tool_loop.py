"""通用 Tool Calling 循环：模型决定工具，执行器负责执行。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from llm.tool_executor import ToolExecutor


ModelCallback = Callable[[list[dict[str, Any]], list[dict[str, Any]]], dict[str, Any]]


@dataclass(frozen=True)
class LoopResult:
    """工具循环结束后的最终答案和完整消息轨迹。"""

    answer: str
    messages: list[dict[str, Any]]
    steps: int


class ToolCallingLoop:
    """执行“模型判断 → 工具执行 → 结果回传”的循环。"""

    def __init__(self, executor: ToolExecutor, max_steps: int = 5) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps 必须大于 0。")
        self.executor = executor
        self.max_steps = max_steps

    def run(self, user_input: str, model: ModelCallback) -> LoopResult:
        """运行循环；model 返回 tool_call 或 final 类型的字典。"""
        if not user_input.strip():
            raise ValueError("user_input 不能为空。")

        messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_input}
        ]
        definitions = self.executor.definitions()

        for step in range(1, self.max_steps + 1):
            response = model(messages, definitions)
            response_type = response.get("type")

            if response_type == "final":
                answer = response.get("content", "")
                if not isinstance(answer, str):
                    raise ValueError("final response 的 content 必须是字符串。")
                messages.append({"role": "assistant", "content": answer})
                return LoopResult(answer, messages, step)

            if response_type != "tool_call":
                raise ValueError("模型响应 type 必须是 tool_call 或 final。")

            name = response.get("name")
            if not isinstance(name, str) or not name:
                raise ValueError("tool_call 必须包含非空 name。")
            arguments = response.get("arguments")
            tool_result = self.executor.execute(name, arguments)
            messages.append({"role": "assistant", "tool_call": response})
            messages.append(
                {
                    "role": "tool",
                    "name": name,
                    "ok": tool_result.ok,
                    "content": tool_result.result if tool_result.ok else tool_result.error,
                }
            )

        raise RuntimeError(f"工具调用超过最大轮数: {self.max_steps}")
