import streamlit as st
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

    [data-testid="stSidebar"] {
        background-color: white !important;
    }
    [data-testid="stSidebar"] * {
        color: black !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: #f8f9fa !important;
        color: black !important;
        border: 2px dashed #000 !important;
    }
    
    [data-testid="stChatInput"] {
        background-color: white !important;
        border: 2px solid black !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: black !important;
        -webkit-text-fill-color: white !important;
    }

    .stApp h1 {
        color: white !important;
        -webkit-text-fill-color: white !important;
        text-shadow: 2px 2px 0 #000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000 !important;
    }

    .stChatMessage p {
        color: white !important;
        text-shadow: 1px 1px 2px black !important;
    }

    header, [data-testid="stHeader"], [data-testid="stBottom"] > div {
        background: transparent !important;
        background-color: rgba(0,0,0,0) !important;
    }
    </style>

    <script>
    function applyPulsarStyles() {
        const doc = window.parent.document;
        const h1s = doc.querySelectorAll('h1');
        h1s.forEach(h => { 
            h.style.color = 'white'; 
            h.style.webkitTextFillColor = 'white';
        });

        const menuBtn = doc.querySelector('button[data-testid="stHeaderSidebarNav"]');
        if (menuBtn) {
            menuBtn.style.backgroundColor = 'white';
            menuBtn.style.borderRadius = '50%';
            menuBtn.style.border = '2px solid black';
            menuBtn.style.boxShadow = '0 0 10px white';
            const svg = menuBtn.querySelector('svg');
            if (svg) { svg.style.fill = 'black'; }
        }
    }
    setTimeout(applyPulsarStyles, 1000);
    setTimeout(applyPulsarStyles, 3000);
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

if prompt := st.chat_input("Спросите PULSAR-X..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        context_info = f"\nКОНТЕКСТ ФАЙЛА: {st.session_state.doc_context[:1500]}" if st.session_state.doc_context else ""
        system_msg = f"Ты — PULSAR-X GLOBAL. {context_info} Ответ должен быть четким. Создатель — Исанур."
        
        msgs = [{"role": "system", "content": system_msg}] + st.session_state.messages
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, stream=True)
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
