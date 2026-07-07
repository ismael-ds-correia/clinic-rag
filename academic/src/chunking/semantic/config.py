"""Configuração para o enriquecimento semântico."""
from dataclasses import dataclass


@dataclass
class SemanticEnricherConfig:
    """Configuração para o enriquecimento semântico."""
    max_semantic_entities: int = 10
    min_phrase_length: int = 2
    max_phrase_length: int = 6
    min_candidate_frequency: int = 1
    idf_threshold: float = 1.5  # Mínimo IDF para considerar uma entidade
    textrank_window: int = 3
    textrank_damping: float = 0.85
    textrank_iterations: int = 30
    textrank_tolerance: float = 1e-5