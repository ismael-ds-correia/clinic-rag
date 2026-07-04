"""Estruturas de dados para o pipeline de detecção de seções."""
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Section:
    """Representa uma seção detectada em um documento."""
    source: str
    section_order: int
    numbering: str
    level: int
    title: str
    content: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    absorbed_sections: List[str] = field(default_factory=list)

@dataclass
class DocumentSections:
    """Representa todas as seções de um documento."""
    source: str
    sections: List[Section] = field(default_factory=list)
    
    def add_section(self, section: Section) -> None:
        """Adiciona uma seção ao documento."""
        self.sections.append(section)
    
    def merge_small_sections(self, min_chars: int = 750) -> None:
        """Mescla seções menores que min_chars na seção válida anterior.
        
        Args:
            min_chars: Limite mínimo de caracteres para seções independentes.
        """
        if len(self.sections) <= 1:
            return
        
        merged_sections = []
        i = 0
        
        while i < len(self.sections):
            current = self.sections[i]
            
            # Verifica se a seção atual é muito pequena
            if len(current.content) < min_chars and merged_sections:
                # Mescla na seção anterior
                previous = merged_sections[-1]
                previous.content += current.content
                previous.absorbed_sections.append(current.numbering)
                
                # Atualiza end_page se a atual tiver
                if current.end_page is not None:
                    previous.end_page = current.end_page
            else:
                # Mantém a seção como está
                merged_sections.append(current)
            
            i += 1
        
        self.sections = merged_sections