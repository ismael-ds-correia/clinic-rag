| Integrante | Função |
|-----------|--------|
| [Ismael Diogenys](#ismael-diogenys--chunking-e-otimização-de-chunking) | Chunking e Otimização de chunking|
| [Brayan Vanz de Oliveira](#brayan-vanz-de-oliveira--) | |
| [Maria Camila](#maria-camila--) | |
| [Guilherme de Almeida Gama](#guilherme-de-almeida-gama--) | |
| [Carlos Alberto](#carlos-alberto--) | |
| [Thiago de Sousa Carvalho](#thiago-de-sousa-carvalho--) | |




# Ismael Diogenys — Chunking e otimização de chunking

Durante o projeto, fui responsável pelo projeto e implementação da estratégia de chunking utilizada para os Protocolos Clínicos e Diretrizes Terapêuticas (PCDTs), bem como pela avaliação e otimização contínua dessa estratégia. O objetivo principal foi construir chunks que preservassem a estrutura lógica dos documentos e maximizassem a qualidade da recuperação de informação em um sistema Retrieval-Augmented Generation (RAG).

A estratégia adotada foi baseada na estrutura hierárquica dos PCDTs, utilizando seções e subseções como unidades fundamentais de chunking. Para isso, desenvolvi um pipeline capaz de reconstruir os documentos a partir do JSONL, identificar automaticamente a hierarquia de seções por meio da numeração oficial dos documentos, consolidar essa estrutura e gerar chunks semanticamente coerentes. Além disso, implementei uma estratégia de merge para evitar chunks excessivamente pequenos, preservando o contexto clínico sem fragmentar informações relevantes.

Outra contribuição importante foi o desenvolvimento de uma etapa de enriquecimento semântico das seções antes da geração dos chunks finais. Nessa etapa, são extraídos automaticamente os principais conceitos presentes em cada seção por meio de técnicas de extração de candidatos, ranqueamento local e filtragem baseada em IDF calculado sobre todo o corpus. O resultado é um conjunto de entidades semânticas (`semantic_entities`) associado a cada chunk, permitindo enriquecer posteriormente a representação utilizada na recuperação de informação.

A avaliação ocorreu de forma iterativa durante todo o desenvolvimento. Diversos casos de erro foram identificados e corrigidos, principalmente relacionados à detecção incorreta de seções, ao tratamento de enumerações presentes no corpo do texto e à reconstrução dos limites das seções. Um dos problemas mais críticos encontrados foi a interrupção prematura do conteúdo da primeira seção de alguns documentos, ocasionando perda de contexto e geração de chunks inconsistentes. A investigação do pipeline permitiu localizar a origem do problema e corrigir a lógica responsável pela delimitação das seções antes da geração dos chunks.

Além da validação estrutural, também realizei avaliações qualitativas sobre o potencial de recuperação dos chunks produzidos. A principal preocupação foi garantir que cada chunk fosse suficientemente informativo para responder, de forma isolada, ao maior número possível de perguntas clínicas, mantendo ao mesmo tempo um tamanho adequado e uma forte coerência semântica.

Com mais tempo, eu expandiria a etapa de avaliação utilizando métricas quantitativas específicas para Retrieval-Augmented Generation, como Recall@k, MRR (Mean Reciprocal Rank) e nDCG, comparando diferentes estratégias de chunking sobre um conjunto padronizado de perguntas clínicas. Também investigaria estratégias híbridas de chunking, combinando a estrutura hierárquica dos documentos com informações semânticas extraídas automaticamente do texto. Em um contexto clínico, considero que uma RAG pode ser considerada "boa o suficiente" quando demonstra, de forma consistente, alta capacidade de recuperar os trechos corretos para diferentes tipos de consultas, preservando o contexto necessário para apoiar respostas confiáveis e reduzindo significativamente a ocorrência de omissões ou recuperações irrelevantes.

Para mais detalhes sobre minhas contribuições, acessar [README.md](academic/src/chunking/README.md).