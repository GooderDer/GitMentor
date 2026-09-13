"""Phase 5：验证 GitMentor 内置工具注册。"""
from llm.tool_definitions import build_default_executor


def _make_repo(root):
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    (root / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")


def test_default_executor_exposes_expected_tool_definitions(tmp_path):
    executor = build_default_executor()

    definitions = executor.definitions()

    assert [item["name"] for item in definitions] == [
        "search_files",
        "read_file",
        "analyze_project",
    ]
    assert all(item["parameters"]["type"] == "object" for item in definitions)


def test_default_executor_runs_real_tools(tmp_path):
    _make_repo(tmp_path)
    executor = build_default_executor()

    search_result = executor.execute(
        "search_files", {"repo_path": str(tmp_path), "pattern": "*.py"}
    )
    read_result = executor.execute(
        "read_file", {"repo_path": str(tmp_path), "relative_path": "main.py"}
    )
    analyze_result = executor.execute(
        "analyze_project", {"repo_path": str(tmp_path)}
    )

    assert search_result.ok is True
    assert search_result.result == ["main.py"]
    assert read_result.ok is True
    assert "def main" in read_result.result
    assert analyze_result.ok is True
    assert analyze_result.result["readme"] == "README.md"
    assert analyze_result.result["main_language"] == "Python"
