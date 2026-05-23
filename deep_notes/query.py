from dataclasses import dataclass
from typing import Generator

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage

from deep_notes.config import Settings, get_settings
from deep_notes.components.embeddings import get_embed_model
from deep_notes.components.llm import get_llm
from deep_notes.components.vector_store import get_vector_store

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based on the user's Obsidian notes.\n"
    "Use ONLY the provided context to answer. If the context doesn't contain enough "
    "information, say so.\n"
    "Always cite which source notes you used by their filename."
)


@dataclass
class SourceChunk:
    file_name: str
    file_path: str
    text: str
    score: float


@dataclass
class RetrievalResult:
    sources: list[SourceChunk]
    context_str: str


def retrieve(question: str, config: Settings | None = None) -> RetrievalResult:
    """Retrieve relevant chunks without generating an answer."""
    if config is None:
        config = get_settings()

    vector_store = get_vector_store(config)
    embed_model = get_embed_model(config)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )

    retriever = index.as_retriever(similarity_top_k=config.similarity_top_k)
    nodes = retriever.retrieve(question)

    sources = [
        SourceChunk(
            file_name=node.metadata.get("file_name", "unknown"),
            file_path=node.metadata.get("file_path", ""),
            text=node.get_content(),
            score=node.score or 0.0,
        )
        for node in nodes
    ]

    context_str = "\n\n---\n\n".join(
        f"[Source: {s.file_name}]\n{s.text}" for s in sources
    )

    return RetrievalResult(sources=sources, context_str=context_str)


def stream_answer(
    question: str,
    context_str: str,
    chat_history: list[dict],
    config: Settings | None = None,
) -> Generator[str, None, None]:
    """Stream LLM response token by token."""
    if config is None:
        config = get_settings()

    llm = get_llm(config)

    messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]

    for msg in chat_history:
        messages.append(ChatMessage(role=msg["role"], content=msg["content"]))

    user_content = f"Context:\n-----\n{context_str}\n-----\n\nQuestion: {question}"
    messages.append(ChatMessage(role="user", content=user_content))

    try:
        response = llm.stream_chat(messages)
        for token in response:
            yield token.delta or ""
    except (NotImplementedError, AttributeError):
        # Fallback to non-streaming if provider doesn't support it
        response = llm.chat(messages)
        yield response.message.content
