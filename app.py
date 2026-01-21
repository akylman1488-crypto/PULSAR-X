import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️")

try:
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=200)
    else:
        st.sidebar.title("🛰️ PULSAR-X")
except:
    st.sidebar.write("PULSAR-X GLOBAL")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Ошибка ключа! Добавьте GROQ_API_KEY в Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Спросите PULSAR-X..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = [
            {"role": "system", "content": "Ты PULSAR-X GLOBAL. Создатель - Исанур. Отвечай на языке пользователя."},
            *st.session_state.messages
        ]
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )
        response = st.write_stream(completion)
    st.session_state.messages.append({"role": "assistant", "content": response})
