"""Configuração central do pipeline de RAG.
 
Todas as demais partes do pacote ``rag`` importam suas constantes daqui, de
modo que caminhos, nomes de modelo e parâmetros de recuperação fiquem
definidos em um único lugar.
"""

import os
import sys
from pathlib import Path

# Garante que academic/src esteja no sys.path.
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Caminhos dos dados.
BASE_DIR = SRC_DIR.parent  # academic/
CHUNKS_PATH = BASE_DIR / "data" / "chunks" / "chunks.jsonl"

VECTOR_STORE_DIR = BASE_DIR / "data" / "embeddings"
VECTOR_STORE_INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
VECTOR_STORE_METADATA_PATH = VECTOR_STORE_DIR / "metadata.jsonl"


# Modelo de embeddings (bge-m3, servido via Ollama).
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "bge-m3")

# LLM (Qwen 3.5, servido via Ollama)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen3.5:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# Temperatura mantém-se em 0 para garantir respostas determinísticas
# sempre de acordo com os documentos.
LLM_TEMPERATURE = 0
LLM_NUM_CTX = int(os.getenv("LLM_NUM_CTX", "8192"))
LLM_NUM_PREDICT = int(os.getenv("LLM_NUM_PREDICT", "2048"))

# Número de chunks recuperados por sub-pergunta na decomposição.
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))

#Número máximo de chunks enviados como contexto.
MAX_CONTEXT_CHUNKS = int(os.getenv("MAX_CONTEXT_CHUNKS", "5"))

# Número máximo de sub-perguntas geradas pela decomposição.
MAX_SUBQUESTIONS = int(os.getenv("MAX_SUBQUESTIONS", "4"))

# Quantas vezes o pipeline pode tentar gerar uma resposta novamente
# após o self-reflection apontar um problema.
MAX_REFLECTION_RETRIES = int(os.getenv("MAX_REFLECTION_RETRIES", "1"))