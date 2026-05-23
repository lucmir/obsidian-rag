from llama_index.core.node_parser import NodeParser, SentenceSplitter, TokenTextSplitter, MarkdownNodeParser

from deep_notes.config import Settings


def get_splitter(config: Settings) -> NodeParser:
    match config.chunk_strategy:
        case "sentence":
            return SentenceSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
            )
        case "token":
            return TokenTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
            )
        case "markdown":
            return MarkdownNodeParser()
        case _:
            raise ValueError(f"Unknown chunk strategy: {config.chunk_strategy}")
