import streamlit as st
from groq import Groq
import os
import datetime
import pandas as pd
from PyPDF2 import PdfReader

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://blogger.googleusercontent.com/img/a/AVvXsEiB-6BuccqoXpOjS2N7yboF1Nd4o_7B3kqo8i-vHtsTJi1TFKCm58DYBHTx6SDDDp4J5MnivHcITN_xFLyS9zOes3qf8OQVky63oXbPksqN4TycQ_Wn2sj-2AWCEK3gkrqEDeMo0c6FgT7W0d2d355GNx2PewlrdPa4h6nnVtnEZeMcaB0QA_Qa3kGPKfaV=s2160-rw
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .stApp h1 {
        color: white !important;
        -webkit-text-fill-color: white !important;
        text-shadow: 2px 2px 0 #000 !important;
    }

    /* МАКСИМАЛЬНО СТРОГИЙ БЕЛЫЙ ЦВЕТ ДЛЯ ВСЕХ ЭЛЕМЕНТОВ ЧАТА */
    [data-testid="stChatMessage"] *, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] p {
        color: white !important;
        -webkit-text-fill-color: white !important;
        text-shadow: 1px 1px 2px black !important;
    }

    [data-testid="stSidebar"] { background-color: white !important; }
    [data-testid="stSidebar"] * { color: black !important; -webkit-text-fill-color: black !important; }

    [data-testid="stChatInput"] { background-color: white !important; border: 2px solid black !important; }
    [data-testid="stChatInput"] textarea { color: black !important; -webkit-text-fill-color: black !important; }

    header, [data-testid="stHeader"], [data-testid="stBottom"] > div {
        background: transparent !important;
    }
    </style>

    <script>
    function fixAllText() {
        const doc = window.parent.document;
        // Находим все элементы внутри сообщений и красим их в белый
        const elements = doc.querySelectorAll('[data-testid="stChatMessage"] *');
        elements.forEach(el => {
            el.style.color = 'white';
            el.style.webkitTextFillColor = 'white';
        });

        const menuBtn = doc.querySelector('button[data-testid="stHeaderSidebarNav"]');
        if (menuBtn) {
            menuBtn.style.backgroundColor = 'white';
            menuBtn.style.borderRadius = '50%';
        }
    }
    setInterval(fixAllText, 1000);
    </script>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

with st.sidebar:
    st.title("Центр управления")
    uploaded_file = st.file_uploader("Анализ данных (PDF/TXT/CSV)", type=["pdf", "txt", "csv"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            st.session_state.doc_context = "ТЕКСТ ИЗ PDF:\n" + "".join([page.extract_text() for page in reader.pages])
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            st.session_state.doc_context = "ДАННЫЕ ИЗ ТАБЛИЦЫ (CSV):\n" + df.head(20).to_string()
        else:
            st.session_state.doc_context = uploaded_file.read().decode("utf-8")

col1, col2 = st.columns([4, 1])
with col1:
    st.title("🛰️ PULSAR-X GLOBAL")
with col2:
    if st.button("+ Новый"):
        st.session_state.messages = []
        st.session_state.doc_context = ""
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Спросите PULSAR-X..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        search_context = ""
        if any(word in prompt.lower() for word in ["новости", "найди", "что сейчас"]):
            try:
                from duckduckgo_search import DDGS
                results = DDGS().text(prompt, max_results=3)
                search_context = "\nДАННЫЕ ИЗ ИНТЕРНЕТА:\n" + "\n".join([r['body'] for r in results])
            except:
                pass

        system_msg = (
            f"Ты — PULSAR-X GLOBAL, ИИ-аналитик. Создатель: Исанур. Ты создан в лицее Акылман в Кргызстане. Дата: {current_date}. "
            f"Твоя цель: глубокий анализ и исследование предоставленных данных. "
            f"Если есть контекст, анализируй его максимально подробно. "
            f"КОНТЕКСТ ДЛЯ АНАЛИЗА: {st.session_state.doc_context[:3000]} {search_context}"
        )
        
        msgs = [{"role": "system", "content": system_msg}] + st.session_state.messages
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, stream=True)
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
