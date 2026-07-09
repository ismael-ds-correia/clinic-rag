# 🔢 Embeddings — ClinicRAG

Esta pasta contém a etapa do pipeline responsável por transformar os pedaços de texto (chunks) já processados em vetores numéricos (embeddings), prontos para serem armazenados na base vetorial e usados na busca por similaridade.

---

## 🗂️ Estrutura da pasta

```
src/embedding/
└── processing_embeddings/
    └── embedding.py      🔢 classe DataEmbedding, gera os vetores a partir dos chunks
```

## 🧠 Como funciona, do começo ao fim

1. **Lê os chunks** já gerados na etapa anterior do pipeline, de um arquivo JSONL (`data/chunks/chunks.jsonl`).
2. **Inicializa o modelo de embeddings** `bge-m3`, rodando localmente via Ollama.
3. **Enriquece o texto de cada chunk** antes de gerar o vetor, juntando o nome do documento de origem, os títulos de seção e as entidades semânticas identificadas — isso dá mais contexto ao modelo na hora de gerar o embedding, além do texto puro.
4. **Gera os vetores em lotes** (batches de 2048 chunks por vez), para não sobrecarregar o Ollama com uma chamada só gigante.
5. **Salva o resultado** em um novo JSONL (`data/embeddings/embeddings.jsonl`), com cada chunk original acompanhado do seu vetor de embedding.

## 🏗️ A classe `DataEmbedding`, método por método

### `__init__`
Recebe o caminho do arquivo de chunks de entrada e o caminho de saída dos embeddings. Valida que ambos são `str` ou `Path`, e guarda o modelo de embeddings como `None` até ele ser realmente necessário (só é inicializado quando o pipeline roda de verdade, evitando conectar no Ollama sem necessidade).

### `_initialize_embedding_model`
Cria a conexão com o modelo `bge-m3` via `OllamaEmbeddings`, usando `base_url="http://ollama:11434"`. Esse endereço não é `localhost` de propósito: dentro do ambiente Docker, o serviço do Ollama é acessado pelo nome do container (`ollama`), já que os dois containers (`ambient-llm` e `ollama`) conversam entre si pela rede interna do Docker Compose.

### `_read_chunks`
Lê o arquivo JSONL linha por linha, convertendo cada linha em um dicionário Python. Se o arquivo não existir, registra um erro no log e retorna uma lista vazia, em vez de quebrar o programa.

### `execute_pipeline`
O método principal, que orquestra tudo:
- Lê os chunks.
- Inicializa o modelo (só agora, de fato).
- Processa em lotes de 2048.
- Para cada chunk, monta um texto enriquecido (documento + seções + entidades + conteúdo) e gera o embedding desse texto combinado, não só do conteúdo puro.
- Escreve cada chunk, já com seu campo `"embedding"` preenchido, no arquivo de saída.

## 🚀 Como executar

Esse script precisa rodar de dentro do container `ambient-llm`, já que é lá que o Python, as dependências e a rede com o `ollama` estão configurados. Primeiro entre no container:

```bash
docker exec -it ambient-llm bash
```

Depois, já dentro do container, vá até a pasta `src` e rode o módulo com `-m`, usando o caminho completo até o arquivo (incluindo a subpasta `processing_embeddings`):

```bash
cd academic/src
python -m embedding.processing_embeddings.embedding
```

Isso vai ler `../data/chunks/chunks.jsonl` e gerar `../data/embeddings/embeddings.jsonl`, mostrando uma barra de progresso (`tqdm`) por lote processado.

📌 **Por que `-m` e não rodar o arquivo direto:** rodar como módulo (`-m`), a partir da pasta `src`, faz o Python reconhecer `embedding` e `processing_embeddings` como pacotes — isso é necessário para que os imports internos do projeto (como `from util.logger import setup_logger`) funcionem, já que eles são resolvidos a partir da raiz de `src`, não da pasta onde o arquivo está fisicamente.

## 📌 Por que enriquecer o texto antes de gerar o embedding

Gerar o vetor só a partir do conteúdo puro do chunk perde contexto valioso — por exemplo, dois chunks parecidos de documentos diferentes podem ficar quase indistinguíveis no espaço vetorial. Ao incluir o nome do documento, as seções e as entidades semânticas no texto que é de fato embedado, o vetor final carrega mais sinal sobre *de onde* aquele trecho veio, o que ajuda a busca por similaridade a recuperar os chunks certos com mais precisão.

## ⚠️ Atenção: consumo de recursos

O `bge-m3` é um modelo de embeddings relativamente pesado, e o `batch_size` usado no pipeline (2048 chunks por lote) é alto — dependendo da quantidade de RAM/VRAM disponível na sua máquina, isso pode deixar o processamento lento ou até travar o container do Ollama em máquinas com menos recursos.

Se isso acontecer, basta ajustar o parâmetro. Dentro de `execute_pipeline`, no arquivo `embedding.py`:

```python
batch_size = 2048
```

Reduza esse valor (por exemplo, para `256` ou `512`) para processar menos chunks por vez — isso deixa cada lote mais leve, ao custo de rodar mais lotes no total. Não é preciso mudar mais nada no resto do código para isso funcionar.

---

✍️ Esta parte do projeto foi feita por **Carlos Alberto da Silva Neto (Líder da Sprint)**.

---

# 🔢 Embeddings — ClinicRAG

This folder contains the pipeline stage responsible for turning the already-processed text chunks into numerical vectors (embeddings), ready to be stored in the vector database and used for similarity search.

---

## 🗂️ Folder structure

```
src/embedding/
└── processing_embeddings/
    └── embedding.py      🔢 DataEmbedding class, generates vectors from the chunks
```

## 🧠 How it works, from start to finish

1. **Reads the chunks** already produced by the previous pipeline stage, from a JSONL file (`data/chunks/chunks.jsonl`).
2. **Initializes the embedding model** `bge-m3`, running locally via Ollama.
3. **Enriches each chunk's text** before generating the vector, joining the source document name, section titles, and identified semantic entities — this gives the model more context when generating the embedding, beyond the raw text alone.
4. **Generates the vectors in batches** (2048 chunks per batch), to avoid overloading Ollama with one giant call.
5. **Saves the result** to a new JSONL file (`data/embeddings/embeddings.jsonl`), with each original chunk accompanied by its embedding vector.

## 🏗️ The `DataEmbedding` class, method by method

### `__init__`
Takes the path to the input chunks file and the output embeddings path. Validates that both are `str` or `Path`, and keeps the embedding model as `None` until it's actually needed (it's only initialized when the pipeline really runs, avoiding an unnecessary connection to Ollama).

### `_initialize_embedding_model`
Creates the connection to the `bge-m3` model via `OllamaEmbeddings`, using `base_url="http://ollama:11434"`. That address is intentionally not `localhost`: inside the Docker environment, the Ollama service is reached by the container's name (`ollama`), since the two containers (`ambient-llm` and `ollama`) talk to each other over Docker Compose's internal network.

### `_read_chunks`
Reads the JSONL file line by line, converting each line into a Python dictionary. If the file doesn't exist, it logs an error and returns an empty list instead of crashing the program.

### `execute_pipeline`
The main method, orchestrating everything:
- Reads the chunks.
- Initializes the model (only now, lazily).
- Processes in batches of 2048.
- For each chunk, builds an enriched text (document + sections + entities + content) and generates the embedding for that combined text, not just the raw content.
- Writes each chunk, now with its `"embedding"` field filled in, to the output file.

## 🚀 How to run

This script needs to run from inside the `ambient-llm` container, since that's where Python, the dependencies, and the network connection to `ollama` are all set up. First, enter the container:

```bash
docker exec -it ambient-llm bash
```

Then, inside the container, go to the `src` folder and run the module with `-m`, using the full path down to the file (including the `processing_embeddings` subfolder):

```bash
cd academic/src
python -m embedding.processing_embeddings.embedding
```

This reads `../data/chunks/chunks.jsonl` and produces `../data/embeddings/embeddings.jsonl`, showing a progress bar (`tqdm`) per processed batch.

📌 **Why `-m` instead of running the file directly:** running it as a module (`-m`), from the `src` folder, makes Python recognize both `embedding` and `processing_embeddings` as packages — this is required for the project's internal imports (like `from util.logger import setup_logger`) to work, since they're resolved from the root of `src`, not from the folder where the file physically lives.

## 📌 Why enrich the text before generating the embedding

Generating the vector from the raw chunk content alone loses valuable context — for example, two similar chunks from different documents could end up nearly indistinguishable in the vector space. By including the document name, sections, and semantic entities in the text that actually gets embedded, the final vector carries more signal about *where* that piece of text came from, which helps similarity search retrieve the right chunks more precisely.

## ⚠️ Warning: resource usage

`bge-m3` is a relatively heavy embedding model, and the `batch_size` used in the pipeline (2048 chunks per batch) is high — depending on how much RAM/VRAM is available on your machine, this can make processing slow or even cause the Ollama container to struggle on machines with fewer resources.

If that happens, just adjust the parameter. Inside `execute_pipeline`, in `embedding.py`:

```python
batch_size = 2048
```

Lower this value (for example, to `256` or `512`) to process fewer chunks at a time — this makes each batch lighter, at the cost of running more batches overall. Nothing else in the code needs to change for this to work.

---

✍️ This part of the project was built by **Carlos Alberto da Silva Neto (Sprint Leader)**.