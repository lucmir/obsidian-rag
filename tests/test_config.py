from deep_notes.config import Settings


def test_defaults():
    s = Settings(vault_path="")
    assert s.embed_provider == "ollama"
    assert s.embed_model == "bge-m3"
    assert s.vector_store_provider == "qdrant"
    assert s.chunk_strategy == "markdown"
    assert s.llm_provider == "openrouter"


def test_collection_name_derived_from_vault_path(tmp_path):
    vault = tmp_path / "My Notes!"
    vault.mkdir()
    s = Settings(vault_path=str(vault))
    assert s.collection_name == "my-notes"


def test_collection_name_explicit_wins(tmp_path):
    s = Settings(vault_path=str(tmp_path), collection_name="custom")
    assert s.collection_name == "custom"


def test_collection_name_fallback_when_no_vault():
    s = Settings(vault_path="")
    assert s.collection_name == "obsidian_notes"
