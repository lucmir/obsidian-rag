import re
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings


_ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}

    # API
    api_port: int = 8000
    api_key: str = ""

    # Vault
    vault_path: str = ""

    # Embedding
    embed_provider: str = "ollama"  # "ollama" | "openai"
    embed_model: str = "bge-m3"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""

    # Vector store
    vector_store_provider: str = "qdrant"  # "qdrant" | "chroma"
    qdrant_url: str = "http://localhost:6333"
    collection_name: str = ""

    @model_validator(mode="after")
    def _derive_collection_name(self):
        if not self.collection_name and self.vault_path:
            slug = re.sub(r"[^a-z0-9]+", "-", Path(self.vault_path).name.lower()).strip("-")
            self.collection_name = slug or "obsidian_notes"
        elif not self.collection_name:
            self.collection_name = "obsidian_notes"
        return self

    # Chunking
    chunk_strategy: str = "markdown"  # "sentence" | "token" | "markdown"
    chunk_size: int = 512
    chunk_overlap: int = 50

    # LLM
    llm_provider: str = "openrouter"  # "openrouter" | "openai" | "ollama"
    llm_model: str = "anthropic/claude-sonnet-4"
    openrouter_api_key: str = ""

    # Retrieval
    similarity_top_k: int = 3


def get_settings(**overrides) -> Settings:
    return Settings(**overrides)
