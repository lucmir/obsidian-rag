import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from deep_notes.components.vector_store import clear_collection
from deep_notes.config import get_settings
from deep_notes.ingest import run_ingest
from deep_notes.query import retrieve, stream_answer

defaults = get_settings()

st.set_page_config(page_title="Deep Notes", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    /* Main content top padding */
    .stMainBlockContainer, .block-container {
        padding-top: 1.5rem !important;
    }
    /* Match sidebar top padding to main content */
    .stSidebar .stSidebarContent,
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    /* Force sidebar visible and hide collapse */
    section[data-testid="stSidebar"] {
        display: flex !important;
        width: 21rem !important;
        min-width: 21rem !important;
        transform: none !important;
        margin-left: 0 !important;
    }
    /* Make success/error alerts full width in sidebar */
    section[data-testid="stSidebar"] [data-testid="stAlert"] {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("#### Deep Notes — Obsidian RAG")

EMBED_PROVIDERS = ["ollama", "openai"]
LLM_PROVIDERS = ["openrouter", "openai", "ollama"]
CHUNK_STRATEGIES = ["sentence", "token", "markdown"]

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources_history" not in st.session_state:
    st.session_state.sources_history = []

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")

    vault_path = st.text_input("Vault path", value=defaults.vault_path, help="Path to your Obsidian vault folder")

    st.subheader("Embedding")
    embed_provider = st.selectbox("Provider", EMBED_PROVIDERS, index=EMBED_PROVIDERS.index(defaults.embed_provider))
    embed_model = st.text_input("Model", value=defaults.embed_model)

    st.subheader("Chunking")
    chunk_strategy = st.selectbox("Strategy", CHUNK_STRATEGIES, index=CHUNK_STRATEGIES.index(defaults.chunk_strategy))
    chunk_size = st.number_input("Chunk size", value=defaults.chunk_size, min_value=64, max_value=4096)
    chunk_overlap = st.number_input("Chunk overlap", value=defaults.chunk_overlap, min_value=0, max_value=512)

    st.subheader("Retrieval")
    similarity_top_k = st.slider("Top K results", min_value=1, max_value=20, value=defaults.similarity_top_k)

    st.subheader("LLM")
    llm_provider = st.selectbox("Provider ", LLM_PROVIDERS, index=LLM_PROVIDERS.index(defaults.llm_provider))
    llm_model = st.text_input("Model ", value=defaults.llm_model)

    st.divider()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources_history = []
        st.rerun()

    col1, col2 = st.columns(2, gap="small")
    with col1:
        index_clicked = st.button("Index Vault", type="primary", disabled=not vault_path, use_container_width=True)
    with col2:
        clear_index_clicked = st.button("Clear Index", use_container_width=True, disabled=not vault_path)

    if index_clicked:
        config = get_settings(
            vault_path=vault_path,
            embed_provider=embed_provider,
            embed_model=embed_model,
            chunk_strategy=chunk_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            llm_provider=llm_provider,
            llm_model=llm_model,
            similarity_top_k=similarity_top_k,
        )
        with st.spinner("Indexing vault..."):
            try:
                count = run_ingest(config)
                st.success(f"Indexed {count} documents.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")

    if clear_index_clicked:
        config = get_settings(vault_path=vault_path)
        try:
            clear_collection(config)
            st.success(f"Cleared collection: {config.collection_name}")
        except Exception as e:
            st.error(f"Clear failed: {e}")


def get_config():
    return get_settings(
        vault_path=vault_path,
        embed_provider=embed_provider,
        embed_model=embed_model,
        chunk_strategy=chunk_strategy,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        llm_provider=llm_provider,
        llm_model=llm_model,
        similarity_top_k=similarity_top_k,
    )


def render_sources(sources, vault_path):
    if not sources:
        return
    vault_name = Path(vault_path).name
    st.markdown("**Sources:**")
    for i, source in enumerate(sources, 1):
        score_str = f"(score: {source.score:.3f})" if source.score else ""
        with st.expander(f"{i}. {source.file_name} {score_str}"):
            file_stem = source.file_path.removesuffix(".md")
            obsidian_url = f"obsidian://open?vault={quote(vault_name)}&file={quote(file_stem)}"
            st.caption(f"Path: `{source.file_path}` | [Open in Obsidian]({obsidian_url})")
            st.markdown(source.text)


# --- Chat history ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i < len(st.session_state.sources_history):
            render_sources(st.session_state.sources_history[i], vault_path)

# --- Chat input ---
if question := st.chat_input("Ask a question about your notes"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    config = get_config()

    # Retrieve relevant chunks
    with st.spinner("Searching notes..."):
        try:
            retrieval = retrieve(question, config)
        except Exception as e:
            st.error(f"Retrieval failed: {e}")
            st.stop()

    # Stream LLM response
    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=False) as status:
            stream = stream_answer(
                question=question,
                context_str=retrieval.context_str,
                chat_history=st.session_state.messages[:-1],
                config=config,
            )
            # Buffer first token to detect errors before streaming
            try:
                first = next(stream)
            except StopIteration:
                first = ""
            except Exception as e:
                st.error(f"Generation failed: {e}")
                st.stop()
            status.update(label="Generating...", state="complete")

        def _stream_with_first():
            yield first
            yield from stream

        try:
            response = st.write_stream(_stream_with_first())
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

        render_sources(retrieval.sources, vault_path)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.sources_history.append(retrieval.sources)
