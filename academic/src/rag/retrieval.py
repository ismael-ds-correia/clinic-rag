"""Recuperação de documentos (chunks de PCDT) relevantes para uma pergunta."""

from typing import List

from langchain_core.documents import Document

from rag import config
from util.logger import setup_logger

logger = setup_logger("RAG.Retrieval")


def retrieve_for_subquestions(
    retriever,
    sub_questions: List[str],
    max_context_chunks: int = config.MAX_CONTEXT_CHUNKS,
) -> List[Document]:
    """Recupera documentos para cada sub-pergunta e mescla os resultados,
    removendo duplicatas (mesmo ``chunk_id``/conteúdo) e limitando o total
    de chunks enviados ao LLM.

    :param retriever: Retriever LangChain (ex.: `vector_store.as_retriever()`).
    :param sub_questions: Lista de sub-perguntas geradas pela decomposição.
    :param max_context_chunks: Número máximo de chunks únicos retornados.
    :return: Lista de ``Document`` deduplicada, na ordem de recuperação.
    """
    seen_ids = set()
    merged_documents: List[Document] = []

    for sub_question in sub_questions:
        try:
            docs = retriever.invoke(sub_question)
        except Exception as error:
            logger.error(f"Falha ao recuperar documentos para '{sub_question}': {error}")
            continue

        for doc in docs:
            dedup_key = doc.metadata.get("chunk_id") or doc.page_content
            if dedup_key in seen_ids:
                continue
            seen_ids.add(dedup_key)
            merged_documents.append(doc)

    if len(merged_documents) > max_context_chunks:
        logger.info(
            f"{len(merged_documents)} chunks únicos recuperados; "
            f"limitando aos {max_context_chunks} primeiros para o contexto."
        )
        merged_documents = merged_documents[:max_context_chunks]

    logger.info(f"Total de chunks usados como contexto: {len(merged_documents)}")
    return merged_documents


def format_documents_for_prompt(documents: List[Document]) -> str:
    """Formata os documentos recuperados em um bloco de texto legível para
    o LLM, identificando claramente a fonte de cada trecho."""
    if not documents:
        return "(Nenhum documento relevante foi encontrado na base de PCDT.)"

    blocks = []
    for idx, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "fonte desconhecida")
        section_titles = doc.metadata.get("section_titles") or []
        section_label = " > ".join(t.strip() for t in section_titles if t and t.strip())

        header = f"[Trecho {idx}] Fonte: {source}"
        if section_label:
            header += f" | Seção: {section_label}"

        blocks.append(f"{header}\n{doc.page_content.strip()}")

    return "\n\n".join(blocks)