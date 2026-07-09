"""Utilitário para obter saídas estruturadas (JSON) de um LLM local via
Ollama de forma robusta.
"""

import re
from typing import Type, TypeVar

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from util.logger import setup_logger

logger = setup_logger("RAG.StructuredOutput")

T = TypeVar("T", bound=BaseModel)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json_block(text: str) -> str:
    """Extrai o maior bloco `{...}` de um texto, tolerando texto extra que
    o modelo eventualmente adicione antes/depois do JSON."""
    match = _JSON_BLOCK_RE.search(text)
    if not match:
        raise ValueError(f"Nenhum bloco JSON encontrado na saída do modelo: {text!r}")
    return match.group(0)


def invoke_structured(
    llm,
    prompt: ChatPromptTemplate,
    pydantic_model: Type[T],
    prompt_variables: dict,
    default: T,
) -> T:
    """Invoca o LLM com um prompt que pede JSON e faz o parsing para
    ``pydantic_model``. Em caso de falha (JSON inválido, campos faltando,
    etc.), tenta uma vez mais pedindo explicitamente uma correção; se ainda
    assim falhar, retorna ``default`` e loga o problema, para nunca quebrar
    o pipeline por causa de uma saída malformada do LLM.
    """
    parser = PydanticOutputParser(pydantic_object=pydantic_model)
    variables = {**prompt_variables, "format_instructions": parser.get_format_instructions()}

    chain = prompt | llm

    raw_output = chain.invoke(variables)
    raw_text = raw_output.content if hasattr(raw_output, "content") else str(raw_output)

    try:
        json_block = _extract_json_block(raw_text)
        return parser.parse(json_block)
    except Exception as first_error:
        logger.warning(
            f"Falha ao parsear saída estruturada ({pydantic_model.__name__}): "
            f"{first_error}. Tentando corrigir..."
        )

    # Segunda tentativa: pede explicitamente para corrigir e reenviar só o JSON.
    try:
        correction_prompt = (
            "A resposta a seguir deveria ser um JSON válido no formato "
            f"especificado, mas não é:\n\n{raw_text}\n\n"
            f"Reenvie APENAS o JSON corrigido, seguindo este formato:\n"
            f"{parser.get_format_instructions()}"
        )
        correction_output = llm.invoke(correction_prompt)
        correction_text = (
            correction_output.content
            if hasattr(correction_output, "content")
            else str(correction_output)
        )
        json_block = _extract_json_block(correction_text)
        return parser.parse(json_block)
    except Exception as second_error:
        logger.error(
            f"Não foi possível obter saída estruturada válida para "
            f"{pydantic_model.__name__} mesmo após correção: {second_error}. "
            "Usando valor padrão."
        )
        return default