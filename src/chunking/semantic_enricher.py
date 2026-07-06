"""Módulo para enriquecimento semântico de seções de documentos clínicos.

Este módulo extrai entidades semânticas relevantes de cada seção utilizando:
1. Extração de candidatos via sintagmas nominais (noun phrases)
2. Ranqueamento local via TextRank
3. Filtragem global via IDF do corpus
4. Seleção final das entidades mais representativas
"""
import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple
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


def extract_noun_phrases(text: str, config: SemanticEnricherConfig) -> List[str]:
    """Extrai sintagmas nominais (noun phrases) do texto.
    
    Prioriza expressões compostas em vez de palavras isoladas.
    
    Args:
        text: Texto para extração.
        config: Configuração do enriquecedor.
    
    Returns:
        Lista de sintagmas nominais extraídos.
    """
    # Normalizar texto: lowercase e remover pontuação excessiva
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    
    # Padrões para sintagmas nominais em português
    # Captura sequências de substantivos e adjetivos
    patterns = [
        # Padrão principal: adjetivo(s) + substantivo(s) + preposições + substantivo(s)
        r'(?:[a-záàâãéèêíïóôõöúç]+(?:\s+[a-záàâãéèêíïóôõöúç]+)*)',
    ]
    
    candidates = set()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            phrase = match.group(0).strip()
            words = phrase.split()
            
            # Filtrar por tamanho da frase
            if config.min_phrase_length <= len(words) <= config.max_phrase_length:
                # Filtrar stopwords muito comuns
                if not _is_common_stopword(phrase):
                    candidates.add(phrase)
    
    # Remover frases que são subconjuntos de outras (preferir as maiores)
    candidates = _remove_subsets(candidates)
    
    return sorted(list(candidates))


def _is_common_stopword(phrase: str) -> bool:
    """Verifica se a frase é composta apenas de stopwords comuns."""
    stopwords = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
        'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
        'para', 'por', 'com', 'sem', 'sobre', 'entre',
        'e', 'ou', 'mas', 'porém', 'todavia',
        'que', 'quem', 'qual', 'quais', 'cujo', 'cuja',
        'é', 'são', 'foi', 'foram', 'ser', 'estar',
        'tem', 'têm', 'haver', 'ter',
        'este', 'esta', 'isto', 'esse', 'essa', 'isso', 'aquele', 'aquela', 'aquilo',
        'meu', 'minha', 'teu', 'tua', 'seu', 'sua', 'nosso', 'nossa',
        'muito', 'muita', 'pouco', 'pouca', 'mais', 'menos',
        'também', 'ainda', 'já', 'agora', 'hoje',
        'onde', 'quando', 'como', 'porque', 'porquê'
    }
    
    words = phrase.split()
    return all(word in stopwords for word in words)


def _remove_subsets(phrases: Set[str]) -> Set[str]:
    """Remove frases que são subconjuntos de outras frases maiores."""
    phrases_list = sorted(phrases, key=len, reverse=True)
    result = set()
    
    for phrase in phrases_list:
        phrase_words = set(phrase.split())
        is_subset = False
        
        for existing in result:
            existing_words = set(existing.split())
            if phrase_words.issubset(existing_words):
                is_subset = True
                break
        
        if not is_subset:
            result.add(phrase)
    
    return result


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


def calculate_global_idf(documents: List[List[str]]) -> Dict[str, float]:
    """Calcula IDF global para todos os candidatos do corpus.
    
    Args:
        documents: Lista de documentos, onde cada documento é uma lista de candidatos.
    
    Returns:
        Dicionário mapeando candidato -> score IDF.
    """
    if not documents:
        return {}
    
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


class SemanticEnricher:
    """Enriquecedor semântico para seções de documentos clínicos."""
    
    def __init__(self, config: SemanticEnricherConfig = None):
        """Inicializa o enriquecedor semântico.
        
        Args:
            config: Configuração opcional. Se None, usa configuração padrão.
        """
        self.config = config or SemanticEnricherConfig()
        self.idf_scores: Dict[str, float] = {}
    
    def enrich_section(self, section_content: str) -> List[str]:
        """Enriquece uma seção individual com entidades semânticas.
        
        Args:
            section_content: Conteúdo textual da seção.
        
        Returns:
            Lista de entidades semânticas da seção.
        """
        # Etapa 1: Extração de candidatos
        candidates = extract_noun_phrases(section_content, self.config)
        
        if not candidates:
            return []
        
        # Etapa 2: Ranqueamento local
        textrank_scores = calculate_textrank_scores(section_content, candidates, self.config)
        
        # Ordenar por score
        candidates_with_scores = sorted(
            textrank_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Etapa 4: Seleção final (sem filtro IDF)
        entities = select_final_entities(candidates_with_scores, self.config)
        
        return entities
    
    def enrich_sections_batch(
        self,
        sections_contents: List[str]
    ) -> Tuple[List[List[str]], Dict[str, float]]:
        """Enriquece múltiplas seções calculando IDF global do batch.
        
        Args:
            sections_contents: Lista de conteúdos das seções.
        
        Returns:
            Tupla contendo:
            - Lista de listas de entidades (uma por seção)
            - Dicionário de IDF scores calculado
        """
        # Etapa 1: Extração de candidatos para todas as seções
        all_candidates = []
        sections_candidates = []
        
        for content in sections_contents:
            candidates = extract_noun_phrases(content, self.config)
            sections_candidates.append(candidates)
            all_candidates.extend(candidates)
        
        # Etapa 3: Calcular IDF global
        self.idf_scores = calculate_global_idf(sections_candidates)
        
        # Processar cada seção
        all_entities = []
        
        for idx, content in enumerate(sections_contents):
            candidates = sections_candidates[idx]
            
            if not candidates:
                all_entities.append([])
                continue
            
            # Etapa 2: Ranqueamento local
            textrank_scores = calculate_textrank_scores(content, candidates, self.config)
            
            # Ordenar por score
            candidates_with_scores = sorted(
                textrank_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Etapa 3: Filtragem por IDF
            filtered = filter_by_idf(candidates_with_scores, self.idf_scores, self.config)
            
            # Etapa 4: Seleção final
            entities = select_final_entities(filtered, self.config)
            all_entities.append(entities)
        
        return all_entities, self.idf_scores
    
    def enrich_document_sections(
        self,
        document_sections_list: List[List[Dict]]
    ) -> List[List[Dict]]:
        """Enriquece seções de múltiplos documentos.
        
        Args:
            document_sections_list: Lista de documentos, onde cada documento é uma lista
                de dicionários de seção (cada dicionário deve ter 'content').
        
        Returns:
            Lista de documentos com seções enriquecidas (campo 'semantic_entities' adicionado).
        """
        # Coletar todos os conteúdos de seções
        all_sections_contents = []
        section_indices = []  # Para mapear de volta
        
        for doc_idx, sections in enumerate(document_sections_list):
            for sec_idx, section in enumerate(sections):
                all_sections_contents.append(section['content'])
                section_indices.append((doc_idx, sec_idx))
        
        # Enriquecer em batch com IDF global
        all_entities, idf_scores = self.enrich_sections_batch(all_sections_contents)
        
        # Adicionar entidades às seções originais
        result = []
        for doc_sections in document_sections_list:
            enriched_doc = []
            for section in doc_sections:
                enriched_section = section.copy()
                enriched_section['semantic_entities'] = []
                enriched_doc.append(enriched_section)
            result.append(enriched_doc)
        
        for (doc_idx, sec_idx), entities in zip(section_indices, all_entities):
            result[doc_idx][sec_idx]['semantic_entities'] = entities
        
        return result