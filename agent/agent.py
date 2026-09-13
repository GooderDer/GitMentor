"""Phase 6：在 Tool Calling 之上提供任务级 Agent。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from llm.tool_executor import ToolExecutor
from llm.tool_loop import ModelCallback, ToolCallingLoop


@dataclass(frozen=True)
class AgentResult:
    """Agent 完成任务后的答案与执行轨迹。"""

    task: str
    answer: str
    steps: int
    messages: list[dict[str, Any]]


class Agent:
    """接收任务并编排工具调用的最小 Agent。"""

    def __init__(
        self,
        executor: ToolExecutor,
        *,
        system_prompt: str = "你是一个谨慎的代码仓库学习助手。",
        max_steps: int = 5,
    ) -> None:
        self.executor = executor
        self.system_prompt = system_prompt
        self.loop = ToolCallingLoop(executor, max_steps=max_steps)

    def run(self, task: str, model: ModelCallback) -> AgentResult:
        """执行一次任务；model 负责决定调用工具或返回最终答案。"""
        if not task.strip():
            raise ValueError("task 不能为空。")

        prompt = f"系统要求：{self.system_prompt}\n\n用户任务：{task}"
        loop_result = self.loop.run(prompt, model)
        return AgentResult(
            task=task,
            answer=loop_result.answer,
            steps=loop_result.steps,
            messages=loop_result.messages,
        )
