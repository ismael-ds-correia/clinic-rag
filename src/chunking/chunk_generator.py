"""Módulo para gerar chunks finais a partir de estruturas de seção."""
import json
from pathlib import Path
from typing import List, Union, Dict, Any
from dataclasses import dataclass
from section_structure import DocumentSections

@dataclass
class FinalChunk:
    """Representa um chunk final para pipeline do RAG."""
    chunk_id: str
    source: str
    section_number: str
    level: int
    title: str
    text: str
    page_start: int
    page_end: int
    metadata: Dict[str, Any]


class FinalChunkGenerator:
    """Gera chunks finais a partir de estruturas de seção temporárias."""
    
    def __init__(self, temp_dir: Union[str, Path] = None):
        """Inicializa o gerador de chunks.
        
        Args:
            temp_dir: Diretório contendo arquivos JSON de seção temporários (opcional).
        """
        self.temp_dir = Path(temp_dir) if temp_dir else None
    
    def generate_chunks(self, output_path: Union[str, Path]) -> Path:
        """Gera chunks finais a partir de todos os arquivos de seção temporários.
        
        Args:
            output_path: Caminho onde a saída JSONL será salva.
        
        Returns:
            Caminho para o arquivo JSONL gerado.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ler todos os arquivos JSON temporários, ordenados por fonte
        temp_files = sorted(self.temp_dir.glob("*.json"))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for temp_file in temp_files:
                # Ler seções do documento
                with open(temp_file, 'r', encoding='utf-8') as tf:
                    doc_data = json.load(tf)
                
                source = doc_data['source']
                
                # Gerar um chunk por seção
                for section_data in doc_data['sections']:
                    chunk = self._section_to_chunk(source, section_data)
                    f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        return output_path
    
    def _section_to_chunk(self, source: str, section_data: Dict) -> Dict:
        """Converte uma seção em um chunk final.
        
        Args:
            source: Fonte do documento.
            section_data: Dados da seção da estrutura temporária.
        
        Returns:
            Dicionário representando o chunk final.
        """
        section_number = section_data['numbering']
        
        # Construir chunk_id: source + "__" + section_number
        chunk_id = f"{source}__{section_number}"
        
        # Construir metadados
        metadata = {
            "absorbed_sections": section_data.get('absorbed_sections', []),
            "document_type": "PCDT"
        }
        
        # Opcional: hierarchy_path se disponível
        if 'hierarchy_path' in section_data:
            metadata['hierarchy_path'] = section_data['hierarchy_path']
        
        chunk = {
            "chunk_id": chunk_id,
            "source": source,
            "section_number": section_number,
            "level": section_data['level'],
            "title": section_data['title'],
            "text": section_data['content'],  # SEM modificação de texto
            "page_start": section_data['start_page'],
            "page_end": section_data['end_page'],
            "metadata": metadata
        }
        
        return chunk

    def document_sections_to_chunks(self, doc_sections: DocumentSections) -> List[Dict]:
        """Converte um objeto DocumentSections em uma lista de dicionários de chunk.
        
        Args:
            doc_sections: Instância de DocumentSections com seções para converter.
        
        Returns:
            Lista de dicionários de chunk.
        """
        chunks = []
        
        for section in doc_sections.sections:
            section_number = section.numbering
            chunk_id = f"{doc_sections.source}__{section_number}"
            
            metadata = {
                "absorbed_sections": section.absorbed_sections,
                "document_type": "PCDT"
            }
            
            chunk = {
                "chunk_id": chunk_id,
                "source": doc_sections.source,
                "section_number": section_number,
                "level": section.level,
                "title": section.title,
                "text": section.content,
                "page_start": section.start_page,
                "page_end": section.end_page,
                "metadata": metadata
            }
            
            chunks.append(chunk)
        
        return chunks