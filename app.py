import streamlit as st

st.sidebar.image("https://raw.githubusercontent.com/Isanur/pulsar-x/main/logo.png", width=200)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png")
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
        response_placeholder = st.empty()
        full_response = ""
        
        system_msg = (
            "Ты — PULSAR-X GLOBAL. Твой создатель Исанур. "
            "Ты мощный полиглот: всегда отвечай на языке, на котором пишет пользователь. "
            "Используй форматирование Markdown и эмодзи для красоты. "
            f"Контекст документа: {context[:2000]}"
        )
        
        messages = [{"role": "system", "content": system_msg}]
        for m in st.session_state.messages[-6:]:
            messages.append({"role": m["role"], "content": m["content"]})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

st.markdown("""
    <style>
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .stImage img {
        animation: rotate 20s linear infinite; /* Логотип будет медленно вращаться */
    }
    </style>
    """, unsafe_allow_html=True)
