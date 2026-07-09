"""
Interface em Streamlit para o sistema RAG utilizando a coleção de PCDT
(Protocolos Clínicos e Diretrizes Terapêuticas) do Ministério da Saúde.

Como executar:
    streamlit run app.py

Esta interface utiliza a função `get_answer` definida em `rag_pipeline.py`
para consultar o pipeline RAG e exibir as respostas ao usuário.
"""

import streamlit as st
from rag_pipeline import get_answer

st.set_page_config(
    page_title="RAG Clínico — Assistente de Acervo",
    page_icon="🩺",
    layout="wide",
)

st.markdown(
    """
    <style>
    .source-name {
        font-weight: 600;
        font-size: 0.95rem;
    }

    .section-text {
        color: #6B7280;
        font-size: 0.82rem;
        margin-top: 4px;
    }

    .source-card {
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_extras(sub_questions: list, low_confidence: bool):
    """Mostra um aviso de confiança e as sub-perguntas usadas na busca,
    quando existirem."""
    if low_confidence:
        st.caption(
            "⚠️ O modelo não teve certeza sobre esta resposta mesmo após "
            "tentar novas buscas. Considere reformular a pergunta ou "
            "conferir os documentos-fonte com atenção."
        )

    if sub_questions:
        with st.expander("🔎 Ver sub-perguntas usadas na busca", expanded=False):
            for sub_question in sub_questions:
                st.markdown(f"- {sub_question}")


def render_sources(sources: list):
    """Renderiza a lista de documentos-fonte recuperados como cards.
 
    Cada fonte traz apenas o arquivo de origem e o caminho da seção
    dentro do documento (o pipeline não retorna um trecho de texto
    nem uma pontuação de similaridade)."""
    with st.expander(
        f"📄 Ver {len(sources)} documento(s) recuperado(s)", expanded=False
    ):
        for i, source in enumerate(sources, start=1):
            section_html = (
                f'<div class="section-text">📍 {source["section"]}</div>'
                if source.get("section")
                else ""
            )
            html = (
                '<div class="source-card">'
                f'<span class="source-name">{i}. {source["source"]}</span>'
                f'{section_html}'
                "</div>"
            )
            st.markdown(html, unsafe_allow_html=True)


if "history" not in st.session_state:
    st.session_state.history = []  

with st.sidebar:
    st.markdown("### 🩺 RAG Clínico")
    st.caption("Assistente sobre Protocolos Clínicos e Diretrizes Terapêuticas")

    st.divider()

    st.markdown("**Sobre**")
    st.write(
        "Este assistente responde perguntas com base nos Protocolos "
        "Clínicos e Diretrizes Terapêuticas (PCDT) do Ministério da "
        "Saúde, recuperando os trechos mais relevantes antes de gerar "
        "a resposta."
    )

    st.divider()

    if st.session_state.history:
        st.metric("Perguntas nesta sessão", len(st.session_state.history))
        st.divider()

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.history = []
        st.rerun()

st.title("🩺 Assistente de Acervo Clínico")
st.caption(
    "Faça uma pergunta sobre os Protocolos Clínicos e Diretrizes "
    "Terapêuticas (PCDT). A resposta indica os documentos-fonte utilizados."
)
st.divider()

for entry in st.session_state.history:
    with st.chat_message("user", avatar="🧑‍⚕️"):
        st.markdown(entry["question"])

    with st.chat_message("assistant", avatar="🩺"):
        st.markdown(entry["answer"])
        render_extras(entry.get("sub_questions", []), entry.get("low_confidence", False))
        if entry["sources"]:
            render_sources(entry["sources"])

question = st.chat_input("Digite sua pergunta sobre o acervo clínico...")

if question:
    with st.chat_message("user", avatar="🧑‍⚕️"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("🧠 Decompondo a pergunta, buscando no acervo e refletindo sobre a resposta..."):
            result = get_answer(question)

        st.markdown(result["answer"])
        render_extras(result.get("sub_questions", []), result.get("low_confidence", False))

        if result["sources"]:
            render_sources(result["sources"])

    st.session_state.history.append(
        {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "sub_questions": result.get("sub_questions", []),
            "low_confidence": result.get("low_confidence", False),
        }
    )