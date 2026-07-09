""" 
Camada de integração entre a interface Streamlit (app.py) e o pacote
`rag` (decomposição de pergunta + retrieval + geração + self-reflection),
implementado em academic/src/rag/.
 
A interface só chama `get_answer`. Ela devolve o mesmo formato produzido
por `rag.answer_question`, por exemplo:
 
    {
        "answer": str,
        "sources": [
            {"source": str, "section": str},
            ...
        ],
        "sub_questions": list[str],
        "low_confidence": bool,
        ...
    }
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

_components = None


def _get_components():
    """Constrói (ou retorna do cache) os componentes do pipeline: o
    retriever da base vetorial e o LLM. Evita recarregar tudo a cada
    pergunta."""
    global _components
    if _components is None:
        from rag import build_pipeline

        _components = build_pipeline()
    return _components


def get_answer(question: str) -> dict:
    """Ponto de entrada usado pela interface Streamlit (app.py)."""
    from rag import answer_question

    components = _get_components()
    return answer_question(question, components=components)