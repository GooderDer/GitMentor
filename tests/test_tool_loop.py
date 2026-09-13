"""Phase 5：验证模型决定工具、工具结果回传、最终回答的循环。"""
import pytest

from llm.tool_definitions import build_default_executor
from llm.tool_loop import ToolCallingLoop


def test_tool_loop_executes_tool_then_returns_final_answer(tmp_path):
    (tmp_path / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")
    calls = []

    def fake_model(messages, definitions):
        calls.append(messages)
        if len(calls) == 1:
            return {
                "type": "tool_call",
                "name": "search_files",
                "arguments": {"repo_path": str(tmp_path), "pattern": "*.py"},
            }
        assert messages[-1]["role"] == "tool"
        assert messages[-1]["content"] == ["main.py"]
        return {"type": "final", "content": "找到 main.py。"}

    result = ToolCallingLoop(build_default_executor()).run(
        "找 Python 文件", fake_model
    )

    assert result.answer == "找到 main.py。"
    assert result.steps == 2
    assert len(result.messages) == 4


def test_tool_loop_stops_after_max_steps(tmp_path):
    def endless_model(messages, definitions):
        return {
            "type": "tool_call",
            "name": "search_files",
            "arguments": {"repo_path": str(tmp_path), "pattern": "*.py"},
        }

    with pytest.raises(RuntimeError, match="最大轮数"):
        ToolCallingLoop(build_default_executor(), max_steps=2).run(
            "不断搜索", endless_model
        )


def test_tool_loop_rejects_invalid_model_response():
    def invalid_model(messages, definitions):
        return {"type": "unknown"}

    with pytest.raises(ValueError, match="tool_call 或 final"):
        ToolCallingLoop(build_default_executor()).run("测试", invalid_model)
