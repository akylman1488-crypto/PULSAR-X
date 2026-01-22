import streamlit as st
from groq import Groq
import datetime
import pandas as pd
from PyPDF2 import PdfReader

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?q=80&w=1200&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stChatMessage"] *, .stMarkdown * {
    color: white !important;
    -webkit-text-fill-color: white !important;
    text-shadow: 1px 1px 2px black !important;
}
[data-testid="stSidebar"] { background-color: white !important; }
[data-testid="stSidebar"] * { color: black !important; }
[data-testid="stChatInput"] { background-color: white !important; border: 2px solid black !important; }
[data-testid="stChatInput"] textarea { color: black !important; }
</style>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

with st.sidebar:
    st.title("Управление")
    uploaded_file = st.file_uploader("Данные (PDF/TXT/CSV)", type=["pdf", "txt", "csv"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            st.session_state.doc_context = "PDF: " + "".join([p.extract_text() for p in reader.pages])
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            st.session_state.doc_context = "CSV: " + df.head(10).to_string()
        else:
            st.session_state.doc_context = uploaded_file.read().decode("utf-8")
    if st.button("Очистить"):
        st.session_state.messages = []
        st.session_state.doc_context = ""
        st.rerun()

st.title("🛰️ PULSAR-X GLOBAL")

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
        sys_msg = f"PULSAR-X GLOBAL (Исанур). Дата: {datetime.datetime.now().date()}. Функции: Код, Анализ, Логика. Контекст: {st.session_state.doc_context[:1000]}"
        
        try:
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Ошибка: {e}")
