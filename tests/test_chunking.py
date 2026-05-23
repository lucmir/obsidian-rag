import pytest
from llama_index.core.node_parser import (
    MarkdownNodeParser,
    SentenceSplitter,
    TokenTextSplitter,
)

from deep_notes.components.chunking import get_splitter
from deep_notes.config import Settings


def _settings(strategy: str) -> Settings:
    return Settings(vault_path="", chunk_strategy=strategy)


def test_sentence_strategy():
    splitter = get_splitter(_settings("sentence"))
    assert isinstance(splitter, SentenceSplitter)


def test_token_strategy():
    splitter = get_splitter(_settings("token"))
    assert isinstance(splitter, TokenTextSplitter)


def test_markdown_strategy():
    splitter = get_splitter(_settings("markdown"))
    assert isinstance(splitter, MarkdownNodeParser)


def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown chunk strategy"):
        get_splitter(_settings("nope"))
