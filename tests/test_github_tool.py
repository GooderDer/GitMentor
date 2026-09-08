"""tools.github_tool 的单元测试（不联网，只测 URL 解析）"""
from tools.github_tool import _repo_name_from_url


def test_repo_name_from_url_with_git_suffix():
    assert _repo_name_from_url("https://github.com/owner/repo.git") == "repo"


def test_repo_name_from_url_without_suffix():
    assert _repo_name_from_url("https://github.com/owner/repo") == "repo"


def test_repo_name_from_url_with_trailing_slash():
    assert _repo_name_from_url("https://github.com/owner/repo/") == "repo"