"""Fábrica do modelo de linguagem (Qwen 3.5, via Ollama) usado no pipeline."""

from langchain_ollama import ChatOllama

from rag import config
from util.logger import setup_logger

logger = setup_logger("RAG.LLM")

def get_llm(model_name: str | None = None, temperature: float | None = None) -> ChatOllama:
    """Cria uma instância do LLM usada pelo pipeline de RAG.

    :param model_name: Nome do modelo no Ollama. Padrão: ``config.LLM_MODEL_NAME``.
    :param temperature: Temperatura de geração. Deve permanecer 0 para manter
        respostas determinísticas e fiéis aos documentos; o parâmetro existe
        apenas para permitir override explícito em testes.
    :return: Instância configurada de ``ChatOllama``.
    """
    resolved_model = model_name or config.LLM_MODEL_NAME
    resolved_temperature = config.LLM_TEMPERATURE if temperature is None else temperature

    logger.info(
        f"Inicializando LLM '{resolved_model}' (temperature={resolved_temperature}) "
        f"em {config.OLLAMA_BASE_URL}..."
    )

    return ChatOllama(
        model=resolved_model,
        base_url=config.OLLAMA_BASE_URL,
        temperature=resolved_temperature,
        reasoning=False,
        num_ctx=config.LLM_NUM_CTX,
        num_predict=config.LLM_NUM_PREDICT
    )