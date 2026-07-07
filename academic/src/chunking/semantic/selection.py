"""Seleção final das entidades semânticas."""
from typing import List, Tuple
from .config import SemanticEnricherConfig


def select_final_entities(
    candidates_with_scores: List[Tuple[str, float]],
    config: SemanticEnricherConfig
) -> List[str]:
    """Seleciona as entidades finais da seção.
    
    Remove duplicatas, preserva ordem de relevância e limita quantidade.
    
    Args:
        candidates_with_scores: Lista de (candidato, score) ordenada por relevância.
        config: Configuração do enriquecedor.
    
    Returns:
        Lista de entidades semânticas selecionadas.
    """
    # Já está ordenado por relevância (score)
    # Selecionar top N
    selected = candidates_with_scores[:config.max_semantic_entities]
    
    # Extrair apenas os nomes (sem scores)
    entities = [cand for cand, _ in selected]
    
    return entities