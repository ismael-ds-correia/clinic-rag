"""Auto-reflexão (self-reflection): avalia se os documentos recuperados são
relevantes e se a resposta gerada está fundamentada e completa.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from rag.prompts import REFLECTION_PROMPT
from rag.structured_output import invoke_structured
from util.logger import setup_logger

logger = setup_logger("RAG.Reflection")

Verdict = Literal["satisfatorio", "contexto_insuficiente", "necessita_nova_busca"]


class ReflectionResult(BaseModel):
    """Avaliação crítica de uma resposta gerada pelo pipeline de RAG."""

    documentos_relevantes: bool = Field(
        description="Se os documentos recuperados são relevantes para a pergunta."
    )

    resposta_fundamentada: bool = Field(
        description=(
            "Se toda afirmação da resposta está apoiada pelo contexto "
            "(uma resposta que corretamente diz 'não sei' conta como fundamentada)."
        )
    )

    resposta_completa: bool = Field(
        description="Se a resposta cobre todos os aspectos da pergunta que o contexto permite cobrir."
    )

    veredito: Verdict = Field(
        description=(
            "'satisfatorio' se está tudo certo; 'contexto_insuficiente' se os "
            "documentos não bastam mas a resposta já reflete isso honestamente "
            "(nesse caso não adianta buscar de novo); 'necessita_nova_busca' se "
            "uma nova recuperação com outra consulta provavelmente ajudaria."
        )
    )

    justificativa: str = Field(description="Breve explicação do veredito, em português.")
    consulta_sugerida: Optional[str] = Field(
        default=None,
        description=(
            "Se veredito == 'necessita_nova_busca', uma nova consulta de busca "
            "sugerida para tentar recuperar documentos melhores. Caso contrário, null."
        ),
    )


def reflect_on_answer(
    llm,
    question: str,
    context_text: str,
    answer: str,
) -> ReflectionResult:
    """Executa a etapa de auto-reflexão sobre a resposta gerada.

    :param llm: LLM (ChatOllama) já configurado com temperature=0.
    :param question: Pergunta original do usuário.
    :param context_text: Contexto formatado usado na geração da resposta.
    :param answer: Resposta gerada pelo pipeline.
    :return: ``ReflectionResult`` com o veredito da avaliação.
    """
    default = ReflectionResult(
        documentos_relevantes=False,
        resposta_fundamentada=False,
        resposta_completa=False,
        veredito="necessita_nova_busca",
        justificativa=(
            "Não foi possível executar a auto-reflexão automaticamente "
            "(falha ao obter avaliação estruturada do LLM); marcando como "
            "baixa confiança por segurança, em vez de assumir sucesso."
        ),
        consulta_sugerida=None,
    )

    result = invoke_structured(
        llm=llm,
        prompt=REFLECTION_PROMPT,
        pydantic_model=ReflectionResult,
        prompt_variables={
            "question": question,
            "context": context_text,
            "answer": answer,
        },
        default=default,
    )

    logger.info(
        f"Auto-reflexão: veredito='{result.veredito}' "
        f"(documentos_relevantes={result.documentos_relevantes}, "
        f"resposta_fundamentada={result.resposta_fundamentada}, "
        f"resposta_completa={result.resposta_completa})"
    )
    return result