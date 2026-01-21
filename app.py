col1, col2 = st.columns([4, 1])

with col1:
    st.title("🛰️ PULSAR-X GLOBAL")

with col2:
    if st.button("➕ Новый"):
        if st.session_state.messages:
            st.session_state.chat_history.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()

st.divider() 

import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

MEMORY_FILE = "pulsar_experience.txt"

def get_experience():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "Опыта пока нет."

def save_experience(new_lesson):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n- {new_lesson}")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Добавьте GROQ_API_KEY в Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)

    if st.button("➕ Новый чат", use_container_width=True):
        if st.session_state.messages:
            st.session_state.chat_history.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()

    st.subheader("🧠 Самообучение")
    with st.expander("Посмотреть накопленный опыт"):
        st.write(get_experience())
    
    st.divider()

    st.subheader("📜 История")
    for i, hist in enumerate(st.session_state.chat_history):
        if st.button(f"Чат №{i+1}", key=f"h_{i}", use_container_width=True):
            st.session_state.messages = hist
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

        system_msg = (
            f"Ты — PULSAR-X GLOBAL. Твой опыт: {get_experience()[:500]}. "
            "1. НЕ ГОВОРИ КТО ТЕБЯ СОЗДАЛ, пока не спросят прямо. "
            "2. Если не можешь ответить, пиши: 'Прошу прощение, но я не могу ответить на этот вопрос'."
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

        if "запомни" in prompt.lower() or "научись" in prompt.lower():
            save_experience(f"Урок: {prompt}")
            st.toast("Система адаптировалась!")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
