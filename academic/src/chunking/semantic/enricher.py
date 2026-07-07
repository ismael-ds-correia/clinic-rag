"""Enriquecedor semântico para seções de documentos clínicos."""
from typing import List, Dict, Tuple

from .config import SemanticEnricherConfig
from .extraction import extract_noun_phrases
from .textrank import calculate_textrank_scores
from .idf import calculate_global_idf, filter_by_idf
from .selection import select_final_entities


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