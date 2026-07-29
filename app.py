import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="IA Brigada",
    page_icon="🚒", 
    layout="centered"
)

# ==========================================
# SUA LOGOTIPO EM BASE64 (EMBUTIDA)
# ==========================================
LOGO_BASE64 = "data:image/png;base64,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3JlIFRpbWUtU3RhbXBpbmcgSUNBIEczAhNsJu7t0Jzc7HZw1UPm2lBOOpxeMAsGCWCGSAFlAwQCAaCBpDAaBgkqhkiG9w0BCQMxDQYLKoZIhvcNAQkQAQQwHAYJKoZIhvcNAQkFMQ8XDTI2MDgwNzEwMzA0MFowLwYJKoZIhvcNAQkEMSIEIMzIveTzcorC1fTj3Jfgfgfrqh63s+cnqs3SYfnOGWWIMDcGCyqGSIb3DQEJEAIvMSgwJjAkMCIEIHkIgdw9M5jxM+VMLtaqvNF2bX/FFBi0oqyfTBmWbOVtMAoGCCqGSM49BAMCBEcwRQIhAIjDRc+lLMiYVknv+WfI3c9OyKBE92PvWkXvbMXu5ryfAiABzSrdyT5HihmAV2rSJ1VOHDOdUiRaiuqb35NYK7isRvZYQA2+jDhYfbuRsR2RlAmCuwBNWkHePPXHhNo/hmk+akAIDptNngBATpilhesPMnhqTlE9qp6OXq5ezVNlb+AaZhAAAAISanVtYgAAACdqdW1kYzJjbAARABCAAACqADibcQNjMnBhLmNsYWltLnYyAAAAAeNjYm9ypWppbnN0YW5jZUlEeCQxZjllOGQxNi02MTVhLTczZGTu2I2MC00YzVkZjIyYWMzZjB0Y2xhaW1fZ2VuZXJhdG9yX2luZm+iZG5hbWV4Ikdvb2dsZSBDMlBBIENvcmUgR2VuZXJhdG9yIExpYnJhcnlndmVyc2lvbnM5NTc5ODEwMDk6OTU3OTgxMDA5cmNyZWF0ZWRfYXNzZXJ0aW9uc4OiY3VybHgtc2VsZiNqdW1iZj1jMnBhLmFzc2VydGlvbnMvYzJwYS5pbmdyZWRpZW50LnYzZGhhc2hYIGzEFfGHzvCK0K9fActk+3Un0IPwXcYIhd3j0xvZyfJ1omN1cmx4KnNlbGYjanVtYmY9YzJwYS5hc3NlcnRpb25zL2MycGEuYWN0aW9ucy52MmRoYXNoWCAiz2j+HvlVzYXfd7NlshHOjXXZ4imYnh/TdYPBWHixIKJjdXJseClzZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmhhc2guZGF0YWRoYXNoWCCltQT+nq0YQzcLOVMBC1K4dBg+sO3lY9jIgfuS0ztDF2lzaWduYXR1cmV4GXNlbGYjanVtYmY9YzJwYS5zaWduYXR1cmVjYWxnZnNoYTI1NgAAC2tqdW1iAAAAKWp1bWRjMmFzABEAEIAAAKoAOJtxA2MycGEuYXNzZXJ0aW9ucwAAAACcanVtYgAAAChqdW1kY2JvcgARABCAAACqADibcQNjMnBhLmhhc2guZGF0YQAAAABsY2JvcqRqZXhjbHVzaW9uc4GiZXN0YXJ0GCFmbGVuZ3RoGUXAY2FsZ2ZzaGEyNTZkaGFzaFggaBUBY5Zkvvrs9Zbms+TyrMkqTvwNmf3GHaQe5FD9965jcGFkTQAAAAAAAAAAAAAAAAAAAAGEanVtYgAAAClqdW1kY2JvcgARABCAAACqADibcQNjMnBhLmFjdGlvbnMudjIAAAABU2Nib3KhZ2FjdGlvbnODomZhY3Rpb25rYzJwYS5vcGVuZdk..."

# ==========================================
# CONFIGURAÇÃO GEMINI
# ==========================================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Erro ao configurar a chave de API.")
    st.stop()

generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

system_instruction = """
Você é a IA Brigada, assistente virtual especializada, técnica e suporte operacional para Bombeiros Civis.
Seu tom de voz deve ser profissional, direto e objetivo.
Forneça a resposta técnica imediata na primeira frase e complemente com os detalhes operacionais em seguida.

BASE DE CONHECIMENTO OBRIGATÓRIA:
- Termo "Pássaro de fogo": Refere-se a balões (crime ambiental).
- Análise de Imagem: Avalie imagens de campo identificando inconformidades, corrosão ou falhas.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# ==========================================
# CABEÇALHO PRINCIPAL (EXIBIÇÃO DA LOGO)
# ==========================================
col_logo, col_texto = st.columns([1, 3.5])

with col_logo:
    if LOGO_BASE64.startswith("data:image"):
        st.markdown(
            f'<img src="{LOGO_BASE64}" style="width: 100%; max-width: 180px; border-radius: 8px;">',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div style="font-size: 60px; text-align: center;">🚒</div>', unsafe_allow_html=True)

with col_texto:
    st.markdown('<h1 style="margin: 0px; text-align: left;">IA Brigada</h1>', unsafe_allow_html=True)
    st.markdown('<p style="margin: -5px 0 0 0; color: #6b7280; font-size: 18px; text-align: left;">Assistente Virtual • Operações e Inspeção</p>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# BARRA LATERAL (CENTRAL DE INSPEÇÃO)
# ==========================================
with st.sidebar:
    st.markdown("### Central de Inspeção")
    st.write("Envie imagens de estruturas ou equipamentos para análise técnica.")
    uploaded_file = st.file_uploader("Selecionar arquivo de imagem", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img_for_display = Image.open(uploaded_file)
        st.image(img_for_display, caption="Imagem carregada", use_container_width=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"]:
            st.image(message["image"], width=250)

if prompt := st.chat_input("Digite sua dúvida operacional..."):
    current_img = Image.open(uploaded_file) if uploaded_file else None
    
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt, 
        "image": current_img
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if current_img:
            st.image(current_img, width=250)

    with st.chat_message("assistant"):
        with st.spinner("Processando análise técnica..."):
            try:
                if current_img:
                    response = model.generate_content([prompt, current_img])
                else:
                    chat = model.start_chat(history=[
                        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                        for m in st.session_state.messages[:-1]
                    ])
                    response = chat.send_message(prompt)
                
                full_res = response.text
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"Erro ao processar: {e}")