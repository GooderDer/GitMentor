"""analyzer.repo_analyzer 的单元测试"""
from analyzer.repo_analyzer import analyze_repository


def _make_repo(root):
    """在 root 下搭一个最小的假仓库，覆盖不同场景"""
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    (root / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")
    (root / "requirements.txt").write_text("requests\n", encoding="utf-8")
    (root / "app").mkdir()
    (root / "app" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    # 这个目录应该被忽略，不计入统计
    (root / ".git").mkdir()
    (root / ".git" / "objects").mkdir()
    (root / ".git" / "objects" / "abc").write_text("", encoding="utf-8")


def test_analyze_detects_language_and_files(tmp_path):
    _make_repo(tmp_path)
    info = analyze_repository(tmp_path)

    assert info.name == tmp_path.name
    assert info.file_count == 4  # README + main.py + requirements.txt + app/core.py
    assert info.main_language == "Python"
    assert info.language_counts == {"Python": 2}
    assert info.readme == "README.md"
    assert info.dependency_files == ["requirements.txt"]
    assert info.entry_files == ["main.py"]


def test_analyze_ignores_ignored_dirs(tmp_path):
    _make_repo(tmp_path)
    info = analyze_repository(tmp_path)

    # .git 目录下的文件不应出现在源码文件列表里
    all_source_files = [
        p for files in info.source_files.values() for p in files
    ]
    assert all(".git" not in p for p in all_source_files)