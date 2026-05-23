import re
from pathlib import Path

import yaml
from llama_index.core import Document, StorageContext, VectorStoreIndex

from deep_notes.config import Settings, get_settings
from deep_notes.components.chunking import get_splitter
from deep_notes.components.embeddings import get_embed_model
from deep_notes.components.vector_store import get_vector_store

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and return (metadata_dict, body_text)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    body = text[match.end() :]
    return meta, body


def load_vault(vault_path: str) -> list[Document]:
    """Load all .md files from a vault directory into LlamaIndex Documents."""
    vault = Path(vault_path)
    if not vault.is_dir():
        raise FileNotFoundError(f"Vault path not found: {vault_path}")

    documents = []
    for md_file in sorted(vault.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_frontmatter(text)

        if not body.strip():
            continue

        # Build metadata
        doc_meta = {
            "file_name": md_file.name,
            "file_path": str(md_file.relative_to(vault)),
        }
        tags = meta.get("tags", [])
        if isinstance(tags, list):
            doc_meta["tags"] = tags
        elif isinstance(tags, str):
            doc_meta["tags"] = [t.strip() for t in tags.split(",")]

        documents.append(Document(text=body, metadata=doc_meta))

    return documents


def run_ingest(config: Settings | None = None) -> int:
    """Run the full ingestion pipeline. Returns number of documents indexed."""
    if config is None:
        config = get_settings()

    if not config.vault_path:
        raise ValueError("VAULT_PATH is not set")

    print(f"Loading vault from: {config.vault_path}")
    documents = load_vault(config.vault_path)
    print(f"Found {len(documents)} documents")

    if not documents:
        print("No documents to index.")
        return 0

    splitter = get_splitter(config)
    embed_model = get_embed_model(config)
    vector_store = get_vector_store(config)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Indexing documents...")
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[splitter],
        show_progress=True,
    )

    print("Ingestion complete.")
    return len(documents)


if __name__ == "__main__":
    run_ingest()
