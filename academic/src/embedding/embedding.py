"""This module contains the embeddings classes for the academic project."""

from langchain_huggingface import HuggingFaceEmbeddings
from util.logger import setup_logger
from typing import List, Dict, Any
from pathlib import Path
from tqdm import tqdm
import json

# === Initialize the logger for this module ===
logger = setup_logger("DataEmbedding")

class DataEmbedding:
    """
    Base class for data embeddings.
    Author: Carlos Alberto da Silva Neto
    """

    def __init__(self, input_chunks_file: str | Path = "data/input_chunks.jsonl", output_file: str | Path = "data/embeddings.jsonl") -> None:
        """
        Main constructor of the DataEmbedding class.

        :param input_chunks_file: Path to the input JSONL file containing chunks.
        :param output_file: Path to the output JSONL file where embeddings will be saved.
        """
        if not isinstance(input_chunks_file, (str, Path)):
            logger.error("Invalid input_chunks_file type.")
            raise TypeError("input_chunks_file must be a string or Path object.")
        
        if not isinstance(output_file, (str, Path)):
            logger.error("Invalid output_file type.")
            raise TypeError("output_file must be a string or Path object.")

        self.input_chunks_file = Path(input_chunks_file)
        self.output_file = Path(output_file)
        self.embedding_model = None

        logger.info(f"DataEmbedding configured successfully!")

    def _initialize_embedding_model(self) -> None:
        """
        Initializes the embedding model on the GPU.
        """
        if self.embedding_model is not None:
            return
        
        logger.info("Initializing the embedding model on CUDA...")
        try:
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="BAAI/bge-m3",
                model_kwargs={"device": "cuda"},
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info("Embedding model initialized successfully!")
        except Exception as error:
            logger.error(f"Failed to initialize the embedding model: {error}")
            raise

    def _read_chunks(self) -> List[Dict[str, Any]]:
        """
        Reads the chunks from the JSONL file.
        """
        if not self.input_chunks_file.exists():
            logger.error(f"File not found: {self.input_chunks_file}")
            return []
        
        with self.input_chunks_file.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def execute_pipeline(self) -> None:
        """
        Orchestrates the embedding generation process.
        """
        chunks = self._read_chunks()
        if not chunks:
            return

        self._initialize_embedding_model()
        
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self.output_file.open("w", encoding="utf-8") as out_f:
            batch_size = 16
            for i in tqdm(range(0, len(chunks), batch_size)):
                batch = chunks[i:i + batch_size]
                texts = [
                    f'Documento: {item.get("source", "Desconhecido")}. ' 
                    f'Seções: {" - ".join(item.get("section_titles", []))}. ' 
                    f'Entidades: {"; ".join(item.get("section_entities", []))}. ' 
                    f'Conteúdo: {item.get("text", "")}' 
                    for item in batch
                ]
                
                vectors = self.embedding_model.embed_documents(texts)
                
                for j, item in enumerate(batch):
                    original_source = item.get("source", "")
                    item["source"] = Path(original_source).stem

                    item["embedding"] = vectors[j]
                    out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        logger.info("Pipeline completed successfully!")


if __name__ == "__main__":
    INPUT_CHUNKS_PATH = "../data/chunks/chunks.jsonl"
    OUTPUT_EMBEDDINGS_PATH = "../data/embeddings/embeddings.jsonl"

    logger.info(f"Starting the embedding pipeline...")

    try:
        data_embedding = DataEmbedding(input_chunks_file=INPUT_CHUNKS_PATH, output_file=OUTPUT_EMBEDDINGS_PATH)
        data_embedding.execute_pipeline()
    
    except Exception as error:
        logger.error(f"An error occurred during the embedding pipeline: {error}")
        