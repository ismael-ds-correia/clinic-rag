"""Orquestração do pipeline completo de RAG.

Fluxo:
    pergunta do usuário
        -> decomposição em sub-perguntas
        -> recuperação (FAISS) por sub-pergunta + deduplicação
        -> geração da resposta (estritamente ancorada no contexto)
        -> auto-reflexão (documentos relevantes? resposta fundamentada e completa?)
        -> se necessário e dentro do limite de tentativas, nova busca + nova geração
        -> resposta final (com metadados de transparência: fontes, sub-perguntas,
           resultado da auto-reflexão)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

from rag import config
from rag.decomposition import decompose_question
from rag.generation import generate_answer
from rag.llm import get_llm
from rag.reflection import ReflectionResult, reflect_on_answer
from rag.retrieval import format_documents_for_prompt, retrieve_for_subquestions
from rag.vector_store import get_retriever, load_vector_store
from util.logger import setup_logger

logger = setup_logger("RAG.Pipeline")


@dataclass
class RAGComponents:
    """Componentes já inicializados do pipeline, reutilizáveis entre chamadas
    (evita recarregar o índice FAISS e o LLM a cada pergunta)."""

    llm: Any
    retriever: Any


def build_pipeline(
    index_path=config.VECTOR_STORE_INDEX_PATH,
    metadata_path=config.VECTOR_STORE_METADATA_PATH,
    top_k: int = config.RETRIEVAL_TOP_K,
) -> RAGComponents:
    """Inicializa (ou carrega) a base vetorial e o LLM uma única vez.

    A base vetorial é apenas carregada aqui — ela é construída por
    ``embedding/create_vector_db.py`` (ver ``rag.vector_store`` e
    ``rag.build_vector_store``).
    """
    vector_store = load_vector_store(index_path=index_path, metadata_path=metadata_path)
    retriever = get_retriever(vector_store, k=top_k)
    llm = get_llm()
    return RAGComponents(llm=llm, retriever=retriever)


def _sources_from_documents(documents: List[Document]) -> List[Dict[str, Any]]:
    sources = []
    seen = set()
    for doc in documents:
        source = doc.metadata.get("source", "fonte desconhecida")
        section = " > ".join(
            t.strip() for t in (doc.metadata.get("section_titles") or []) if t and t.strip()
        )
        key = (source, section)
        if key in seen:
            continue
        seen.add(key)
        sources.append({"source": source, "section": section})
    return sources


def _run_single_attempt(
    components: RAGComponents,
    question: str,
    search_query: Optional[str] = None,
) -> Dict[str, Any]:
    """Executa uma passada completa: decomposição -> recuperação -> geração
    -> reflexão, usando ``search_query`` (ou a própria pergunta) como base
    para a decomposição/recuperação."""
    query_for_retrieval = search_query or question

    sub_questions = decompose_question(components.llm, query_for_retrieval)
    documents = retrieve_for_subquestions(components.retriever, sub_questions)
    context_text = format_documents_for_prompt(documents)

    answer = generate_answer(components.llm, question, context_text)
    reflection = reflect_on_answer(components.llm, question, context_text, answer)

    return {
        "answer": answer,
        "sub_questions": sub_questions,
        "documents": documents,
        "context_text": context_text,
        "reflection": reflection,
    }


def answer_question(
    question: str,
    components: Optional[RAGComponents] = None,
    max_retries: int = config.MAX_REFLECTION_RETRIES,
) -> Dict[str, Any]:
    """Responde a uma pergunta do usuário usando o pipeline completo de RAG.

    :param question: Pergunta em português do usuário.
    :param components: Componentes já inicializados (``build_pipeline()``).
        Se omitido, são inicializados sob demanda (útil para uso pontual,
        mas ineficiente em loops — prefira reutilizar via ``build_pipeline``).
    :param max_retries: Nº máximo de novas tentativas quando a auto-reflexão
        indica que uma nova busca provavelmente ajudaria.
    :return: Dicionário com ``answer``, ``sources``, ``sub_questions``,
        ``reflection`` e ``low_confidence`` (True se, mesmo após as
        tentativas, a auto-reflexão não considerou o resultado satisfatório
        — a resposta retornada continua sendo a mais honesta possível, dado
        que o prompt de geração já instrui o modelo a admitir quando não
        sabe).
    """
    if not question or not question.strip():
        raise ValueError("A pergunta não pode ser vazia.")

    if components is None:
        components = build_pipeline()

    attempt = 0
    search_query: Optional[str] = None
    result = _run_single_attempt(components, question, search_query)

    while (
        result["reflection"].veredito == "necessita_nova_busca"
        and attempt < max_retries
    ):
        consulta_sugerida = result["reflection"].consulta_sugerida
        # Com temperature=0, refazer a mesma consulta produz exatamente o
        # mesmo resultado (determinístico) — só vale a pena tentar de novo
        # se a auto-reflexão sugeriu uma consulta efetivamente diferente.
        if not consulta_sugerida or consulta_sugerida.strip() == (search_query or question).strip():
            logger.info(
                "Auto-reflexão pediu nova busca mas não sugeriu uma consulta "
                "diferente da já usada; como temperature=0 uma nova tentativa "
                "reproduziria o mesmo resultado, encerrando aqui (resposta "
                "marcada como baixa confiança)."
            )
            break

        attempt += 1
        logger.info(
            f"Auto-reflexão sugeriu nova busca (tentativa {attempt}/{max_retries}): "
            f"'{consulta_sugerida}'"
        )
        search_query = consulta_sugerida
        result = _run_single_attempt(components, question, search_query)

    reflection: ReflectionResult = result["reflection"]
    low_confidence = reflection.veredito != "satisfatorio"

    return {
        "answer": result["answer"],
        "question": question,
        "sub_questions": result["sub_questions"],
        "sources": _sources_from_documents(result["documents"]),
        "reflection": reflection.model_dump(),
        "low_confidence": low_confidence,
        "attempts": attempt + 1,
    }