"""Shared test fixtures.

Strips environment variables and the dotenv file so tests see the
pure code defaults from `Settings`, not whatever happens to live in
the developer's local `deep_notes/.env`.
"""

import pytest

_ENV_PREFIXES = (
    "API_",
    "VAULT_",
    "EMBED_",
    "OLLAMA_",
    "OPENAI_",
    "OPENROUTER_",
    "VECTOR_",
    "QDRANT_",
    "COLLECTION_",
    "CHUNK_",
    "LLM_",
    "SIMILARITY_",
)


@pytest.fixture(autouse=True)
def isolate_settings(monkeypatch):
    """Run every test with a clean environment for Settings."""
    import os

    for key in list(os.environ):
        if key.startswith(_ENV_PREFIXES):
            monkeypatch.delenv(key, raising=False)

    from deep_notes import config

    monkeypatch.setattr(
        config.Settings,
        "model_config",
        {"env_file": None, "env_file_encoding": "utf-8"},
    )
