import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

BASE_URL = "https://www.gov.br/saude/pt-br/assuntos/pcdt"
DOWNLOAD_FOLDER = "data/raw/pdfs/PCDT"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Reutiliza a conexão HTTP
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

# Coleta as letras
print("Obtendo lista de letras...")

response = session.get(BASE_URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

letter_urls = []

for a in soup.select("a.govbr-card-content"):
    href = a.get("href")

    if href:
        letter_urls.append(urljoin(BASE_URL, href))

print(f"{len(letter_urls)} letras encontradas.\n")

# Coleta todas as doenças
diseases = []

for letter_url in tqdm(letter_urls, desc="Letras"):

    try:
        response = session.get(letter_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.select("a.summary.url"):

            diseases.append({
                "name": a.get_text(strip=True),
                "url": urljoin(letter_url, a["href"])
            })

    except Exception as e:
        print(f"Erro na letra {letter_url}")
        print(e)

print(f"\n{len(diseases)} protocolos encontrados.\n")

# Download dos PDFs
for disease in tqdm(diseases, desc="Baixando PDFs"):

    try:

        response = session.get(disease["url"], timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        pdf_url = None
        filename = None

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if "@@download/file" in href:

                pdf_url = urljoin(disease["url"], href)
                filename = a.get_text(strip=True)

                if not filename.lower().endswith(".pdf"):
                    filename += ".pdf"

                break

        if pdf_url is None:
            print(f"PDF não encontrado: {disease['name']}")
            continue

        file_path = os.path.join(DOWNLOAD_FOLDER, filename)

        # Não baixa novamente
        if os.path.exists(file_path):
            continue

        sucesso = False

        for tentativa in range(3):

            try:

                pdf = session.get(
                    pdf_url,
                    stream=True,
                    timeout=60
                )

                pdf.raise_for_status()

                with open(file_path, "wb") as f:

                    for chunk in pdf.iter_content(chunk_size=8192):

                        if chunk:
                            f.write(chunk)

                sucesso = True
                break

            except requests.RequestException:

                print(
                    f"Tentativa {tentativa+1}/3 falhou para {filename}"
                )

                time.sleep(2)

        if not sucesso:
            print(f"Não foi possível baixar {filename}")

        time.sleep(1)

    except Exception as e:

        print(f"Erro em {disease['name']}")
        print(e)

print("\nTodos os downloads foram processados.")