"""GitHub 仓库相关工具"""
import os


def _repo_name_from_url(repo_url: str) -> str:
    """从仓库 URL 中提取仓库名，去掉末尾的 / 和 .git 后缀。

    例如:
        "https://github.com/owner/repo.git" -> "repo"
        "https://github.com/owner/repo"     -> "repo"
        "https://github.com/owner/repo/"    -> "repo"
    """
    name = repo_url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def clone_repository(repo_url: str, save_path: str = "repos") -> str:
    """下载 GitHub 仓库到本地。

    参数:
        repo_url:  GitHub 仓库地址
        save_path: 保存仓库的目录，默认保存到当前项目的 repos 文件夹

    返回:
        本地仓库路径（字符串）
    """
    repo_name = _repo_name_from_url(repo_url)
    repo_path = os.path.join(save_path, repo_name)

    if os.path.exists(repo_path):
        print(f"仓库已存在，跳过下载: {repo_path}")
        return repo_path

    print(f"正在下载仓库: {repo_url}")
    try:
        # 延迟导入：只分析本地仓库时不需要 GitPython。
        from git import Repo
        Repo.clone_from(repo_url, repo_path)
    except ImportError as exc:
        raise RuntimeError(
            "缺少 GitPython，请先运行 `python -m pip install -r requirements.txt`"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"下载仓库失败: {repo_url}") from exc

    print(f"下载完成: {repo_path}")
    return repo_path
