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

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Erro ao carregar a chave GEMINI_API_KEY.")
    st.stop()

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
# CABEÇALHO
# ==========================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(
        "logo_brigada.png",
        width=280
    )

st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0px;'>
        IA BRIGADA
    </h1>

    <p style='text-align:center;
              color:#6b7280;
              font-size:18px;
              margin-top:0px;'>
        Assistente Virtual para Bombeiros Civis
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background:#0f172a;
        color:white;
        text-align:center;
        padding:12px;
        border-radius:10px;
        font-weight:bold;
        margin-bottom:15px;
    ">
        🚒 Operações • Inspeções • Emergências • Suporte Técnico
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("### Central de Inspeção")

    st.write(
        "Envie imagens de estruturas, equipamentos ou instalações para análise técnica."
    )

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
# HISTÓRICO DE CONVERSA
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# EXIBIÇÃO DO HISTÓRICO
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("image") is not None:

            st.image(
                message["image"],
                width=250
            )

# ==========================================
# ENTRADA DO USUÁRIO
# ==========================================

prompt = st.chat_input(
    "Digite sua dúvida operacional ou solicitação de inspeção..."
)

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

            st.image(
                current_image,
                width=250
            )

    with st.chat_message("assistant"):

        with st.spinner("Processando análise técnica..."):

            try:

                if current_image:

                    response = model.generate_content(
                        [
                            prompt,
                            current_image
                        ]
                    )

                else:

                    history = []

                    for msg in st.session_state.messages[:-1]:

                        role = (
                            "user"
                            if msg["role"] == "user"
                            else "model"
                        )

                        history.append(
                            {
                                "role": role,
                                "parts": [msg["content"]]
                            }
                        )

                    chat = model.start_chat(
                        history=history
                    )

                    response = chat.send_message(
                        prompt
                    )

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

                st.error(
                    f"Erro ao processar a solicitação: {e}"
                )