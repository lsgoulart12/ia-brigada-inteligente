import base64
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configuração da página do Streamlit
st.set_page_config(
    page_title="IA Brigada",
    page_icon="🧯", 
    layout="centered"
)

# Configuração da chave de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Erro ao configurar a chave de API nos segredos do Streamlit.")

# Configuração do modelo especializado para Bombeiros Civis
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
- Termo "Passaro de fogo": Refere-se a balões (crime ambiental, Art. 42 da Lei 9.605/98, com pena de 1 a 3 anos de detenção e multa).
- Análise de Imagem: Avalie imagens de campo (estruturas, longarinas, equipamentos, painéis) identificando inconformidades, corrosão ou falhas.
"""

# Instanciação central do modelo Gemini 2.5 Flash (Multimodal)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# --- CABEÇALHO PRINCIPAL (EXIBIÇÃO ROBUSTA DA MARCA) ---
col_logo, col_texto = st.columns([1, 4])

with col_logo:
    try:
        # Tenta carregar a imagem local se ela existir na pasta
        logo_img = Image.open("logo_brigada.png").convert("RGB")
        st.image(logo_img, use_container_width=True)
    except Exception:
        # Fallback elegante em HTML/CSS caso o arquivo físico falhe na nuvem
        st.markdown(
            """
            <div style="background-color:#b91c1c; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:18px;">
                IA BRIGADA
            </div>
            """,
            unsafe_allow_html=True
        )

with col_texto:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.caption("Assistente Virtual • Operações e Inspeção")

st.markdown("---")

# --- BARRA LATERAL (CENTRAL DE INSPEÇÃO E UPLOAD) ---
with st.sidebar:
    st.markdown("### Central de Inspeção")
    st.write("Envie imagens de estruturas ou equipamentos para análise técnica.")
    uploaded_file = st.file_uploader("Selecionar arquivo de imagem", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img_for_display = Image.open(uploaded_file)
        st.image(img_for_display, caption="Imagem carregada para análise", use_container_width=True)

# Inicialização do histórico de mensagens no estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibição do histórico na interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"]:
            st.image(message["image"], width=250)

# Entrada de Mensagem e Processamento (Texto e Imagem)
if prompt := st.chat_input("Digite sua dúvida operacional ou comando de inspeção..."):
    
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
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_res, 
                    "image": None
                })
            
            except Exception as e:
                st.error(f"Ocorreu um erro técnico ao processar a solicitação: {e}")