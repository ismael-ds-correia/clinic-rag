"""Módulo para enriquecimento semântico de seções de documentos clínicos.

Este módulo extrai entidades semânticas relevantes de cada seção utilizando:
1. Extração de candidatos via sintagmas nominais (noun phrases)
2. Ranqueamento local via TextRank
3. Filtragem global via IDF do corpus
4. Seleção final das entidades mais representativas
"""

from .config import SemanticEnricherConfig
from .extraction import extract_noun_phrases
from .textrank import calculate_textrank_scores
from .idf import calculate_global_idf, filter_by_idf
from .selection import select_final_entities
from .enricher import SemanticEnricher

__all__ = [
    'SemanticEnricherConfig',
    'extract_noun_phrases',
    'calculate_textrank_scores',
    'calculate_global_idf',
    'filter_by_idf',
    'select_final_entities',
    'SemanticEnricher',
]