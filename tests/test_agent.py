"""Phase 6：验证 Agent 对任务的编排能力。"""
from agent.agent import Agent
from llm.tool_definitions import build_default_executor


def test_agent_runs_task_and_preserves_execution_trace(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    seen_messages = []

    def fake_model(messages, definitions):
        seen_messages.append(messages)
        if len(seen_messages) == 1:
            assert "用户任务：读取项目 README" in messages[0]["content"]
            return {
                "type": "tool_call",
                "name": "read_file",
                "arguments": {
                    "repo_path": str(tmp_path),
                    "relative_path": "README.md",
                },
            }
        return {"type": "final", "content": "README 是项目说明文档。"}

    result = Agent(build_default_executor()).run("读取项目 README", fake_model)

    assert result.task == "读取项目 README"
    assert result.answer == "README 是项目说明文档。"
    assert result.steps == 2
    assert len(result.messages) == 4


def test_agent_rejects_empty_task():
    agent = Agent(build_default_executor())

    try:
        agent.run("   ", lambda messages, definitions: {"type": "final", "content": ""})
    except ValueError as exc:
        assert "不能为空" in str(exc)
    else:
        raise AssertionError("空任务应该被拒绝")
