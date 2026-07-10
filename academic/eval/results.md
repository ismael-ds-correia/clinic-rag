# Avaliação do Sistema RAG — PCDT (Protocolos Clínicos e Diretrizes Terapêuticas)

Este documento consolida os itens 8, 9 e 10 dos requisitos do projeto: o
conjunto de teste (gabarito), a avaliação de fidelidade/relevância e o
levantamento de respostas insatisfatórias do pipeline de RAG.

---

## 8. Conjunto de Teste (Gabarito)

12 perguntas clínicas sobre o acervo de PCDT, cada uma com resposta
esperada e trecho-fonte (documento + página, conforme
`academic/data/processed/pcdt.jsonl`). Este é o gabarito contra o qual as
respostas do sistema serão comparadas na Seção 9.

---

### Pergunta 1

**Pergunta:** Sendo a deficiência de biotinidase (DB) um erro inato do
metabolismo de herança autossômica recessiva, qual é o mecanismo
patológico que impede o organismo de reciclar a biotina endógena ou usar
a biotina ligada às proteínas da dieta?

**Resposta esperada:** Na DB, a enzima biotinidase — responsável por
liberar a biotina a partir de pequenos biotinilpeptídios e da biocitina
presentes nos alimentos, e por reciclar a biotina ligada a carboxilases
endógenas — tem sua atividade catalítica diminuída ou ausente. Sem essa
enzima funcional, a biotina não pode ser liberada da dieta nem reciclada
a partir do turnover de suas próprias carboxilases, sendo progressivamente
perdida na urina (principalmente como biocitina), levando ao esgotamento
gradual da vitamina no organismo.

**Resposta Gerada:** [Resposta 1](answers.md#resposta-1)

**Resposta Gerada (otimizada):** [Resposta 1 (Optimized Chunking)](answers_optimized_chunking.md#resposta-1)

**Trecho-fonte:** *Deficiência de Biotinidase (PCDT).pdf*, página 3.

> "A deficiência de biotinidase (DB) é um erro inato do metabolismo, de
> herança autossômica recessiva, no qual a biotinidase, enzima
> responsável pela capacidade de obtenção da vitamina biotina a partir
> dos alimentos, tem sua atividade catalítica diminuída ou ausente. [...]
> Assim, pacientes com DB são incapazes de reciclar a biotina endógena ou
> usar a biotina ligada às proteínas da dieta. Consequentemente, a
> biotina é perdida na urina, principalmente sob a forma de biocitina,
> ocorrendo o esgotamento progressivo."

---

### Pergunta 2

**Pergunta:** Quais são os sinais e sintomas clássicos de DGH/hipopituitarismo
que devem ser ativamente investigados no período neonatal ou em lactentes?

**Resposta esperada:** No período neonatal, os sinais e sintomas clássicos
de deficiência de GH (DGH)/hipopituitarismo que devem ser ativamente
investigados são: hipoglicemia, icterícia prolongada, micropênis e
defeitos de linha média.

**Resposta Gerada:** [Resposta 2](answers.md#resposta-2)

**Resposta Gerada (otimizada):** [Resposta 2 (Optimized Chunking)](answers_optimized_chunking.md#resposta-2)

**Trecho-fonte:** *Deficiência do Hormônio de Crescimento - HipopituitarismO.pdf*, página 5.

> "sinais e sintomas de DGH/hipopituitarismo no período neonatal
> (hipoglicemia, icterícia prolongada, micropênis, defeitos de linha
> média)."

---

### Pergunta 3

**Pergunta:** Frente à suspeita clínica, quais são os dois exames
solicitados para identificar arritmias cardíacas e afastar situações que
mimetizam o AVC (como a hipoglicemia)?

**Resposta esperada:** São solicitados a eletrocardiografia de repouso
(para identificar arritmias que aumentem o risco de AVC, sinais de
infarto do miocárdio ou dissecção de aorta) e a glicemia capilar (exame
laboratorial que avalia, entre outras coisas, se o quadro pode ser
explicado por hipoglicemia, uma das condições que mimetizam o AVC).

**Resposta Gerada:** [Resposta 3](answers.md#resposta-3)

**Resposta Gerada (otimizada):** [Resposta 3 (Optimized Chunking)](answers_optimized_chunking.md#resposta-3)

**Trecho-fonte:** *Acidente Vascular Cerebral Isquêmico Agudo - Portaria Conjunta SAES-SECTICS n 29.pdf*, página 4.

> "3.3. Outros exames complementares. Frente à suspeita clínica de AVC,
> os seguintes exames devem ser solicitados: eletrocardiografia de
> repouso; glicemia capilar; hemograma completo [...]. A
> eletrocardiografia visa a identificar arritmias que aumentem o risco de
> AVC, sinais de infarto do miocárdio ou dissecção de aorta associada,
> enquanto os exames laboratoriais avaliam o grau de coagulabilidade e
> situações que possam mimetizar ou agravar um AVC em curso (como, por
> exemplo, hipoglicemia, infecção ou distúrbios hidroeletrolíticos)."

---

### Pergunta 4

**Pergunta:** Como deve ser feita a monitorização da glicemia e da
temperatura nas primeiras 24 horas pós-trombólise?

**Resposta esperada:** Nas primeiras 24 horas pós-trombólise, a glicemia
deve ser monitorizada continuamente e mantida em níveis inferiores a 200
mg/dL. A temperatura axilar também deve ser monitorizada continuamente e
tratada caso seja maior ou igual a 37,5°C.

**Resposta Gerada:** [Resposta 4](answers.md#resposta-4)

**Resposta Gerada (otimizada):** [Resposta 4 (Optimized Chunking)](answers_optimized_chunking.md#resposta-4)

**Trecho-fonte:** *Acidente Vascular Cerebral Isquêmico Agudo - Portaria Conjunta SAES-SECTICS n 29.pdf*, página 10.

> "8.1. Monitorização pós trombólise. Deve-se monitorar continuamente,
> por pelo menos 24 horas, a pressão arterial, oximetria de pulso e
> eletrocardiografia. A glicemia também deve ser monitorizada e mantida
> em níveis inferiores a 200 mg/dL. A temperatura axilar também deve ser
> foco de monitorização, devendo ser tratada se maior ou igual a 37,5°C."

---

### Pergunta 5

**Pergunta:** No protocolo de "Acidente Vascular Cerebral Isquêmico Agudo", na seção de uso de anticoagulantes, qual é a regra específica
para pacientes que usaram dabigatrana nas últimas 48 horas? Existe
alguma condição ou medicamento reversor (antídoto) obrigatório
mencionado para autorizar a trombólise?

**Resposta esperada:** O uso de anticoagulantes orais diretos (incluindo
a dabigatrana) nas últimas 48 horas é, em regra, uma contraindicação à
trombólise — a menos que a função renal esteja normal e os testes de
coagulação (TTPA, RNI, contagem de plaquetas, tempo de trombina, tempo
de ecarina, atividade de Xa) estejam normais, sem outras
contraindicações. Especificamente para a dabigatrana, existe um
medicamento reversor (antídoto): se o agente reversor idarucizumabe
estiver disponível, ele pode ser utilizado e a trombólise realizada logo
em seguida.

**Resposta Gerada:** [Resposta 5](answers.md#resposta-5)

**Resposta Gerada (otimizada):** [Resposta 5 (Optimized Chunking)](answers_optimized_chunking.md#resposta-5)

**Trecho-fonte:** *Acidente Vascular Cerebral Isquêmico Agudo - Portaria Conjunta SAES-SECTICS n 29.pdf*, página 6.

> "Uso de anticoagulantes orais diretos (ACOD - inibidores diretos de
> trombina ou de fator Xa) nas últimas 48 horas, se a função renal
> estiver normal. Caso o paciente apresente testes de coagulação (TTPA,
> RNI, contagem de plaquetas, tempo de trombina, tempo de ecarina,
> atividade de Xa) normais, a trombólise pode ser realizada, se não
> apresentar outras contraindicações. Em pacientes em uso de
> dabigatrana, se houver o agente reversor disponível (idarucizumabe),
> ele pode ser utilizado e a trombólise realizada logo após."

---

### Pergunta 6

**Pergunta:** Como a Insuficiência Adrenal (IA) é dividida de acordo com
a localização do defeito da produção e em qual delas haverá deficiência
de mineralocorticoide?

**Resposta esperada:** A IA é dividida em primária (doença de Addison,
quando o defeito está localizado na própria glândula adrenal),
secundária (defeito na hipófise) e terciária (defeito no hipotálamo) —
sendo que as duas últimas podem ser agrupadas como Insuficiência Adrenal
Central (IAC). Apenas na IA primária haverá deficiência de
mineralocorticoide (aldosterona), já que esse hormônio é produzido pela
própria adrenal.

**Resposta Gerada:** [Resposta 6](answers.md#resposta-6)

**Resposta Gerada (otimizada):** [Resposta 6 (Optimized Chunking)](answers_optimized_chunking.md#resposta-6)

**Trecho-fonte:** *Insuficiência Adrenal.pdf*, página 2.

> "A IA pode ser dividida em primária (também chamada de doença de
> Addison, quando o defeito da produção está localizado na própria
> glândula adrenal), secundária (quando o defeito está localizado na
> hipófise) ou terciária (quando o defeito está localizado no
> hipotálamo). Essas duas últimas também podem ser agrupadas e chamadas
> de Insuficiência Adrenal Central (IAC). Cabe ressaltar que somente na
> IA primária haverá deficiência de mineralocorticoide, hormônio
> essencial para o equilíbrio hidroeletrolítico."

---

### Pergunta 7

**Pergunta:** Em até quanto tempo a administração do alteplase deve
ocorrer após o início dos sintomas de AVCi?

**Resposta esperada:** A administração de alteplase deve ocorrer em até
4 horas e 30 minutos (4,5 horas) do início dos sintomas de AVC isquêmico
agudo.

**Resposta Gerada:** [Resposta 7](answers.md#resposta-7)

**Resposta Gerada (otimizada):** [Resposta 7 (Optimized Chunking)](answers_optimized_chunking.md#resposta-7)

**Trecho-fonte:** *Acidente Vascular Cerebral Isquêmico Agudo - Portaria Conjunta SAES-SECTICS n 29.pdf*, página 10.

> "Alteplase: 0,9 mg/kg (máximo de 90 mg), por via intravenosa, com 10%
> da dose aplicada em bolus e o restante, continuamente, ao longo de 60
> minutos. A administração da alteplase deve ocorrer em até 4 horas e 30
> minutos do início dos sintomas de AVCi."

---

### Pergunta 8

**Pergunta:** Paciente com adenocarcinoma de cólon vai para cirurgia
curativa. Qual é a amostragem linfonodal mínima que o patologista precisa
encontrar na peça?

**Resposta esperada:** É essencial uma amostragem linfonodal mínima de
12 linfonodos na peça de ressecção colônica.

**Resposta Gerada:** [Resposta 8](answers.md#resposta-8)

**Resposta Gerada (otimizada):** [Resposta 8 (Optimized Chunking)](answers_optimized_chunking.md#resposta-8)

**Trecho-fonte:** *Adenocarcinoma de Cólon e de Reto - PCDT.pdf*, página 7.

> "Na cirurgia do adenocarcinoma de cólon é fundamental garantir margens
> satisfatórias (aproximadamente 5 cm) na ressecção colônica, juntamente
> com uma linfadenectomia adequada. Esta última envolve a ligadura dos
> vasos nutridores em suas origens do segmento colônico correspondente,
> sendo essencial uma amostragem linfonodal mínima de 12 linfonodos."

---

### Pergunta 9

**Pergunta:** Por qual motivo o uso de benzodiazepínicos, como o
diazepam, é especificamente sugerido no manejo clínico de acidentes
escorpiônicos da Região Amazônica?

**Resposta esperada:** Porque os acidentes escorpiônicos causados por
espécies da Região Amazônica (ex.: *Tityus obscurus*) cursam
predominantemente com manifestações neuromusculares, como mioclonias.
Os benzodiazepínicos, como o diazepam, auxiliam no controle dessas
mioclonias, proporcionando alívio dos sintomas e conforto ao paciente —
diferente do padrão de outras regiões do Brasil, onde predominam
manifestações cardiovasculares, respiratórias e digestivas.

**Resposta Gerada:** [Resposta 9](answers.md#resposta-9)

**Resposta Gerada (otimizada):** [Resposta 9 (Optimized Chunking)](answers_optimized_chunking.md#resposta-9)

**Trecho-fonte:** *PCDT - Acidentes Escorpiônicos.pdf*, página 14.

> "Benzodiazepínicos, como o diazepam, podem ser utilizados no
> tratamento dos acidentes escorpiônicos envolvendo espécies da Região
> Amazônica, onde as manifestações neuromusculares são prevalentes.
> Nesse contexto, essa terapia medicamentosa auxilia no controle das
> mioclonias, proporcionando alívio dos sintomas e conforto ao
> paciente."

---

### Pergunta 10

**Pergunta:** O que diferencia as causas congênitas das adquiridas na
etiologia da deficiência de GH (DGH) e quais fatores de risco ou eventos
na vida adulta podem lesionar a região hipotálamo-hipofisária?

**Resposta esperada:** As causas congênitas de DGH são menos comuns e
podem ou não estar associadas a defeitos anatômicos. As causas
adquiridas incluem tumores e doenças infiltrativas da região
hipotálamo-hipofisária, tratamento cirúrgico de lesões hipofisárias,
trauma, infecções e infarto hipofisário ou radioterapia craniana. Em
adultos especificamente, a DGH pode ser a persistência de um quadro
iniciado na infância ou decorrer de uma lesão da região
hipotálamo-hipofisária (tumor, irradiação, trauma, doença inflamatória
ou infecciosa) surgida já na vida adulta.

**Resposta Gerada:** [Resposta 10](answers.md#resposta-10)

**Resposta Gerada (otimizada):** [Resposta 10 (Optimized Chunking)](answers_optimized_chunking.md#resposta-10)

**Trecho-fonte:** *Deficiência do Hormônio de Crescimento - HipopituitarismO.pdf*, páginas 3 e 5.

> (p. 3) "A deficiência de GH (DGH) pode ser congênita ou adquirida. As
> causas congênitas são menos comuns e podem ou não estar associadas a
> defeitos anatômicos. As causas adquiridas incluem tumores e doenças
> infiltrativas da região hipotálamo-hipofisária, tratamento cirúrgico
> de lesões hipofisárias, trauma, infecções e infarto hipofisário ou
> radioterapia craniana."
>
> (p. 5) "A DGH em adultos pode ser isolada ou associada a outras
> deficiências hormonais, e pode ser decorrente de duas situações:
> persistência da DGH iniciada na infância; presença de lesão da região
> hipotálamo-hipofisária (tumor, irradiação, trauma, doença inflamatória
> ou infecciosa) surgida na vida adulta."

---

### Pergunta 11

**Pergunta:** Como deve ser administrado o tratamento medicamentoso da
epilepsia?

**Resposta esperada:** O tratamento é feito com fármacos antiepilépticos
(FAE), escolhidos conforme o mecanismo de ação mais adequado ao tipo de
crise do paciente. Busca-se, idealmente, controlar as crises em
monoterapia. Em caso de falha do primeiro fármaco, faz-se a substituição
gradual por outro de primeira escolha, mantendo a monoterapia (introdução
gradual do segundo fármaco até controle das crises ou intolerância, com
retirada gradual do primeiro se houver controle). Se a segunda tentativa
de monoterapia também falhar, pode-se associar dois fármacos
antiepilépticos (politerapia); a associação de mais de dois fármacos não
é preconizada, pois poucos pacientes obtêm benefício adicional.

**Resposta Gerada:** [Resposta 11](answers.md#resposta-11)

**Resposta Gerada (otimizada):** [Resposta 11 (Optimized Chunking)](answers_optimized_chunking.md#resposta-11)

**Trecho-fonte:** *PCDT Epilepsia.pdf*, páginas 10-11.

> (p. 10) "Deve-se buscar um fármaco antiepiléptico com um mecanismo de
> ação eficaz sobre os mecanismos de geração e propagação, específicos
> das crises do paciente, individualmente."
>
> (p. 11) "Em caso de falha do primeiro fármaco, deve-se tentar sempre
> fazer a substituição gradual por outro, de primeira escolha,
> mantendo-se a monoterapia. Em caso de falha na segunda tentativa de
> monoterapia, pode-se tentar a combinação de dois fármacos
> antiepilépticos conforme evidências de benefício [...]. Poucos
> pacientes parecem obter benefício adicional com a associação de mais
> de dois fármacos, por isso, tal conduta não está preconizada neste
> Protocolo."

---

### Pergunta 12

**Pergunta:** Quais são os critérios de suspensão do tratamento com
somatropina em casos de síndrome de Turner?

**Resposta esperada:** O tratamento com somatropina deve ser
interrompido quando a idade óssea atingir 13,5 a 14 anos, ou quando a
velocidade de crescimento cair para menos de 2 cm/ano.

**Resposta Gerada:** [Resposta 12](answers.md#resposta-12)

**Resposta Gerada (otimizada):** [Resposta 12 (Optimized Chunking)](answers_optimized_chunking.md#resposta-12)

**Trecho-fonte:** *Síndrome de Turner.pdf*, página 6.

> "6.1.3. Critérios de interrupção. O tratamento com somatropina deverá
> ser interrompido nas seguintes situações: Idade óssea de 13,5 a 14
> anos de idade; Velocidade de crescimento inferior a 2 cm/ano."

---

## 9. Avaliação de Fidelidade e Relevância

Para cada pergunta do gabarito (Seção 8), execute um LLM as a judge
para validar a qualidade das respostas obtidas. 

**Definições:**
- **Fidelidade** — a resposta gerada está fundamentada no contexto
  recuperado (sem alucinação/invenção)? Toda afirmação feita pode ser
  encontrada nos trechos recuperados?
- **Relevância** — a resposta de fato responde à pergunta feita (mesmo
  que fundamentada, pode ser irrelevante/incompleta/tangencial)?
- **Nota do Juiz (LLM-as-Judge)** — nota de 1 a 5 atribuída por um LLM
  avaliador (sugestão: usar um modelo diferente do usado no pipeline de
  geração, para reduzir viés de auto-avaliação), com base em um rubrica
  de fidelidade + relevância combinadas.

| ID | Pergunta (resumo) | Fidelidade (Sim/Parcial/Não) | Relevância (Sim/Parcial/Não) | Nota do Juiz (1-5) |
|----|--------------------|------------------------------|-------------------------------|:------------------:|
| 1  | Mecanismo patológico da DB | | | |
| 2  | Sinais neonatais de DGH | | | |
| 3  | Exames p/ arritmia e hipoglicemia no AVC | | | |
| 4  | Monitorização glicemia/temperatura pós-trombólise | | | |
| 5  | Dabigatrana 48h e idarucizumabe | | | |
| 6  | Classificação da IA e mineralocorticoide | | | |
| 7  | Janela de tempo do alteplase | | | |
| 8  | Amostragem linfonodal mínima (cólon) | | | |
| 9  | Benzodiazepínicos em escorpionismo amazônico | | | |
| 10 | Causas congênitas x adquiridas de DGH | | | |
| 11 | Tratamento medicamentoso da epilepsia | | | |
| 12 | Critérios de suspensão de somatropina (Turner) | | | |

### 9.1. Avaliação de Fidelidade e Relevância (após otimização de chunks)

| ID | Pergunta (resumo) | Fidelidade (Sim/Parcial/Não) | Relevância (Sim/Parcial/Não) | Nota do Juiz (1-5) |
|----|--------------------|------------------------------|-------------------------------|:------------------:|
| 1  | Mecanismo patológico da DB | | | |
| 2  | Sinais neonatais de DGH | | | |
| 3  | Exames p/ arritmia e hipoglicemia no AVC | | | |
| 4  | Monitorização glicemia/temperatura pós-trombólise | | | |
| 5  | Dabigatrana 48h e idarucizumabe | | | |
| 6  | Classificação da IA e mineralocorticoide | | | |
| 7  | Janela de tempo do alteplase | | | |
| 8  | Amostragem linfonodal mínima (cólon) | | | |
| 9  | Benzodiazepínicos em escorpionismo amazônico | | | |
| 10 | Causas congênitas x adquiridas de DGH | | | |
| 11 | Tratamento medicamentoso da epilepsia | | | |
| 12 | Critérios de suspensão de somatropina (Turner) | | | |

---

## 10. Detecção de Respostas Insatisfatórias

Para cada resposta problemática identificada na Seção 9 (fidelidade ou
relevância = "Parcial"/"Não"), preencher uma linha abaixo, nomeando a
causa provável.

**Tipos de falha (categorias sugeridas — usar como referência ao
preencher "Tipo de falha"):**
- **Alucinação** — resposta contém informação não presente em nenhum
  trecho recuperado (dado, dose, critério ou recomendação inventados).
- **Contexto irrelevante recuperado** — a recuperação (retrieval) trouxe
  chunks de PCDT que não têm relação com a pergunta (falha de
  decomposição, embedding ou de ranking).
- **Contexto relevante, mas incompleto** — os chunks certos foram
  recuperados, mas faltou informação (ex.: `MAX_CONTEXT_CHUNKS` cortou
  chunks relevantes, ou chunking dividiu a informação necessária entre
  trechos não recuperados juntos).
- **Não respondeu / resposta vazia ou truncada** — falha técnica do LLM
  (ex.: truncamento por `num_ctx`/`num_predict`, falha de parsing de
  saída estruturada) impediu uma resposta completa.
- **Recusa indevida** — o sistema respondeu "não sei" apesar de a
  informação estar de fato disponível no contexto recuperado.

| ID | Pergunta (resumo) | Tipo de falha | Causa provável | Gravidade (Baixa/Média/Alta/**CRÍTICA — alucinação**) | Ação corretiva sugerida |
|----|--------------------|----------------|-----------------|:-----------------------------------------------------:|--------------------------|
|    |                    |                |                 |                                                       |                          |
|    |                    |                |                 |                                                       |                          |
|    |                    |                |                 |                                                       |                          |
## 11. Otimização de Chunks

Uma etapa de enriquecimento semântico foi introduzida no fluxo antes da segmentação final em chunks. Esse passo extrai os conceitos-chave de cada seção de forma automatizada, utilizando métodos de identificação de candidatos, ordenação local e filtros de IDF sobre todo o conjunto de documentos. Dessa forma, geramos um grupo de `semantic_entities` associado a cada chunk (mapeando, de forma dinâmica, expressões como *atraso no desenvolvimento neuropsicomotor*, *hiperventilação*, *aminobenzoato como substrato*, *doença hepática*, *quimioluminescência* ou *suspensão do gh*), agregando valor à representação do texto e melhorando o desempenho na recuperação de informações.

Para mais detalhes, ler [README.md](../src/chunking/README.md).