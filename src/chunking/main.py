"""Script principal de orquestração para detecção de seções e pipeline de chunking final."""
from pathlib import Path
import json

from jsonl_reader import JSONLReader
from document_reconstructor import DocumentReconstructor
from section_detector import SectionDetector
from section_structure import DocumentSections
from chunk_generator import FinalChunkGenerator
from typing import Union, Optional

def main(
    jsonl_path: Union[str, Path],
    chunks_output_path: Union[str, Path],
    max_sources: Optional[int] = None
) -> None:
    """Executa o pipeline completo: detecção de seções + chunking final (sem arquivos temporários).
    
    Args:
        jsonl_path: Caminho para o arquivo JSONL de entrada.
        chunks_output_path: Caminho onde os chunks JSONL finais serão salvos.
        max_sources: Número máximo de fontes para processar.
                    Se None ou <= 0, processa todas as fontes.
    """
    print(f"Iniciando pipeline completo (detecção de seções + chunking)...")
    print(f"Entrada: {jsonl_path}")
    print(f"Chunks finais: {chunks_output_path}")
    print(f"Máximo de fontes: {max_sources if max_sources else 'todas'}")
    
    # Inicializando componentes
    reader = JSONLReader(jsonl_path)
    reconstructor = DocumentReconstructor()
    detector = SectionDetector()
    chunk_generator = FinalChunkGenerator(None)  # temp_dir not needed anymore
    
    # Read and group documents
    print("\nLendo e agrupando documentos...")
    grouped_docs = reader.group_by_source(max_sources)
    print(f"Encontrados {len(grouped_docs)} documentos para processar")
    
    # Accumulate all chunks in memory
    all_chunks = []
    
    # Process each document
    for idx, (source, pages) in enumerate(grouped_docs.items(), 1):
        print(f"\n[{idx}/{len(grouped_docs)}] Processando: {source}")
        print(f"  Páginas: {len(pages)}")
        
        # Reconstruct document
        full_text, page_offset_map = reconstructor.reconstruct(pages)
        print(f"  Comprimento do texto reconstruído: {len(full_text)} caracteres")
        
        # Detect sections
        sections = detector.detect_sections(full_text, source, page_offset_map)
        print(f"  Seções detectadas: {len(sections)}")
        
        # Create document sections structure
        doc_sections = DocumentSections(source=source)
        for section in sections:
            doc_sections.add_section(section)
        
        # Merge small sections (< 750 characters)
        doc_sections.merge_small_sections(min_chars=750)
        print(f"  Seções após fusão: {len(doc_sections.sections)}")
        
        # Convert sections to chunks directly in memory
        chunks = chunk_generator.document_sections_to_chunks(doc_sections)
        all_chunks.extend(chunks)
        print(f"  Chunks gerados: {len(chunks)}")
    
    # Salva todos os chunks no arquivo JSONL
    print(f"\nSalvando {len(all_chunks)} chunks em: {chunks_output_path}")
    chunks_output_path = Path(chunks_output_path)
    chunks_output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(chunks_output_path, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
    
    print(f"\nPipeline completo finalizado com sucesso!")
    print(f"Total de chunks gerados: {len(all_chunks)}")
    print(f"Chunks finais salvos em: {chunks_output_path}")


if __name__ == "__main__":
    JSONL_PATH = "data/processed/documents.jsonl"
    CHUNKS_OUTPUT_PATH = "data/chunks/chunks.jsonl"
    MAX_SOURCES = None  # Alterar para None irá processar todos os documentos
    
    main(
        jsonl_path=JSONL_PATH,
        chunks_output_path=CHUNKS_OUTPUT_PATH,
        max_sources=MAX_SOURCES
    )