"""Geração da resposta final, estritamente ancorada no contexto recuperado."""

from rag.prompts import ANSWER_PROMPT
from util.logger import setup_logger

logger = setup_logger("RAG.Generation")


def generate_answer(llm, question: str, context_text: str) -> str:
    """Gera a resposta em português, usando somente o contexto fornecido.

    :param llm: LLM (ChatOllama) já configurado com temperature=0.
    :param question: Pergunta do usuário.
    :param context_text: Texto formatado dos chunks recuperados
        (ver ``retrieval.format_documents_for_prompt``).
    :return: Resposta gerada pelo modelo, em português.
    """
    chain = ANSWER_PROMPT | llm

    logger.info("Gerando resposta com base no contexto recuperado...")
    result = chain.invoke({"question": question, "context": context_text})

    answer = result.content if hasattr(result, "content") else str(result)
    return answer.strip()