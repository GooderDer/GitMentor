"""chunker 的单元测试。"""
from chunker.code_splitter import split_code, split_code_file
from chunker.text_splitter import split_markdown


def test_markdown_is_split_into_nonempty_chunks_with_source_locations():
    text = "# Title\n\n" + "\n".join(f"Paragraph {number}." for number in range(20))
    chunks = split_markdown(text, "README.md", max_chars=60, overlap_lines=1)
    assert len(chunks) > 1
    assert all(chunk.text.strip() and chunk.source_file == "README.md" for chunk in chunks)
    assert all(chunk.chunk_type == "doc" and chunk.start_line <= chunk.end_line for chunk in chunks)
    assert split_markdown(" \n\n", "README.md") == []


def test_python_is_split_by_function_and_class_with_line_numbers():
    text = "@decorator\ndef first():\n    return 1\n\nclass Service:\n    def run(self):\n        return 'ok'\n\nasync def second():\n    return 2\n"
    chunks = split_code(text, "src/service.py")
    assert len(chunks) == 3
    assert [chunk.start_line for chunk in chunks] == [1, 5, 9]
    assert all(chunk.source_file == "src/service.py" and chunk.chunk_type == "code" for chunk in chunks)
    assert all(chunk.language == "Python" and chunk.text.strip() for chunk in chunks)
    assert "def run" in chunks[1].text


def test_non_python_and_invalid_python_fall_back_to_line_chunks():
    chunks = split_code("const a = 1;\nconst b = 2;", "web/app.js", max_chars=12)
    invalid_python = split_code("def broken(:\n", "broken.py")
    assert len(chunks) == 2
    assert all(chunk.source_file == "web/app.js" and chunk.text for chunk in chunks)
    assert len(invalid_python) == 1
    assert invalid_python[0].start_line == invalid_python[0].end_line == 1


def test_code_file_uses_project_relative_source_path(tmp_path):
    source = tmp_path / "src" / "example.py"
    source.parent.mkdir()
    source.write_text("def hello():\n    return 'hi'\n", encoding="utf-8")
    chunks = split_code_file(source, tmp_path)
    assert chunks[0].source_file == "src/example.py"
