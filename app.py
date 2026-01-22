
from groq import Groq
import os
from PyPDF2 import PdfReader

st.set_page_config(page_title="PULSAR-X GLOBAL", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://blogger.googleusercontent.com/img/a/AVvXsEiB-6BuccqoXpOjS2N7yboF1Nd4o_7B3kqo8i-vHtsTJi1TFKCm58DYBHTx6SDDDp4J5MnivHcITN_xFLyS9zOes3qf8OQVky63oXbPksqN4TycQ_Wn2sj-2AWCEK3gkrqEDeMo0c6FgT7W0d2d355GNx2PewlrdPa4h6nnVtnEZeMcaB0QA_Qa3kGPKfaV=s2160-rw");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .stApp h1 {
        color: white !important;
        -webkit-text-fill-color: white !important;
        text-shadow: 2px 2px 0 #000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000 !important;
    }

    [data-testid="stChatMessage"] div, 
    [data-testid="stChatMessage"] p, 
    .stMarkdown p, 
    .stMarkdown span {
        color: white !important;
        -webkit-text-fill-color: white !important;
        text-shadow: 1px 1px 3px black !important;
    }

    [data-testid="stSidebar"] {
        background-color: white !important;
    }
    [data-testid="stSidebar"] * {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    [data-testid="stChatInput"] {
        background-color: white !important;
        border: 2px solid black !important;
    }
    [data-testid="stChatInput"] textarea {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    header, [data-testid="stHeader"], [data-testid="stBottom"] > div {
        background: transparent !important;
    }
    </style>

    <script>
    function forceWhiteText() {
        const doc = window.parent.document;
        const messages = doc.querySelectorAll('[data-testid="stChatMessage"] p');
        messages.forEach(msg => {
            msg.style.color = 'white';
            msg.style.webkitTextFillColor = 'white';
        });
        
        const h1 = doc.querySelector('h1');
        if (h1) {
            h1.style.color = 'white';
            h1.style.webkitTextFillColor = 'white';
        }

        const menuBtn = doc.querySelector('button[data-testid="stHeaderSidebarNav"]');
        if (menuBtn) {
            menuBtn.style.backgroundColor = 'white';
            menuBtn.style.borderRadius = '50%';
        }
    }
    setInterval(forceWhiteText, 1000);
    </script>
    """, unsafe_allow_html=True)

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
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.title("Центр управления")
    uploaded_file = st.file_uploader("Документ (PDF/TXT)", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.session_state.doc_context = read_pdf(uploaded_file)
        else:
            st.session_state.doc_context = uploaded_file.read().decode("utf-8")
        st.success("Изучено!")

    if st.button("🗑️ Забыть файл"):
        st.session_state.doc_context = ""
        st.rerun()

col1, col2 = st.columns([4, 1])
with col1:
    st.title("🛰️ PULSAR-X GLOBAL")
with col2:
    if st.button("+ Новый"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

import datetime
from duckduckgo_search import DDGS

if prompt := st.chat_input("Спросите PULSAR-X..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        search_context = ""
        if any(word in prompt.lower() for word in ["новости", "найди", "что сейчас", "произошло"]):
            with st.spinner("PULSAR-X ищет в сети..."):
                try:
                    results = DDGS().text(prompt, max_results=3)
                    search_context = "\nНОВОСТИ ИЗ СЕТИ:\n" + "\n".join([r['body'] for r in results])
                except:
                    search_context = ""

        system_msg = (
            f"Ты — PULSAR-X GLOBAL, созданный Исануром. Тебя создали в школе Акылман находящаяся в Кыргызстане. "
            "АКТИВИРОВАНЫ 15 ФУНКЦИЙ: Логика, Код, Анализ нот/данных, Мультиязычность, Поиск. "
            f"У тебя есть доступ к интернету. {search_context} "
            f"ВАЖНО: Не называй дату в каждом сообщении. Упоминай её только если пользователь прямо спросит о текущем дне или дате."
            f"Используй новости только если тебя об этом просят. Не называй дату без необходимости."
        )
        
        msgs = [{"role": "system", "content": system_msg}] + st.session_state.messages
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, stream=True)
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
