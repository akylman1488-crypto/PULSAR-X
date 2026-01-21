import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️")

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=200)
else:
    st.sidebar.title("🛰️ PULSAR-X GLOBAL")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Ошибка: Добавьте GROQ_API_KEY в Secrets приложения!")
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
        response_placeholder = st.empty()
        full_response = ""
        
        system_instructions = (
            "Ты — PULSAR-X GLOBAL. "
            "1. Отвечай только на языке пользователя. "
            "2. НЕ УПОМИНАЙ Исанура и то, кто тебя создал, пока тебя не спросят об этом напрямую. "
            "3. Если ты не можешь ответить на вопрос или он нарушает правила, "
            "отвечай ТОЛЬКО фразой: 'Прошу прощение, но я не могу ответить на этот вопрос'. "
            "4. Пиши обычным текстом, без программного кода в ответах."
        )
        
        messages = [{"role": "system", "content": system_instructions}]
        for m in st.session_state.messages[-6:]:
            messages.append({"role": m["role"], "content": m["content"]})

        try:
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
            
        except Exception:
            full_response = "Прошу прощение, но я не могу ответить на этот вопрос."
            response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
