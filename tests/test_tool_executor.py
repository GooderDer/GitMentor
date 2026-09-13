"""Phase 5：验证工具注册与执行器。"""
import pytest

from llm.tool_executor import ToolDefinition, ToolExecutor


def add_numbers(left: int, right: int) -> int:
    return left + right


def test_executor_registers_definitions_and_executes_dict_arguments():
    executor = ToolExecutor()
    executor.register(
        ToolDefinition(
            name="add_numbers",
            description="计算两个数字的和",
            function=add_numbers,
            parameters={"type": "object"},
        )
    )

    result = executor.execute("add_numbers", {"left": 2, "right": 3})

    assert result.ok is True
    assert result.result == 5
    assert executor.definitions()[0]["name"] == "add_numbers"


def test_executor_accepts_json_arguments_and_reports_errors():
    executor = ToolExecutor()
    executor.register(
        ToolDefinition("add_numbers", "加法", add_numbers, {"type": "object"})
    )

    json_result = executor.execute(
        "add_numbers", '{"left": 4, "right": 6}'
    )
    unknown_result = executor.execute("missing_tool", {})
    invalid_result = executor.execute("add_numbers", {"left": 1})

    assert json_result.result == 10
    assert unknown_result.ok is False
    assert "未知工具" in unknown_result.error
    assert invalid_result.ok is False


def test_executor_rejects_duplicate_or_empty_tool_names():
    executor = ToolExecutor()
    definition = ToolDefinition("add_numbers", "加法", add_numbers, {})
    executor.register(definition)

    with pytest.raises(ValueError, match="已注册"):
        executor.register(definition)
    with pytest.raises(ValueError, match="不能为空"):
        executor.register(ToolDefinition("", "无名称", add_numbers, {}))
