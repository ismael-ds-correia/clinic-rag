"""Cálculo de relevância local usando algoritmo TextRank."""
import re
from typing import List, Dict
from .config import SemanticEnricherConfig


def calculate_textrank_scores(
    text: str,
    candidates: List[str],
    config: SemanticEnricherConfig
) -> Dict[str, float]:
    """Calcula relevância local usando algoritmo TextRank.
    
    Args:
        text: Texto da seção.
        candidates: Lista de candidatos para ranquear.
        config: Configuração do enriquecedor.
    
    Returns:
        Dicionário mapeando candidato -> score TextRank.
    """
    if not candidates:
        return {}
    
    # Tokenizar texto em palavras
    words = re.findall(r'[a-záàâãéèêíïóôõöúç]+', text.lower())
    
    # Criar mapa de palavra -> índice
    word_to_idx = {word: idx for idx, word in enumerate(set(words))}
    
    # Construir grafo de co-ocorrência
    # Nós são os candidatos, arestas representam co-ocorrência em janela
    candidate_set = set(candidates)
    candidate_to_idx = {cand: idx for idx, cand in enumerate(candidates)}
    
    n = len(candidates)
    if n == 0:
        return {}
    
    # Matriz de adjacência
    adj = [[0.0] * n for _ in range(n)]
    
    # Contar co-ocorrências em janela deslizante
    for i in range(len(words)):
        window_words = words[i:i + config.textrank_window]
        
        # Encontrar candidatos na janela
        candidates_in_window = []
        for cand in candidates:
            cand_words = cand.split()
            # Verificar se todas as palavras do candidato aparecem na janela
            if all(cw in window_words for cw in cand_words):
                candidates_in_window.append(cand)
        
        # Adicionar arestas entre todos os pares na janela
        for i1, c1 in enumerate(candidates_in_window):
            for c2 in candidates_in_window[i1 + 1:]:
                idx1 = candidate_to_idx[c1]
                idx2 = candidate_to_idx[c2]
                adj[idx1][idx2] += 1.0
                adj[idx2][idx1] += 1.0
    
    # Normalizar matriz (convertendo para probabilidades de transição)
    for i in range(n):
        total = sum(adj[i])
        if total > 0:
            adj[i] = [val / total for val in adj[i]]
    
    # Inicializar scores uniformemente
    scores = [1.0 / n] * n
    
    # Iterar TextRank
    for _ in range(config.textrank_iterations):
        new_scores = [0.0] * n
        
        for i in range(n):
            rank_sum = 0.0
            for j in range(n):
                if adj[j][i] > 0:
                    rank_sum += scores[j] * adj[j][i]
            
            new_scores[i] = (1 - config.textrank_damping) / n + config.textrank_damping * rank_sum
        
        # Verificar convergência
        diff = sum(abs(new_scores[i] - scores[i]) for i in range(n))
        scores = new_scores
        if diff < config.textrank_tolerance:
            break
    
    # Normalizar scores para soma = 1
    total_score = sum(scores)
    if total_score > 0:
        scores = [s / total_score for s in scores]
    
    return {cand: scores[candidate_to_idx[cand]] for cand in candidates}