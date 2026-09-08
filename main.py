"""GitMentor 入口：演示「下载仓库 -> 分析仓库」的完整流程"""
from tools.github_tool import clone_repository
from analyzer.repo_analyzer import analyze_repository


def print_repo_info(info) -> None:
    """把一个 RepoInfo 打印成易读的多行文本"""
    print("\n" + "=" * 50)
    print(f"项目名称: {info.name}")
    print(f"主要语言: {info.main_language or '未识别'}")
    print(f"源文件总数: {info.file_count}")
    print(f"语言分布: {info.language_counts}")
    print(f"README: {info.readme or '未找到'}")
    print(f"依赖文件: {info.dependency_files}")
    print(f"入口文件: {info.entry_files}")
    print("=" * 50 + "\n")


def main() -> None:
    repo_url = "https://github.com/addyosmani/agent-skills.git"

    # 1) 下载仓库
    repo_path = clone_repository(repo_url)
    print("项目保存位置:", repo_path)

    # 2) 分析仓库
    info = analyze_repository(repo_path)
    print_repo_info(info)


if __name__ == "__main__":
    main()