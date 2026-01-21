import streamlit as st
from groq import Groq
import os
from PyPDF2 import PdfReader

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

MEMORY_FILE = "pulsar_experience.txt"

def get_experience():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_experience(new_lesson):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n- {new_lesson}")

def read_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except:
        return "Ошибка чтения PDF"

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Добавьте GROQ_API_KEY в Secrets приложения!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🛰️ PULSAR-X")
    
    st.divider()
    st.subheader("📁 Загрузка знаний")
    uploaded_file = st.file_uploader("Загрузи PDF или TXT", type=["pdf", "txt"])
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.session_state.doc_context = read_pdf(uploaded_file)
        else:
            st.session_state.doc_context = uploaded_file.read().decode("utf-8")
        st.success("Файл изучен!")

    if st.button("🗑️ Забыть файл"):
        st.session_state.doc_context = ""
        st.rerun()

    st.divider()
    with st.expander("🧠 Мой накопленный опыт"):
        st.write(get_experience() if get_experience() else "Опыта пока нет.")

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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Спросите о чем угодно..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        res_box = st.empty()
        full_res = ""

        context = f"КОНТЕКСТ ИЗ ФАЙЛА: {st.session_state.doc_context[:1500]}" if st.session_state.doc_context else ""
        exp = f"ТВОЙ ПРОШЛЫЙ ОПЫТ: {get_experience()[-1000:]}"
        
        system_prompt = (
            f"Ты — PULSAR-X GLOBAL. {exp} {context} "
            "1. Если в контексте файла есть ответ, используй его. "
            "2. Если не можешь ответить, пиши: 'Прошу прощение, но я не могу ответить на этот вопрос'. "
            "3. Про создателя (Исанура) говори только если спросят."
        )
        
        msgs = [{"role": "system", "content": system_prompt}] + st.session_state.messages

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)

            if "запомни" in prompt.lower() or "научись" in prompt.lower():
                save_experience(f"Запрос: {prompt} | Твой успешный ответ: {full_res[:100]}...")
                st.toast("Я запомнил это!")
                
        except:
            full_res = "Прошу прощение, но я не могу ответить на этот вопрос."
            res_box.markdown(full_res)

    st.session_state.messages.append({"role": "assistant", "content": full_res})
