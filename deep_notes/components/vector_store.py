from llama_index.core.vector_stores.types import BasePydanticVectorStore

from deep_notes.config import Settings


def get_vector_store(config: Settings) -> BasePydanticVectorStore:
    match config.vector_store_provider:
        case "qdrant":
            from llama_index.vector_stores.qdrant import QdrantVectorStore
            from qdrant_client import QdrantClient

            client = QdrantClient(url=config.qdrant_url)
            return QdrantVectorStore(
                client=client,
                collection_name=config.collection_name,
            )
        case _:
            raise ValueError(
                f"Unknown vector store provider: {config.vector_store_provider}"
            )


def clear_collection(config: Settings) -> None:
    """Delete the vector collection so the next index starts fresh."""
    match config.vector_store_provider:
        case "qdrant":
            from qdrant_client import QdrantClient

            client = QdrantClient(url=config.qdrant_url)
            client.delete_collection(config.collection_name)
        case _:
            raise ValueError(
                f"Unknown vector store provider: {config.vector_store_provider}"
            )
