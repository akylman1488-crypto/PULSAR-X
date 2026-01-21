import streamlit as st
from groq import Groq
import os
from PyPDF2 import PdfReader

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://raw.githubusercontent.com/Isanur-code/pulsar-x/main/IMG_1246.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stHeader"], 
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stCanvas"],
    .main {
        background: transparent !important;
    }

    header {
        background-color: rgba(0,0,0,0) !important;
    }

    [data-testid="stBottom"] > div {
        background: transparent !important;
    }

    .stChatInputContainer {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border-radius: 15px;
    }

    [data-testid="stChatInput"] {
        background-color: rgba(40, 40, 80, 0.6) !important;
        border: 1px solid #764ba2 !important;
        color: white !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 35, 0.7) !important;
        backdrop-filter: blur(10px);
    }

    h1, h2, h3, p, span, .stMarkdown {
        color: white !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.9);
    }

    .stButton>button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

MEMORY_FILE = "pulsar_experience.txt"

def get_experience():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""
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
    st.error("Критическая ошибка: Добавьте GROQ_API_KEY в Secrets приложения Streamlit!")
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
        st.success("Файл изучен системой!")

    if st.button("🗑️ Забыть файл"):
        st.session_state.doc_context = ""
        st.rerun()

    st.divider()

    with st.expander("🧠 База опыта (Адаптивность)"):
        current_exp = get_experience()
        st.write(current_exp if current_exp else "Опыта пока нет. Начните обучение!")

head_col1, head_col2 = st.columns([4, 1])
with head_col1:
    st.title("🛰️ PULSAR-X GLOBAL")
with head_col2:
    if st.button("➕ Новый", use_container_width=True):
        if st.session_state.messages:
            st.session_state.chat_history.append(st.session_state.messages)
        st.session_state.messages = []
        st.session_state.doc_context = "" 
        st.rerun()

st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Спросите PULSAR-X о чем угодно..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""

        file_info = f"\n[КОНТЕКСТ ИЗ ВАШЕГО ФАЙЛА: {st.session_state.doc_context[:1500]}]" if st.session_state.doc_context else ""
        past_lessons = f"\n[ТВОЙ НАКОПЛЕННЫЙ ОПЫТ: {get_experience()[-1000:]}]"
        
        system_instruction = (
            f"Ты — PULSAR-X GLOBAL, интеллектуальная самообучающаяся система. {past_lessons} {file_info} "
            "ИНСТРУКЦИИ: "
            "1. Если в контексте файла есть информация для ответа — используй её в приоритете. "
            "2. Если вопрос выходит за рамки твоих знаний или правил, отвечай строго: 'Прошу прощение, но я не могу ответить на этот вопрос'. "
            "3. О создателе (Исануре) говори только если спросят напрямую."
        )

        groq_messages = [{"role": "system", "content": system_instruction}] + st.session_state.messages

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=groq_messages,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)

            if any(word in prompt.lower() for word in ["запомни", "научись", "важно"]):
                save_experience(f"Пользователь: {prompt} | Ты ответил: {full_response[:150]}...")
                st.toast("Новый опыт сохранен в базу!")
                
        except Exception as e:
            full_response = "Прошу прощение, но я не могу ответить на этот вопрос."
            response_container.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
