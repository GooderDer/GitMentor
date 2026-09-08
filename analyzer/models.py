"""仓库分析结果的数据结构定义"""
from dataclasses import dataclass, field


@dataclass
class RepoInfo:
    """一次仓库分析的聚合结果。

    字段说明:
        name             仓库名
        path             本地仓库路径
        file_count       有效源文件总数（已排除 .git 等目录）
        language_counts  各语言的文件数量，如 {"Python": 12, "JavaScript": 3}
        main_language    主要编程语言（文件数最多的语言）
        dependency_files 依赖清单文件列表（相对路径）
        readme           README 文件相对路径（找到的第一个）
        entry_files      入口文件列表（相对路径）
        source_files     按语言分组的所有源码文件（相对路径）
    """
    name: str
    path: str
    file_count: int = 0
    language_counts: dict = field(default_factory=dict)
    main_language: str | None = None
    dependency_files: list = field(default_factory=list)
    readme: str | None = None
    entry_files: list = field(default_factory=list)
    source_files: dict = field(default_factory=dict)