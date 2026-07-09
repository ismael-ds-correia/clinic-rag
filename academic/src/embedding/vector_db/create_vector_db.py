import json
from pathlib import Path

import faiss
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[2]

EMBEDDINGS_PATH = BASE_DIR / "data" / "embeddings" / "embeddings.jsonl"
OUTPUT_DIR = BASE_DIR / "data" / "embeddings"

INDEX_PATH = OUTPUT_DIR / "index.faiss"
METADATA_PATH = OUTPUT_DIR / "metadata.jsonl"


def load_embeddings():
    embeddings = []

    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            embeddings.append(item)

    return embeddings


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = load_embeddings()

    print(f"Carregando {len(embeddings)} embeddings pré-calculados...")

    vectors = np.array([item["embedding"] for item in embeddings], dtype=np.float32)
    metadata = [{key: value for key, value in item.items() if key != "embedding"} 
    for item in embeddings]

    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, str(INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        for item in metadata:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("Base vetorial criada com sucesso!")
    print(f"Índice FAISS: {INDEX_PATH}")
    print(f"Metadados: {METADATA_PATH}")


if __name__ == "__main__":
    main()