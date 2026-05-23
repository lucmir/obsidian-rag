from llama_index.core.embeddings import BaseEmbedding

from deep_notes.config import Settings


def get_embed_model(config: Settings) -> BaseEmbedding:
    match config.embed_provider:
        case "ollama":
            from llama_index.embeddings.ollama import OllamaEmbedding

            return OllamaEmbedding(
                model_name=config.embed_model,
                base_url=config.ollama_base_url,
            )
        case "openai":
            from llama_index.embeddings.openai import OpenAIEmbedding

            return OpenAIEmbedding(
                model=config.embed_model,
                api_key=config.openai_api_key,
            )
        case _:
            raise ValueError(f"Unknown embed provider: {config.embed_provider}")
