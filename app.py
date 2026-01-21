import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history_list" not in st.session_state:
    st.session_state.chat_history_list = []

with st.sidebar:
    # Твой новый логотип
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.title("PULSAR-X")
    
    if st.button("➕ Новый чат", use_container_width=True):
        if st.session_state.messages:
            st.session_state.chat_history_list.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("История чатов")
    for i, history in enumerate(st.session_state.chat_history_list):
        if st.button(f"Чат №{i+1}", key=f"hist_{i}", use_container_width=True):
            st.session_state.messages = history
            st.rerun()

st.markdown("### 🛰️ PULSAR-X GLOBAL")

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

        messages = [
            {"role": "system", "content": "Ты — PULSAR-X GLOBAL. Не говори, кто тебя создал, пока не спросят. Если не можешь ответить, пиши: 'Прошу прощение, но я не могу ответить на этот вопрос'."},
            *st.session_state.messages
        ]

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
