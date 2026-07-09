"""Interface de linha de comando simples para o pipeline de RAG sobre PCDT.

Uso:
    cd academic/src
    python -m rag.cli
"""

from rag.pipeline import answer_question, build_pipeline

def _print_result(result: dict) -> None:
    print("\n" + "=" * 70)
    print("RESPOSTA:")
    print(result["answer"])

    if result["sources"]:
        print("\nFontes consultadas:")
        for src in result["sources"]:
            label = src["source"]
            if src["section"]:
                label += f" | Seção: {src['section']}"
            print(f"  - {label}")

    if result["low_confidence"]:
        print(
            "\n⚠️  Aviso: a auto-reflexão do sistema indicou baixa confiança "
            "nesta resposta (contexto possivelmente insuficiente)."
        )
    print("=" * 70 + "\n")


def main() -> None:
    print("Inicializando pipeline de RAG (base vetorial + LLM)...")
    components = build_pipeline()
    print("Pronto! Digite sua pergunta sobre os PCDT (ou 'sair' para encerrar).\n")

    while True:
        try:
            question = input("Pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not question:
            continue
        if question.lower() in {"sair", "exit", "quit"}:
            print("Encerrando.")
            break

        result = answer_question(question, components=components)
        _print_result(result)


if __name__ == "__main__":
    main()