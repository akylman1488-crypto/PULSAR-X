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

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.title("PULSAR-X")
    st.subheader("🧠 Самообучение")
    exp = get_experience()
    st.caption("Накопленный опыт:")
    st.text_area("", exp, height=150, disabled=True)

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

        current_exp = get_experience()
        system_instructions = (
            f"Ты — PULSAR-X GLOBAL, самообучающаяся система. Твой накопленный опыт: {current_exp}. "
            "Используй этот опыт, чтобы не повторять ошибок. Отвечай на языке пользователя. "
            "Если тебя спросят о создателе — отвечай 'Исанур'. В других случаях не упоминай его."
        )
        
        messages = [{"role": "system", "content": system_instructions}, *st.session_state.messages]

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

        if "запомни" in prompt.lower() or "ошибка" in prompt.lower():
            save_experience(f"Пользователь сказал: {prompt}. Мой ответ был: {full_response}")
            st.toast("Система адаптировалась: новый опыт сохранен!")
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
