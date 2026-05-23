from llama_index.core.llms import LLM

from deep_notes.config import Settings


def get_llm(config: Settings) -> LLM:
    match config.llm_provider:
        case "openrouter":
            from llama_index.llms.openrouter import OpenRouter

            return OpenRouter(
                model=config.llm_model,
                api_key=config.openrouter_api_key,
            )
        case "openai":
            from llama_index.llms.openai import OpenAI

            return OpenAI(
                model=config.llm_model,
                api_key=config.openai_api_key,
            )
        case "ollama":
            from llama_index.llms.ollama import Ollama

            return Ollama(
                model=config.llm_model,
                base_url=config.ollama_base_url,
            )
        case _:
            raise ValueError(f"Unknown LLM provider: {config.llm_provider}")
