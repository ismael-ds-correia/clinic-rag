# 🐳 Docker — ClinicRAG

Esta pasta contém toda a infraestrutura de containerização do projeto: o ambiente Python onde a aplicação roda, e o serviço Ollama que serve os modelos de LLM e embeddings localmente.

---

## 🗂️ Estrutura da pasta

```
docker/
├── scripts/
│   ├── entrypoint.sh              ⚙️ roda dentro do container quando ele inicia
│   └── setup.sh                   🚀 script único que sobe todo o ambiente
├── docker-compose.yml             🧩 definição dos serviços (ambient-llm + ollama)
├── docker-compose.override.yml    🔧 sobreposições de configuração (ambiente local)
├── Dockerfile                     🏗️ receita da imagem do container Python
├── .dockerignore                  🚫 arquivos ignorados na construção da imagem
└── README.md                      📘 este arquivo
```

## 🚀 Como subir o ambiente (único passo necessário)

Basta estar dentro da pasta `docker/scripts/` e rodar:

```bash
bash setup.sh
```

Esse único comando constrói as imagens, sobe os dois containers em segundo plano e já baixa o modelo de embeddings necessário no Ollama. Nenhum outro passo manual é necessário para preparar o ambiente.

## 🧩 Como os dois serviços funcionam juntos

O `docker-compose.yml` define dois containers, que rodam em paralelo e conseguem se comunicar entre si pela rede interna que o Docker Compose cria automaticamente:

- **`ambient-llm`** 🐍 — o container Python da aplicação (build feito a partir do `Dockerfile` desta pasta). É onde o Streamlit e o restante do pipeline do ClinicRAG rodam. Ele tem a pasta `academic/` inteira montada como volume (`../academic:/app/academic`), então qualquer alteração de código no seu computador aparece dentro do container imediatamente, sem precisar reconstruir a imagem.
- **`ollama`** 🧠 — a imagem oficial do Ollama, responsável por rodar os modelos de LLM e de embeddings localmente. Ele expõe a porta `11434`, e guarda os modelos baixados no volume nomeado `ollama_data`, para que eles não precisem ser baixados de novo toda vez que o container reiniciar.

De dentro do container `ambient-llm`, o Ollama é acessado pelo nome do serviço, não por `localhost` — ou seja, uma chamada HTTP para `http://ollama:11434` (e não `http://localhost:11434`). Isso funciona porque o Docker Compose cria automaticamente um DNS interno onde o nome de cada serviço vira um endereço válido para os outros containers da mesma rede.

## 🏗️ Dockerfile — o que cada bloco faz

```dockerfile
FROM python:3.10-slim
WORKDIR /app
```
Parte da imagem oficial e enxuta do Python 3.10, e define `/app` como diretório de trabalho dentro do container.

```dockerfile
COPY ./academic/requirements.txt /scripts/requirements.txt
RUN pip install --no-cache-dir -r /scripts/requirements.txt
```
Copia só o `requirements.txt` primeiro (antes do resto do código) e instala as dependências. Isso é proposital: o Docker guarda essa camada em cache, então se você só mudar código depois (sem mexer no `requirements.txt`), a reconstrução da imagem não precisa reinstalar tudo de novo.

```dockerfile
COPY ./docker/scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

EXPOSE 8501
ENTRYPOINT [ "sh", "/scripts/entrypoint.sh" ]
```
Copia o script de entrada, dá permissão de execução para ele, expõe a porta `8501` (a porta padrão do Streamlit) e define que, sempre que o container iniciar, ele vai rodar o `entrypoint.sh`.

## ⚙️ `entrypoint.sh` — o que roda quando o container liga

```bash
#!/bin/bash
set -e

echo "Initializing the entrypoint script..."

streamlit run academic/src/interface/app.py --server.port=8501 --server.address=0.0.0.0

echo "🚀 Setup successfully created!"
```

```bash
docker exec -it ambient-llm bash
streamlit run academic/src/interface/app.py --server.port=8501 --server.address=0.0.0.0
```

## 🚀 `setup.sh` — o que ele automatiza, passo a passo

```bash
#!/bin/bash
set -e

echo "⚙️ Starting the Setup..."

echo "🔓 Giving Permissions to entrypoint.sh & setup.sh.."
chmod +x ./entrypoint.sh

echo "⬆️ Upping the Docker Image..."
cd .. ; docker compose up --build -d

echo "⏳ Waiting for the Ollama container to be ready..."
sleep 5

echo "📥 Verifying and downloading the bge-m3 model (this may take time on the first run)..."
docker exec ollama ollama pull bge-m3

echo "✅ All done! Get fun."
```

1. **Dá permissão de execução** ao `entrypoint.sh` (necessário caso o arquivo tenha perdido a permissão, por exemplo depois de um `git clone`).
2. **Sobe os dois containers** (`ambient-llm` e `ollama`) em segundo plano (`-d`), reconstruindo a imagem se algo mudou (`--build`).
3. **Espera 5 segundos** para dar tempo do container do Ollama terminar de inicializar antes de mandar comandos para ele.
4. **Baixa o modelo `bge-m3`** dentro do container do Ollama, caso ele ainda não exista localmente — esse é o modelo de embeddings usado pelo ClinicRAG. Como o download fica salvo no volume `ollama_data`, isso só demora de verdade na primeira execução; nas próximas, o Ollama já reconhece que o modelo existe e pula o download.

## 🔎 Comandos úteis para o dia a dia

```bash
# ver os logs dos containers em tempo real
docker compose -f docker/docker-compose.yml logs -f

# entrar no container da aplicação
docker exec -it ambient-llm bash

# parar tudo
docker compose -f docker/docker-compose.yml down
```

---

✍️ Esta parte do projeto foi feita por **Carlos Alberto da Silva Neto (Líder da Sprint)**.

---

# 🐳 Docker — ClinicRAG

This folder contains all of the project's containerization infrastructure: the Python environment where the application runs, and the Ollama service that serves LLM and embedding models locally.

---

## 🗂️ Folder structure

```
docker/
├── scripts/
│   ├── entrypoint.sh              ⚙️ runs inside the container when it starts
│   └── setup.sh                   🚀 single script that brings up the whole environment
├── docker-compose.yml             🧩 service definitions (ambient-llm + ollama)
├── docker-compose.override.yml    🔧 configuration overrides (local environment)
├── Dockerfile                     🏗️ recipe for the Python container image
├── .dockerignore                  🚫 files ignored when building the image
└── README.md                      📘 this file
```

## 🚀 How to bring up the environment (only step needed)

Just be inside the `docker/scripts/` folder and run:

```bash
bash setup.sh
```

This single command builds the images, brings up both containers in the background, and already downloads the required embedding model into Ollama. No other manual step is needed to prepare the environment.

## 🧩 How the two services work together

`docker-compose.yml` defines two containers, which run in parallel and can talk to each other over the internal network that Docker Compose creates automatically:

- **`ambient-llm`** 🐍 — the application's Python container (built from the `Dockerfile` in this folder). This is where Streamlit and the rest of the ClinicRAG pipeline run. It has the entire `academic/` folder mounted as a volume (`../academic:/app/academic`), so any code change on your machine shows up inside the container immediately, with no need to rebuild the image.
- **`ollama`** 🧠 — the official Ollama image, responsible for running LLM and embedding models locally. It exposes port `11434`, and stores downloaded models in the named volume `ollama_data`, so they don't need to be downloaded again every time the container restarts.

From inside the `ambient-llm` container, Ollama is reached by the service name, not by `localhost` — that is, an HTTP call to `http://ollama:11434` (not `http://localhost:11434`). This works because Docker Compose automatically creates an internal DNS where each service's name becomes a valid address for the other containers on the same network.

## 🏗️ Dockerfile — what each block does

```dockerfile
FROM python:3.10-slim
WORKDIR /app
```
Starts from the official, lightweight Python 3.10 image, and sets `/app` as the working directory inside the container.

```dockerfile
COPY ./academic/requirements.txt /scripts/requirements.txt
RUN pip install --no-cache-dir -r /scripts/requirements.txt
```
Copies only `requirements.txt` first (before the rest of the code) and installs the dependencies. This is intentional: Docker caches this layer, so if you only change code afterward (without touching `requirements.txt`), rebuilding the image doesn't need to reinstall everything again.

```dockerfile
COPY ./docker/scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

EXPOSE 8501
ENTRYPOINT [ "sh", "/scripts/entrypoint.sh" ]
```
Copies the entrypoint script, gives it execute permission, exposes port `8501` (Streamlit's default port), and sets it so that whenever the container starts, it runs `entrypoint.sh`.

## ⚙️ `entrypoint.sh` — what runs when the container starts

```bash
#!/bin/bash
set -e

echo "Initializing the entrypoint script..."

streamlit run academic/src/interface/app.py --server.port=8501 --server.address=0.0.0.0

echo "🚀 Setup successfully created!"
```

```bash
docker exec -it ambient-llm bash
streamlit run academic/src/interface/app.py --server.port=8501 --server.address=0.0.0.0
```

## 🚀 `setup.sh` — what it automates, step by step

```bash
#!/bin/bash
set -e

echo "⚙️ Starting the Setup..."

echo "🔓 Giving Permissions to entrypoint.sh & setup.sh.."
chmod +x ./entrypoint.sh

echo "⬆️ Upping the Docker Image..."
cd .. ; docker compose up --build -d

echo "⏳ Waiting for the Ollama container to be ready..."
sleep 5

echo "📥 Verifying and downloading the bge-m3 model (this may take time on the first run)..."
docker exec ollama ollama pull bge-m3

echo "✅ All done! Get fun."
```

1. **Grants execute permission** to `entrypoint.sh` (needed in case the file lost that permission, for example after a `git clone`).
2. **Brings up both containers** (`ambient-llm` and `ollama`) in the background (`-d`), rebuilding the image if anything changed (`--build`).
3. **Waits 5 seconds** to give the Ollama container time to finish initializing before sending commands to it.
4. **Downloads the `bge-m3` model** inside the Ollama container, if it doesn't already exist locally — this is the embedding model used by ClinicRAG. Since the download is saved in the `ollama_data` volume, this only takes real time on the first run; on later runs, Ollama already recognizes the model exists and skips the download.

## 🔎 Handy day-to-day commands

```bash
# watch container logs in real time
docker compose -f docker/docker-compose.yml logs -f

# enter the application container
docker exec -it ambient-llm bash

# stop everything
docker compose -f docker/docker-compose.yml down
```

---

✍️ This part of the project was built by **Carlos Alberto da Silva Neto (Sprint Leader)**.