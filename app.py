import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64
import os

# ==========================================
# FUNÇÃO PARA CARREGAR LOGO EM BASE64
# ==========================================
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="IA Brigada", page_icon="🧯", layout="centered")

# ==========================================
# CONFIGURAÇÃO GEMINI
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Erro: Chave de API não configurada.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="Você é a IA Brigada, assistente técnica especializada em Bombeiros Civis. Responda de forma profissional, direta e técnica."
)

# ==========================================
# CABEÇALHO COM LOGO EMBUTIDA
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])
logo_base64 = get_image_base64("logo_brigada.png")

with col2:
    if logo_base64:
        st.markdown(
            f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_base64}" width="280"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h1 style='text-align:center;'>IA BRIGADA</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:#6b7280; font-size:16px;'>Assistente Virtual para Bombeiros Civis</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### Central de Inspeção")
    uploaded_file = st.file_uploader("Selecionar imagem", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Imagem carregada", use_container_width=True)

# ==========================================
# CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua dúvida operacional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            try:
                img = Image.open(uploaded_file) if uploaded_file else None
                response = model.generate_content([prompt, img] if img else prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro: {e}")
                