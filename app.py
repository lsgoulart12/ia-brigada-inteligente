import base64
import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="IA Brigada",
    page_icon="logo_brigada.png",
    layout="centered"
)

# ==========================================
# CONFIGURAÇÃO GEMINI
# ==========================================
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Erro: A chave GEMINI_API_KEY não foi encontrada nos secrets.")
    st.stop()

genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

system_instruction = """
Você é a IA Brigada, assistente virtual especializada em Bombeiros Civis.

Seu tom deve ser:
- Técnico
- Objetivo
- Profissional
- Direto

Sempre forneça a resposta técnica primeiro.

BASE DE CONHECIMENTO OBRIGATÓRIA:

- Termo "Pássaro de Fogo":
Refere-se a balões.
Crime ambiental previsto no Art. 42 da Lei 9.605/98.
Pena:
- Detenção de 1 a 3 anos
- Multa

- Análise de imagens:
Avalie estruturas, longarinas, equipamentos, painéis, corrosão, falhas visíveis, riscos operacionais e inconformidades.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# ==========================================
# CABEÇALHO LIMPO COM A NOVA LOGO
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    logo_file = "logo_brigada.png"
    if os.path.exists(logo_file):
        # Renderiza a imagem perfeitamente convertida para evitar erros na nuvem
        with open(logo_file, "rb") as f:
            encoded_img = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="text-align: center;"><img src="data:image/png;base64,{encoded_img}" style="width: 100%; max-width: 240px; border-radius: 8px;"></div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Arquivo 'logo_brigada.png' não encontrado na pasta.")

st.markdown(
    """
    <p style='text-align:center; color:#6b7280; font-size:16px; margin-top:5px; margin-bottom:10px;'>
        Assistente Virtual para Bombeiros Civis • Operações e Inspeção
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# SIDEBAR (CENTRAL DE INSPEÇÃO)
# ==========================================
with st.sidebar:
    st.markdown("### Central de Inspeção")
    st.write("Envie imagens de estruturas, equipamentos ou instalações para análise técnica.")
    
    uploaded_file = st.file_uploader(
        "Selecionar imagem",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        preview_image = Image.open(uploaded_file)
        st.image(
            preview_image,
            caption="Imagem carregada",
            use_container_width=True
        )

# ==========================================
# HISTÓRICO E CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image") is not None:
            st.image(message["image"], width=250)

prompt = st.chat_input("Digite sua dúvida operacional ou solicitação de inspeção...")

if prompt:
    current_image = None
    if uploaded_file:
        current_image = Image.open(uploaded_file)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "image": current_image
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)
        if current_image:
            st.image(current_image, width=250)

    with st.chat_message("assistant"):
        with st.spinner("Processando análise técnica..."):
            try:
                if current_image:
                    response = model.generate_content([prompt, current_image])
                else:
                    history = []
                    for msg in st.session_state.messages[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append(
                            {
                                "role": role,
                                "parts": [msg["content"]]
                            }
                        )

                    chat = model.start_chat(history=history)
                    response = chat.send_message(prompt)

                answer = response.text
                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "image": None
                    }
                )

            except Exception as e:
                st.error(f"Erro ao processar a solicitação: {e}")