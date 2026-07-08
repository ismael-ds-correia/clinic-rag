import json
from pathlib import Path
import re
import unicodedata

from langchain_community.document_loaders import PyPDFLoader


RAW_FOLDER = Path(__file__).resolve().parents[2] / "data" / "raw" / "pdfs" / "PCDT"
OUTPUT_FILE = Path(__file__).resolve().parents[2] / "data" / "processed" / "documents.jsonl"


SECTION_HEADERS = [
    "ANEXO",
    "ANEXOS",
    "APENDICE",
    "APENDICES",
    "FLUXOGRAMA",
    "FLUXOGRAMAS",
    "COLABORADORES",
    "AGRADECIMENTOS"
]

REFERENCE_HEADERS = [
    "REFERENCIAS",
    "REFERÊNCIAS",
    "REFERENCIAS BIBLIOGRAFICAS",
    "REFERÊNCIAS BIBLIOGRÁFICAS",
    "BIBLIOGRAFIA"
]


def normalize_text(text: str) -> str:
    """Remove excesso de espaços, acentos e cedilha."""

    text = text.replace("\x00", " ")

    # Remove acentos e cedilha
    #text = unicodedata.normalize("NFD", text)
    #text = "".join(
    #    c for c in text
    #    if unicodedata.category(c) != "Mn"
    #)

    # Remove excesso de espaços
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def infer_document_type(pages) -> str:
    """Infere o tipo do documento."""

    for page in pages:
        if "protocolo clínico e diretrizes terapêuticas" in page.page_content.lower():
            return "PCDT"

    return "OUTRO"


def is_reference_header(line: str) -> bool:
    return re.fullmatch(
        r"\s*(\d+\s*\.?)?\s*(REFERENCIAS|REFERÊNCIAS)(\s+BIBLIOGRAFICAS)?\s*",
        line,
        flags=re.IGNORECASE
    ) is not None


def is_section_header(line: str) -> bool:
    """Detecta cabeçalhos que encerram a seção de referências."""
    line = line.strip().upper()

    return any(
        line.startswith(header)
        for header in SECTION_HEADERS
    )


def remove_references(document):
    """Remove apenas a seção REFERÊNCIAS, preservando anexos, apêndices e demais seções posteriores."""

    inside_references = False

    for page in document:

        cleaned_lines = []

        for line in page["text"].splitlines():

            # Encontrou o início da seção REFERÊNCIAS
            if not inside_references and is_reference_header(line):
                inside_references = True
                continue

            # Encontrou uma nova seção
            if inside_references and is_section_header(line):
                inside_references = False

            if not inside_references:
                cleaned_lines.append(line)

        page["text"] = "\n".join(cleaned_lines).strip()

    return document


# main

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("", encoding="utf-8")

pdfs = list(RAW_FOLDER.glob("*.pdf"))

print(f"Encontrados {len(pdfs)} PDFs.\n")

with OUTPUT_FILE.open("a", encoding="utf-8") as f:

    for pdf in pdfs:

        print(f"Lendo {pdf.name}")

        try:
            loader = PyPDFLoader(str(pdf))
            pages = loader.load()

        except Exception as e:
            print(f"Erro em {pdf.name}")
            print(e)
            continue

        document_type = infer_document_type(pages)

        # Cria uma representação do PDF

        document = []

        for page in pages:

            document.append({
                "page": page.metadata["page"] + 1,
                "text": normalize_text(page.page_content)
            })

        # Limpeza

        document = remove_references(document)

        # Exportação

        for page in document:

            if not page["text"]:
                continue

            record = {
                "text": page["text"],
                "source": pdf.name,
                "page": page["page"],
                "type": document_type
            }

            f.write(json.dumps(record, ensure_ascii=False))
            f.write("\n")

print("\nIngestão concluída!")
