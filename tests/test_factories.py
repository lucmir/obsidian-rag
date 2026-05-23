"""Negative-path tests for the component factories.

We verify each factory raises a clear ValueError for unknown providers
without importing any network-dependent integration packages.
"""

import pytest

from deep_notes.components.embeddings import get_embed_model
from deep_notes.components.llm import get_llm
from deep_notes.components.vector_store import clear_collection, get_vector_store
from deep_notes.config import Settings


def test_embeddings_unknown_provider():
    s = Settings(vault_path="", embed_provider="bogus")
    with pytest.raises(ValueError, match="Unknown embed provider"):
        get_embed_model(s)


def test_llm_unknown_provider():
    s = Settings(vault_path="", llm_provider="bogus")
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_llm(s)


def test_vector_store_unknown_provider():
    s = Settings(vault_path="", vector_store_provider="bogus")
    with pytest.raises(ValueError, match="Unknown vector store provider"):
        get_vector_store(s)


def test_clear_collection_unknown_provider():
    s = Settings(vault_path="", vector_store_provider="bogus")
    with pytest.raises(ValueError, match="Unknown vector store provider"):
        clear_collection(s)
