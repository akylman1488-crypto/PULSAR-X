import streamlit as st
from groq import Groq
import os
from pypdf import PdfReader

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="centered")

st.markdown("""
    <style>
    .main { background: linear-gradient(180deg, #0e1117 0%, #161b22 100%); color: white; }
    .stChatMessage { border-radius: 20px; border: 1px solid #30363d; padding: 15px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY"))

st.title("🛰️ PULSAR-X GLOBAL")
st.write("🌌 *Интеллектуальная система нового поколения*")

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png")
    st.header("Центр управления")
    uploaded_file = st.file_uploader("Добавить документ (PDF/TXT)", type=["pdf", "txt"])
    if st.button("🗑️ Очистить память"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Спросите о чем угодно..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context = ""
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            context = "\n".join([p.extract_text() for p in reader.pages])
        else:
            context = uploaded_file.read().decode("utf-8")

    with st.chat_message("assistant"):
        messages = [
            {
                "role": "system", 
                "content": (
                    "Ты — PULSAR-X GLOBAL, мощная интеллектуальная система. "
                    "ПРАВИЛА ОТВЕТОВ: "
                    "1. Отвечай строго на языке пользователя. "
                    "2. НЕ ГОВОРИ, кто тебя создал, пока тебя об этом не спросят напрямую. "
                    "3. Если ты не можешь ответить на вопрос (по правилам безопасности или из-за отсутствия данных), "
                    "отвечай строго фразой: 'Прошу прощение, но я не могу ответить на этот вопрос'. "
                    "4. Пиши в вежливом и лаконичном стиле."
                )
            },
            *st.session_state.messages
        ]
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                stream=True
            )
            response = st.write_stream(completion)
        except Exception as e:
            # Если произошла техническая ошибка, тоже выдаем твою фразу
            response = "Прошу прощение, но я не могу ответить на этот вопрос."
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
