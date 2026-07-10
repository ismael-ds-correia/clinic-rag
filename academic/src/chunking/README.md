# Pipeline de Chunking de PCDTs

## Índice

- [1. Visão Geral](#1-visão-geral)
- [2. Arquitetura Geral](#2-arquitetura-geral)
- [3. Estratégia de Chunking](#3-estratégia-de-chunking)
- [4. Pipeline de Processamento](#4-pipeline-de-processamento)
- [5. Estrutura dos Chunks](#5-estrutura-dos-chunks)
- [6. Estratégias Implementadas](#6-estratégias-implementadas)
- [7. Organização do Código](#7-organização-do-código)
- [8. Fluxo dos Dados](#8-fluxo-dos-dados)
- [9. Decisões Arquiteturais](#9-decisões-arquiteturais)
- [10. Como Executar](#10-como-executar)

---

## 1. Visão Geral

Este módulo do projeto implementa um pipeline de chunking estrutural para Protocolos Clínicos e Diretrizes Terapêuticas (PCDTs). O objetivo é transformar documentos clínicos estruturados em chunks semânticos que preservem o contexto clínico e sejam adequados para sistemas de RAG.

**Problema resolvido:** Documentos clínicos longos e estruturados precisam ser divididos em unidades menores para indexação e recuperação eficiente, mas a divisão simples por tamanho de caracteres quebra o contexto clínico e a estrutura lógica do documento.

**Resultado produzido:** Arquivo JSONL contendo os chunks, cada um representando uma seção ou conjunto de seções do documento original, enriquecidos com metadados estruturais e entidades semânticas.

---

## 2. Arquitetura Geral

**Etapas do pipeline:**

1. **Leitura e agrupamento:** Lê arquivo JSONL contendo páginas de documentos e agrupa por fonte
2. **Reconstrução:** Reconstrói o texto completo do documento a partir das páginas ordenadas
3. **Detecção de seções:** Identifica seções baseadas em numeração hierárquica (1., 2.1, 3.4.2, etc.)
4. **Consolidação:** Realiza merge de seções pequenas para evitar chunks fragmentados
5. **Enriquecimento semântico:** Extrai entidades relevantes de cada seção usando técnicas de NLP
6. **Geração de chunks:** Converte seções enriquecidas em chunks finais com metadados

---

## 3. Estratégia de Chunking

### Chunking Estrutural

O pipeline utiliza chunking estrutural baseado na hierarquia de seções do documento. Cada chunk corresponde a uma seção detectada ou a um conjunto de seções mescladas.

**Padrão de detecção de seções:**
- Inicia com nova linha (`\n`)
- Seguido de enumeração numérica (ex: "1.", "2.1", "3.4.2.1")
- Seguido de espaço
- Seguido de título (iniciando com letra maiúscula)
- Seguido de nova linha

Exemplos válidos:
- `\n2. Diagnóstico\n`
- `\n2.1 Diagnóstico Clínico\n`
- `\n3.4.2 Tratamento Farmacológico\n`

### Validação Hierárquica

O detector implementa uma máquina de estados para validar transições hierárquicas entre seções, garantindo que apenas seções com numeração válida sejam aceitas. As regras de transição incluem:

- **Incremento do último componente:** `A.B.C → A.B.(C+1)`
- **Criação de subseção:** `A.B.C → A.B.C.1`
- **Subida para ancestral:** `A.B.C → A.(B+1)`
- **Primeiro subtítulo do próximo capítulo:** `A → (A+1).1`

### Preservação do Contexto Clínico

- Cada chunk preserva o título da seção e títulos de seções absorvidas
- Metadados incluem intervalo de páginas (start_page, end_page)
- Entidades semânticas são extraídas para representar conceitos-chave

### Regras de Merge

Seções com conteúdo menor que 750 caracteres são mescladas:

- **Backward merge:** Seção pequena é absorvida pela seção anterior (padrão)
- **Forward merge:** Se a primeira seção for pequena, absorve a próxima seção

Seções absorvidas têm suas numerações e títulos preservados nos metadados (`absorbed_sections`, `absorbed_section_titles`).

### Princípios Adotados

1. **Respeito à estrutura original:** Chunking segue a hierarquia natural do documento
2. **Evitar fragmentação:** Merge de seções pequenas previne chunks com contexto insuficiente
3. **Enriquecimento semântico:** Entidades extraídas melhoram a recuperação por conceito
4. **Rastreabilidade:** Metadados permitem rastrear a origem de cada chunk no documento original

---

## 4. Pipeline de Processamento

### 4.1 Leitura do JSONL

**Módulo:** `io/jsonl_reader.py`

**Função:** Lê arquivo JSONL contendo páginas de documentos e agrupa por fonte.

**Entrada:** Arquivo JSONL com linhas contendo:
- `text`: texto da página
- `source`: identificador do documento
- `page`: número da página
- `type`: tipo do documento

**Saída:** Dicionário mapeando `source` → lista de `DocumentPage` ordenadas por número de página.

**Parâmetro opcional:** `max_sources` limita o número de documentos processados.

### 4.2 Reconstrução do Documento

**Módulo:** `io/document_reconstructor.py`

**Função:** Reconstrói o texto completo concatenando páginas em ordem.

**Processo:**
1. Itera sobre páginas ordenadas
2. Concatena texto de cada página
3. Adiciona nova linha entre páginas
4. Constrói `page_offset_map` mapeando número da página → offset de caractere

**Saída:** Tupla `(full_text, page_offset_map)`

### 4.3 Detecção de Seções

**Módulo:** `sections/section_detector.py`

**Função:** Identifica seções usando regex e validação hierárquica.

**Processo:**
1. Encontra todos os candidatos usando regex `ENUMERATION_PATTERN`
2. Valida cada candidato usando máquina de estados
3. Para seções de referências, interrompe o processamento
4. Calcula nível hierárquico (profundidade da numeração)
5. Determina limites da seção (start_pos, end_pos)
6. Mapeia para intervalo de páginas usando `page_offset_map`

**Saída:** Lista de objetos `Section` com:
- `source`, `section_order`, `numbering`, `level`, `title`, `content`
- `start_page`, `end_page`

### 4.4 Construção da Estrutura

**Módulo:** `sections/section_structure.py`

**Função:** Organiza seções detectadas em estrutura `DocumentSections`.

**Processo:**
1. Cria objeto `DocumentSections` para o documento
2. Adiciona cada seção detectada
3. Executa merge de seções pequenas

### 4.5 Merge de Seções Pequenas

**Módulo:** `sections/section_structure.py` (método `merge_small_sections`)

**Função:** Mescla seções com conteúdo < 750 caracteres.

**Estratégias:**
- **Backward merge (padrão):** Seção pequena é absorvida pela anterior
- **Forward merge:** Primeira seção pequena absorve a próxima

**Metadados preservados:**
- `absorbed_sections`: lista de numerações absorvidas
- `absorbed_section_titles`: lista de títulos absorvidos
- `end_page`: atualizado para incluir páginas absorvidas

### 4.6 Enriquecimento Semântico

**Módulo:** `semantic/semantic_enricher.py`

**Função:** Extrai entidades semânticas representativas de cada seção.

**Processo em batch:**
1. **Extração de candidatos:** Sintagmas nominais (noun phrases) de 2-6 palavras
2. **Ranqueamento local:** TextRank calcula relevância dentro da seção
3. **Filtragem global:** IDF remove termos muito frequentes no corpus
4. **Seleção final:** Top N entidades por relevância

**Sobre IDF (Inverse Document Frequency):**

IDF é uma métrica estatística que avalia a importância de um termo em um corpus de documentos. O conceito é que termos que aparecem em muitos documentos são menos discriminativos do que termos que aparecem em poucos documentos.

A fórmula matemática do IDF é:

```
IDF(t) = log(N / df(t))
```

Onde:
- `N` = número total de documentos no corpus
- `df(t)` = número de documentos que contêm o termo `t`
- `log` = logaritmo natural

**Interpretação:**
- IDF alto → termo é raro no corpus (mais discriminativo)
- IDF baixo → termo é comum no corpus (menos discriminativo)
- Se um termo aparece em todos os documentos, IDF = log(1) = 0

No pipeline, IDF é calculado globalmente sobre todas as seções do batch e usado para filtrar candidatos com IDF < 1.5, removendo termos muito frequentes como "paciente" ou "tratamento" que não agregam discriminação semântica.

**Saída:** Lista de entidades semânticas por seção, adicionadas ao campo `semantic_entities`.

### 4.7 Geração dos Chunks

**Módulo:** `chunks/chunk_generator.py`

**Função:** Converte seções enriquecidas em chunks finais.

**Processo:**
1. Para cada seção em `DocumentSections`
2. Constrói `chunk_id`: `source__section_number`
3. Compila `section_titles`: título principal + títulos absorvidos
4. Limpa texto (remove bullets, underscores, aspas, pontos repetidos)
5. Constrói metadados (absorbed_sections, semantic_entities, document_type)
6. Serializa como JSON

**Saída:** Lista de dicionários JSON prontos para escrita em JSONL.

---

## 5. Estrutura dos Chunks

### Formato JSON

```json
{
  "chunk_id": "pcdt_diretriz_123__2.1",
  "source": "pcdt_diretriz_123",
  "section_number": "2.1",
  "level": 2,
  "section_titles": ["Diagnóstico Clínico", "Exames Complementares"],
  "text": "conteúdo limpo da seção...",
  "page_start": 5,
  "page_end": 7,
  "metadata": {
    "absorbed_sections": ["2.1.1"],
    "absorbed_section_titles": ["Exames Complementares"],
    "document_type": "PCDT",
    "semantic_entities": ["insuficiência cardíaca", "ecocardiograma", "troponina"]
  }
}
```

### Descrição dos Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `chunk_id` | string | Identificador único: `source__section_number` |
| `source` | string | Identificador do documento original |
| `section_number` | string | Numeração da seção principal (ex: "2.1") |
| `level` | int | Nível hierárquico da seção |
| `section_titles` | list[string] | Título principal + títulos de seções absorvidas |
| `text` | string | Conteúdo textual limpo da seção |
| `page_start` | int | Página inicial da seção |
| `page_end` | int | Página final da seção |
| `metadata` | object | Metadados adicionais |

### Metadados

| Campo | Descrição |
|-------|-----------|
| `absorbed_sections` | Lista de numerações de seções absorvidas |
| `absorbed_section_titles` | Lista de títulos de seções absorvidas |
| `document_type` | Tipo do documento (fixo: "PCDT") |
| `semantic_entities` | Lista de entidades semânticas extraídas |

---

## 6. Estratégias Implementadas

### 6.1 Chunking Estrutural

**Objetivo:** Preservar a estrutura lógica do documento.

**Funcionamento:**
- Detecta seções baseadas em numeração hierárquica
- Valida transições hierárquicas para evitar falsos positivos
- Cada chunk corresponde a uma seção ou conjunto de seções

**Benefício:** Mantém contexto clínico coeso e segue a organização original do PCDT.

### 6.2 Merge de Seções Pequenas

**Objetivo:** Evitar chunks com contexto insuficiente.

**Funcionamento:**
- Seções < 750 caracteres são mescladas
- Backward merge: absorve na seção anterior
- Forward merge: primeira seção pequena absorve a próxima
- Preserva numerações e títulos absorvidos nos metadados

**Benefício:** Reduz fragmentação e garante chunks com conteúdo significativo para recuperação.

### 6.3 Metadados Estruturais

**Objetivo:** Permitir rastreabilidade e contexto adicional.

**Funcionamento:**
- `chunk_id`: identificador único composto
- `section_number`: numeração da seção
- `level`: profundidade hierárquica
- `page_start`/`page_end`: intervalo de páginas
- `absorbed_sections`/`absorbed_section_titles`: histórico de merge

**Benefício:** Permite rastrear origem, navegar hierarquia e citar fontes.

### 6.4 Enriquecimento Semântico

**Objetivo:** Extrair conceitos-chave para melhorar recuperação por conceito.

**Funcionamento:**

**Pipeline de enriquecimento:**
1. **Extração de sintagmas nominais:** Regex captura sequências de 2-6 palavras em português
2. **Filtro de stopwords:** Remove frases compostas apenas de stopwords comuns
3. **Remoção de subconjuntos:** Prefere frases maiores que contêm subconjuntos
4. **TextRank local:** Algoritmo de ranqueamento baseado em co-ocorrência em janela deslizante
5. **IDF global:** Filtra termos muito frequentes no corpus (threshold: 1.5)
6. **Seleção final:** Top N entidades (padrão: 10)

**Benefício:** Permite recuperação semântica por conceitos clínicos, não apenas por palavras-chave literais.

---

## 7. Organização do Código

| Arquivo | Responsabilidade | Principais Classes/Funções | Relação |
|---------|------------------|---------------------------|---------|
| `main.py` | Orquestração do pipeline | `main()` | Coordena todos os módulos |
| `io/jsonl_reader.py` | Leitura de JSONL | `JSONLReader`, `DocumentPage` | Fornece páginas para reconstrutor |
| `io/document_reconstructor.py` | Reconstrução de documentos | `DocumentReconstructor.reconstruct()` | Recebe páginas, gera texto completo |
| `sections/section_detector.py` | Detecção de seções | `SectionDetector.detect_sections()` | Recebe texto, gera seções |
| `sections/section_structure.py` | Estruturas de dados | `Section`, `DocumentSections.merge_small_sections()` | Armazena e consolida seções |
| `chunks/chunk_generator.py` | Geração de chunks | `FinalChunkGenerator.document_sections_to_chunks()` | Converte seções em chunks |
| `semantic/__init__.py` | Exportações do módulo | Exporta classes e funções | Interface pública do módulo |
| `semantic/config.py` | Configuração | `SemanticEnricherConfig` | Parâmetros para enriquecimento |
| `semantic/enricher.py` | Orquestrador de enriquecimento | `SemanticEnricher.enrich_sections_batch()` | Coordena pipeline semântico |
| `semantic/extraction.py` | Extração de candidatos | `extract_noun_phrases()` | Extrai sintagmas nominais |
| `semantic/textrank.py` | Ranqueamento local | `calculate_textrank_scores()` | Calcula TextRank |
| `semantic/idf.py` | Filtragem global | `calculate_global_idf()`, `filter_by_idf()` | Calcula e aplica IDF |
| `semantic/selection.py` | Seleção final | `select_final_entities()` | Seleciona top N entidades |
| `semantic/semantic_enricher.py` | Implementação monolítica | Contém todas as funções acima | Versão alternativa com tudo em um arquivo |

---

## 8. Fluxo dos Dados

**Evolução dos dados:**

1. **JSONL (páginas):** Linhas com `text`, `source`, `page`, `type`
2. **DocumentPage:** Objetos dataclass representando cada página
3. **Documento reconstruído:** String `full_text` + mapa de offsets
4. **Seções:** Lista de objetos `Section` com numeração, título, conteúdo
5. **Seções consolidadas:** `DocumentSections` com merge aplicado
6. **Seções enriquecidas:** `DocumentSections` com `semantic_entities`
7. **Chunks:** Dicionários com todos os campos finais
8. **JSONL final:** Arquivo com uma linha por chunk

---

## 9. Decisões Arquiteturais

### 9.1 Chunking por Seções vs. Tamanho Fixo

**Decisão:** Chunking estrutural baseado em seções.

**Justificativa:**
- Documentos clínicos têm estrutura lógica bem-definida (diagnóstico, tratamento, etc.)
- Chunking por tamanho fixo quebraria conceitos clínicos entre chunks
- Seções naturais preservam contexto clínico coeso
- Permite navegação hierárquica nos resultados

### 9.2 Merge de Seções Pequenas

**Decisão:** Mesclar seções < 750 caracteres.

**Justificativa:**
- Seções muito pequenas têm contexto insuficiente para recuperação eficaz
- Evita fragmentação excessiva do documento
- Preserva informação através de metadados de seções absorvidas
- Threshold de 750 caracteres baseado em empírica para contexto clínico mínimo

### 9.3 Enriquecimento Semântico em Batch

**Decisão:** Calcular IDF global sobre todas as seções do batch.

**Justificativa:**
- IDF requer estatísticas do corpus completo
- Processamento em batch permite cálculo eficiente de IDF global
- Remove termos muito frequentes (ex: "paciente", "tratamento") que não discriminam
- Melhora qualidade das entidades selecionadas

### 9.4 TextRank para Ranqueamento Local

**Decisão:** Usar TextRank baseado em co-ocorrência em janela.

**Justificativa:**
- TextRank é eficiente e não requer treinamento
- Co-ocorrência em janela captura relações locais entre termos
- Algoritmo bem estabelecido para extração de palavras-chave
- Parâmetros configuráveis (janela, damping, iterações)

---

## 10. Como Executar

### Dependências

O projeto utiliza apenas bibliotecas Python padrão:
- `pathlib` - Manipulação de caminhos
- `json` - Serialização JSON
- `re` - Expressões regulares
- `math` - Cálculos matemáticos (IDF)
- `collections` - Estruturas de dados (Counter, defaultdict)
- `dataclasses` - Estruturas de dados
- `typing` - Anotações de tipo

Não há dependências externas (pip install não necessário).

### Arquivos de Entrada

**Arquivo JSONL de entrada:** `academic/data/processed/documents.jsonl`

Formato esperado por linha:
```json
{
  "text": "conteúdo da página",
  "source": "identificador_do_documento",
  "page": 1,
  "type": "tipo_do_documento"
}
```

### Arquivos Gerados

**Arquivo JSONL de saída:** `academic/data/chunks/chunks.jsonl`

Contém uma linha por chunk com o formato descrito na seção 5.

### Ponto de Entrada

**Script principal:** `academic/src/chunking/main.py`

Função de orquestração:
```python
main(
    jsonl_path: Union[str, Path],
    chunks_output_path: Union[str, Path],
    max_sources: Optional[int] = None
)
```

