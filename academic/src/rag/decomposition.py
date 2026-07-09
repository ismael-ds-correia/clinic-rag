"""Decomposição da pergunta do usuário em sub-perguntas (prompt decomposition).

Perguntas compostas (ex.: "Quais os critérios diagnósticos e o tratamento
de primeira linha para a Doença de Gaucher?") tendem a recuperar documentos
melhores quando quebradas em sub-perguntas mais objetivas, cada uma buscada
separadamente na base vetorial.
"""

from typing import List

from pydantic import BaseModel, Field

from rag import config
from rag.prompts import DECOMPOSITION_PROMPT
from rag.structured_output import invoke_structured
from util.logger import setup_logger

logger = setup_logger("RAG.Decomposition")


class SubQuestions(BaseModel):
    """Lista de sub-perguntas em que a pergunta original foi decomposta."""

    sub_questions: List[str] = Field(
        description=(
            "Lista com 1 a "
            f"{config.MAX_SUBQUESTIONS} sub-perguntas objetivas, "
            "autossuficientes e em português do Brasil."
        )
    )


def decompose_question(
    llm,
    question: str,
    max_subquestions: int = config.MAX_SUBQUESTIONS,
) -> List[str]:
    """Decompõe a pergunta do usuário em sub-perguntas objetivas.

    Sempre retorna pelo menos a pergunta original (fallback seguro caso a
    decomposição estruturada falhe).

    :param llm: LLM (ChatOllama) já configurado com temperature=0.
    :param question: Pergunta original do usuário, em português.
    :param max_subquestions: Número máximo de sub-perguntas permitidas.
    :return: Lista de sub-perguntas (>= 1).
    """
    default = SubQuestions(sub_questions=[question])

    result = invoke_structured(
        llm=llm,
        prompt=DECOMPOSITION_PROMPT,
        pydantic_model=SubQuestions,
        prompt_variables={
            "question": question,
            "max_subquestions": max_subquestions,
        },
        default=default,
    )

    sub_questions = [q.strip() for q in result.sub_questions if q and q.strip()]

    if not sub_questions:
        logger.warning("Decomposição retornou lista vazia; usando a pergunta original.")
        sub_questions = [question]

    sub_questions = sub_questions[:max_subquestions]

    logger.info(f"Pergunta decomposta em {len(sub_questions)} sub-pergunta(s): {sub_questions}")
    return sub_questions