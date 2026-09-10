"""
分析 GitHub 项目的基本信息：
目录遍历、语言识别、依赖文件与入口文件识别、README 查找
"""
from pathlib import Path

from analyzer.models import RepoInfo

# 遍历时跳过这些目录（它们是工具产物，不是项目源码）
IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".idea", ".vscode", "dist", "build", ".tox", ".mypy_cache",
    ".pytest_cache", ".eggs", "repos",
}

# 文件后缀 -> 语言名
LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".cpp": "C++",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".sh": "Shell",
    ".html": "HTML",
    ".css": "CSS",
}

# 常见依赖清单文件名（小写）
DEPENDENCY_FILES = {
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "pipfile",
    "package.json", "package-lock.json", "go.mod", "go.sum", "gemfile",
    "cargo.toml", "pom.xml", "build.gradle", "composer.json",
}

# 常见入口文件名（小写）
ENTRY_FILES = {
    "main.py", "app.py", "manage.py", "run.py", "server.py",
    "index.js", "server.js", "main.go", "main.rs", "app.js",
}

# 常见 README 文件名（小写）
README_NAMES = {
    "readme.md", "readme.rst", "readme.txt", "readme", "readme.markdown",
    "readme.org",
}


def analyze_repository(repo_path) -> RepoInfo:
    """分析一个本地仓库，返回结构化的 RepoInfo。"""
    root = Path(repo_path)
    info = RepoInfo(name=root.name, path=str(root))

    for file in _iter_source_files(root):
        relative = file.relative_to(root).as_posix()
        lower_name = file.name.lower()
        ext = file.suffix.lower()

        info.file_count += 1

        # 1) 语言识别
        language = LANGUAGE_EXTENSIONS.get(ext)
        if language:
            info.language_counts[language] = info.language_counts.get(language, 0) + 1
            info.source_files.setdefault(language, []).append(relative)

        # 2) README 查找（取第一个）
        if info.readme is None and lower_name in README_NAMES:
            info.readme = relative

        # 3) 依赖文件
        if lower_name in DEPENDENCY_FILES:
            info.dependency_files.append(relative)

        # 4) 入口文件
        if lower_name in ENTRY_FILES:
            info.entry_files.append(relative)

    if info.language_counts:
        info.main_language = max(info.language_counts, key=info.language_counts.get)

    return info


def _iter_source_files(root: Path):
    """递归遍历 root 下的所有源文件，跳过被忽略的目录。"""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        yield path
