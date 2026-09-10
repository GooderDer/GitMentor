"""Phase 5：验证按 glob 模式搜索仓库文件。"""
import pytest

from tools.file_search import search_files


def test_search_files_returns_sorted_relative_matches(tmp_path):
    (tmp_path / "main.py").write_text("", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("", encoding="utf-8")

    assert search_files(tmp_path, "**/*.py") == ["main.py", "src/service.py"]


def test_search_files_ignores_configured_directories(tmp_path):
    (tmp_path / "repos").mkdir()
    (tmp_path / "repos" / "external.py").write_text("", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "internal.py").write_text("", encoding="utf-8")
    (tmp_path / "app.py").write_text("", encoding="utf-8")

    assert search_files(tmp_path, "**/*.py") == ["app.py"]


def test_search_files_validates_arguments(tmp_path):
    with pytest.raises(ValueError, match="不能为空"):
        search_files(tmp_path, " ")
    with pytest.raises(NotADirectoryError):
        search_files(tmp_path / "missing", "*.py")
