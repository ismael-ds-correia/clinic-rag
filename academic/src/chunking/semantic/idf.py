"""Cálculo de IDF global e filtragem por IDF."""
import math
from typing import List, Dict, Tuple
from .config import SemanticEnricherConfig


def calculate_global_idf(documents: List[List[str]]) -> Dict[str, float]:
    """Calcula IDF global para todos os candidatos do corpus.
    
    Args:
        documents: Lista de documentos, onde cada documento é uma lista de candidatos.
    
    Returns:
        Dicionário mapeando candidato -> score IDF.
    """
    if not documents:
        return {}
    
    from collections import Counter
    
    # Contar em quantos documentos cada candidato aparece
    doc_freq = Counter()
    
    for doc_candidates in documents:
        unique_candidates = set(doc_candidates)
        for cand in unique_candidates:
            doc_freq[cand] += 1
    
    n_docs = len(documents)
    idf_scores = {}
    
    for cand, freq in doc_freq.items():
        # IDF = log(N / df)
        idf = math.log(n_docs / freq) if freq > 0 else 0
        idf_scores[cand] = idf
    
    return idf_scores


def filter_by_idf(
    candidates_with_scores: List[Tuple[str, float]],
    idf_scores: Dict[str, float],
    config: SemanticEnricherConfig
) -> List[Tuple[str, float]]:
    """Filtra candidatos por IDF global.
    
    Remove candidatos com IDF abaixo do threshold (muito frequentes no corpus).
    
    Args:
        candidates_with_scores: Lista de (candidato, score local).
        idf_scores: Dicionário de IDF global.
        config: Configuração do enriquecedor.
    
    Returns:
        Lista filtrada de (candidato, score local).
    """
    filtered = []
    
    for cand, score in candidates_with_scores:
        idf = idf_scores.get(cand, 0)
        if idf >= config.idf_threshold:
            filtered.append((cand, score))
    
    return filtered