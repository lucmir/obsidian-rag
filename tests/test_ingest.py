from deep_notes.ingest import load_vault, parse_frontmatter


def test_parse_frontmatter_basic():
    text = "---\ntitle: Hello\ntags: [a, b]\n---\nBody text here.\n"
    meta, body = parse_frontmatter(text)
    assert meta == {"title": "Hello", "tags": ["a", "b"]}
    assert body.strip() == "Body text here."


def test_parse_frontmatter_missing():
    text = "No frontmatter here.\n"
    meta, body = parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_parse_frontmatter_invalid_yaml_falls_back():
    text = "---\ntitle: : bad : yaml\n---\nBody\n"
    meta, body = parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_load_vault_reads_markdown(tmp_path):
    (tmp_path / "note-a.md").write_text("# A\nFirst note.\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "note-b.md").write_text(
        "---\ntags: [foo, bar]\n---\nSecond note.\n"
    )
    (tmp_path / "not-markdown.txt").write_text("ignored")

    docs = load_vault(str(tmp_path))

    assert len(docs) == 2
    names = {d.metadata["file_name"] for d in docs}
    assert names == {"note-a.md", "note-b.md"}

    by_name = {d.metadata["file_name"]: d for d in docs}
    assert by_name["note-b.md"].metadata["tags"] == ["foo", "bar"]


def test_load_vault_skips_empty_body(tmp_path):
    (tmp_path / "empty.md").write_text("---\ntitle: empty\n---\n   \n")
    (tmp_path / "real.md").write_text("Content.\n")

    docs = load_vault(str(tmp_path))

    assert len(docs) == 1
    assert docs[0].metadata["file_name"] == "real.md"


def test_load_vault_missing_path_raises(tmp_path):
    import pytest

    missing = tmp_path / "does-not-exist"
    with pytest.raises(FileNotFoundError):
        load_vault(str(missing))


def test_load_vault_tags_as_csv_string(tmp_path):
    (tmp_path / "note.md").write_text(
        "---\ntags: foo, bar, baz\n---\nBody.\n"
    )
    docs = load_vault(str(tmp_path))
    assert docs[0].metadata["tags"] == ["foo", "bar", "baz"]
