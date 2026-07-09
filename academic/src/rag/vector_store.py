"""Carregamento da base vetorial FAISS (embeddings bge-m3 via Ollama)."""
 
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
 
import faiss
import numpy as np
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_ollama import OllamaEmbeddings
 
from rag import config
from util.logger import setup_logger
 
logger = setup_logger("RAG.VectorStore")

def get_embeddings() -> OllamaEmbeddings:
    """Instancia o modelo de embeddings bge-m3, servido via Ollama."""
    return OllamaEmbeddings(
        model=config.EMBEDDING_MODEL_NAME,
        base_url=config.OLLAMA_BASE_URL,
    )

def _load_faiss_index(index_path: Path) -> faiss.Index:
    if not index_path.exists():
        raise FileNotFoundError(
            f"Índice FAISS não encontrado em {index_path}. Rode "
            "`python -m embedding.create_vector_db` antes de usar "
            "o pipeline de RAG."
        )
    logger.info(f"Carregando índice FAISS de {index_path}...")
    return faiss.read_index(str(index_path))

def _load_metadata(metadata_path: Path) -> List[Dict[str, Any]]:
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadados não encontrados em {metadata_path}. Rode "
            "`python -m embedding.create_vector_db` anstes de usar "
            "o pipeline de RAG."
        )

    with metadata_path.open("r", encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]

class FaissChunkRetriever(BaseRetriever):
    """Retriever LangChain sobre o índice FAISS bruto (``IndexFlatIP`` +
    vetores normalizados) e os metadados produzidos por
    ``embedding/create_vector_db.py``.
    """
 
    index: Any
    chunks: List[Dict[str, Any]]
    embeddings: Any
    k: int = config.RETRIEVAL_TOP_K
 
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        """Busca documentos relevantes baseados na `query` do usuário."""
        query_vector = np.array([self.embeddings.embed_query(query)], dtype="float32")

        # O índice foi construído com vetores normalizados + IndexFlatIP
        # (produto interno == similaridade de cosseno)
        faiss.normalize_L2(query_vector)
        scores, indices = self.index.search(query_vector, self.k)
 
        documents: List[Document] = []
        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
 
            chunk = self.chunks[idx]
            documents.append(
                Document(
                    page_content=chunk.get("text", ""),
                    metadata={
                        "chunk_id": chunk.get("chunk_id"),
                        "source": chunk.get("source"),
                        "section_number": chunk.get("section_number"),
                        "section_titles": chunk.get("section_titles", []),
                        "page_start": chunk.get("page_start"),
                        "page_end": chunk.get("page_end"),
                        "document_type": chunk.get("metadata", {}).get("document_type"),
                        # IndexFlatIP + vetores normalizados: maior = mais similar
                        "similarity": float(scores[0][rank]),
                    },
                )
            )
        return documents

def load_vector_store(
    index_path: Path = config.VECTOR_STORE_INDEX_PATH,
    metadata_path: Path = config.VECTOR_STORE_METADATA_PATH,
) -> Dict[str, Any]:
    """Carrega o índice FAISS e os metadados dos chunks de PCDT gerados por
    ``embedding/create_vector_db.py``.
 
    :return: Dicionário ``{"index": faiss.Index, "chunks": List[dict]}``.
    """
    index = _load_faiss_index(index_path)
    chunks = _load_metadata(metadata_path)
 
    if index.ntotal != len(chunks):
        logger.warning(
            f"Índice FAISS tem {index.ntotal} vetores, mas há {len(chunks)} "
            "registros de metadados. Verifique se ambos vêm da mesma "
            "execução de `embedding/create_vector_db.py`."
        )
 
    logger.info(f"Base vetorial carregada: {index.ntotal} vetores, {len(chunks)} chunks.")
    return {"index": index, "chunks": chunks}

def get_retriever(
    vector_store: Dict[str, Any],
    k: int = config.RETRIEVAL_TOP_K,
    embeddings: Optional[OllamaEmbeddings] = None,
) -> FaissChunkRetriever:
    """Retorna um retriever LangChain padrão (busca por similaridade) sobre
    a base vetorial carregada por ``load_vector_store``."""
    return FaissChunkRetriever(
        index=vector_store["index"],
        chunks=vector_store["chunks"],
        embeddings=embeddings or get_embeddings(),
        k=k,
    )