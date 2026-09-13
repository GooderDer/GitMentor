"""Phase 5：验证安全读取仓库文件。"""
import pytest

from tools.file_read import read_file


def test_read_file_returns_numbered_lines(tmp_path):
    source = tmp_path / "src" / "main.py"
    source.parent.mkdir()
    source.write_text("def main():\n    return 1\n", encoding="utf-8")

    result = read_file(tmp_path, "src/main.py")

    assert "   1: def main():" in result
    assert "   2:     return 1" in result


def test_read_file_supports_max_chars(tmp_path):
    (tmp_path / "notes.txt").write_text("abcdef", encoding="utf-8")

    result = read_file(tmp_path, "notes.txt", max_chars=3)

    assert result == "   1: abc"


def test_read_file_rejects_paths_outside_repo(tmp_path):
    outside = tmp_path.parent / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="目录之外"):
        read_file(tmp_path, "../secret.txt")


def test_read_file_validates_missing_file_and_arguments(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_file(tmp_path, "missing.py")
    with pytest.raises(ValueError, match="不能为空"):
        read_file(tmp_path, "")
    with pytest.raises(ValueError, match="max_chars"):
        read_file(tmp_path, "missing.py", max_chars=0)
