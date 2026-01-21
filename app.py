import streamlit as st
from groq import Groq
import os
from PyPDF2 import PdfReader # Библиотека для чтения PDF

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

MEMORY_FILE = "pulsar_experience.txt"

def get_experience():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.title("Центр управления")

    uploaded_file = st.file_uploader("Добавить документ (PDF/TXT)", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.session_state.doc_context = read_pdf(uploaded_file)
        else:
            st.session_state.doc_context = uploaded_file.read().decode("utf-8")
        st.success("Документ загружен и изучен!")

    st.divider()

    if st.button("🗑️ Очистить контекст файла"):
        st.session_state.doc_context = ""
        st.rerun()

    st.divider()
    with st.expander("🧠 База самообучения"):
        st.write(get_experience())

col1, col2 = st.columns([4, 1])
with col1:
    st.title("🛰️ PULSAR-X GLOBAL")
with col2:
    if st.button("➕ Новый"):
        st.session_state.messages = []
        st.rerun()

st.divider()

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

        context_info = f"\nКОНТЕКСТ ЗАГРУЖЕННОГО ФАЙЛА: {st.session_state.doc_context[:2000]}" if st.session_state.doc_context else ""
        
        system_msg = (
            f"Ты — PULSAR-X GLOBAL. {context_info} "
            "Если в контексте файла есть ответ, используй его. "
            "Если тебя спросят о создателе — отвечай 'Исанур'."
        )
        
        msgs = [{"role": "system", "content": system_msg}] + st.session_state.messages

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=msgs,
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
