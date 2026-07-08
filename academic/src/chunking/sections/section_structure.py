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
    absorbed_section_titles: List[str] = field(default_factory=list)
    semantic_entities: List[str] = field(default_factory=list)

@dataclass
class DocumentSections:
    """Representa todas as seções de um documento."""
    source: str
    sections: List[Section] = field(default_factory=list)
    
    def add_section(self, section: Section) -> None:
        """Adiciona uma seção ao documento."""
        self.sections.append(section)
    
    def merge_small_sections(self, min_chars: int = 750) -> None:
        if len(self.sections) <= 1:
            return
        
        merged_sections = []
        i = 0
        
        while i < len(self.sections):
            current = self.sections[i]
            
            # Verifica se a seção atual é muito pequena
            if len(current.content) < min_chars and merged_sections:
                # Mescla na seção anterior (backward merge)
                previous = merged_sections[-1]
                previous.absorbed_sections.append(current.numbering)
                previous.absorbed_section_titles.append(current.title)
                
                # Atualiza end_page se a atual tiver
                if current.end_page is not None:
                    previous.end_page = current.end_page
            elif len(current.content) < min_chars and not merged_sections:
                # Primeira seção pequena: absorve a próxima seção (forward merge)
                if i + 1 < len(self.sections):
                    next_section = self.sections[i + 1]
                    current.content += "\n" + next_section.content
                    current.absorbed_sections.append(next_section.numbering)
                    current.absorbed_section_titles.append(next_section.title)
                    if next_section.end_page is not None:
                        current.end_page = next_section.end_page
                    i += 1  # Pula a próxima seção já absorvida
                merged_sections.append(current)
            else:
                # Mantém a seção como está
                merged_sections.append(current)
            
            i += 1
        
        self.sections = merged_sections
        