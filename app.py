import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuração da página do Streamlit
st.set_page_config(
    page_title="IA Brigada",
    page_icon="logo_brigada.png", 
    layout="centered"
)

# Configuração da chave de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Erro ao configurar a chave de API nos segredos do Streamlit.")

# Configuração do modelo
generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

system_instruction = """
Você é a IA BRIGADA, uma assistente virtual especializada, técnica e parceira para Bombeiros Civis.
Seu tom de voz deve ser profissional, direto e amigável.
Dê a resposta técnica imediata na primeira frase e depois complemente com os detalhes operacionais.
- Termo "Pássaro de fogo": Refere-se a balões (crime ambiental, Art. 42 da Lei 9.605/98).
- Análise de Imagem: Avalie fotos de campo (longarinas, equipamentos) em busca de inconformidades.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# --- BARRA LATERAL ---
with st.sidebar:
    try:
        logo = Image.open("logo_brigada.png")
        st.image(logo, use_container_width=True)
    except:
        st.subheader("IA BRIGADA")
    
    st.markdown("---")
    st.markdown("### 📸 Central de Inspeção")
    uploaded_file = st.file_uploader("Carregar foto de campo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img_for_display = Image.open(uploaded_file)
        st.image(img_for_display, caption="Pronta para análise", use_container_width=True)

# Cabeçalho Principal
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo_brigada.png", width=80)
    except:
        pass
with col2:
    st.markdown("## IA Brigada: Assistente Virtual")
    st.caption("Pronta para a missão. Como posso te ajudar hoje?")

# Histórico de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"]:
            st.image(message["image"], width=250)

# Entrada de Mensagem e Resposta
if prompt := st.chat_input("Digite sua dúvida ou comando..."):
    current_img = Image.open(uploaded_file) if uploaded_file else None
    
    st.session_state.messages.append({"role": "user", "content": prompt, "image": current_img})
    with st.chat_message("user"):
        st.markdown(prompt)
        if current_img:
            st.image(current_img, width=250)

    with st.chat_message("assistant"):
        with st.spinner("Analisando com atenção..."):
            try:
                if current_img:
                    response = model.generate_content([prompt, current_img])
                else:
                    chat = model.start_chat(history=[
                        {"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} 
                        for m in st.session_state.messages[:-1]
                    ])
                    response = chat.send_message(prompt)
                
                full_res = response.text
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            except Exception as e:
                # Tratamento de erro seguro para o usuário final
                st.error("Desculpe, ocorreu uma instabilidade temporária ao processar sua solicitação. Por favor, tente novamente em instantes.")