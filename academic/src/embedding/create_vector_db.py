import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]

CHUNKS_PATH = BASE_DIR / "data" / "chunks" / "chunks.jsonl"
OUTPUT_DIR = BASE_DIR / "data" / "embeddings"

INDEX_PATH = OUTPUT_DIR / "index.faiss"
METADATA_PATH = OUTPUT_DIR / "metadata.json"


def load_chunks():
    chunks = []

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            chunks.append(item)

    return chunks


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chunks = load_chunks()

    texts = [chunk["text"] for chunk in chunks]

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    print("Base vetorial criada com sucesso!")
    print(f"Índice FAISS: {INDEX_PATH}")
    print(f"Metadados: {METADATA_PATH}")


if __name__ == "__main__":
    main()