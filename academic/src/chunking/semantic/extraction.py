"""Extração de sintagmas nominais (noun phrases) do texto."""
import re
from typing import List, Set
from .config import SemanticEnricherConfig


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