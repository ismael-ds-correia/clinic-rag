"""Pacote de resposta a perguntas (RAG) sobre os Protocolos Clínicos e Diretrizes
Terapêuticas (PCDT) do Ministério da Saúde.

Este pacote é construído em cima dos artefatos já gerados pelos módulos
``ingestion``, ``chunking`` e ``embedding`` do projeto. Em particular, a
base vetorial FAISS é construída por ``embedding/create_vector_db.py``
(chunks de PCDT + embeddings bge-m3 via Ollama), e apenas carregada aqui —
o pacote ``rag`` não constrói sua própria base vetorial. Ele implementa, de
forma modular:

- carregamento da base vetorial FAISS já construída (``vector_store.py``);
- decomposição da pergunta do usuário em sub-perguntas (``decomposition.py``);
- recuperação de documentos relevantes (``retrieval.py``);
- geração de respostas fiéis aos documentos (``generation.py``);
- auto-reflexão sobre a qualidade da resposta/recuperação (``reflection.py``);
- orquestração de tudo isso em um pipeline único (``pipeline.py``).

Uso típico:

    from rag import answer_question

    resultado = answer_question("Qual o tratamento de primeira linha para X?")
    print(resultado["answer"])
"""

from .pipeline import answer_question, build_pipeline

__all__ = ["answer_question", "build_pipeline"]