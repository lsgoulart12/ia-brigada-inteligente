from datetime import datetime
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

# Configuração segura das APIs e Supabase
try:
    API_KEY = st.secrets["GEMINI_API_KEY"].strip()
    genai.configure(api_key=API_KEY)

    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    pass

# --- INTERFACE COM FONTES AJUSTADAS ---
st.image("logo_brigada.png.png", width=120)

st.markdown(
    "<h3 style='margin-bottom: 0px;'>IA BRIGADA</h3>", unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size: 1.1rem; color: #c0c0c0; font-weight: 600;"
    " margin-top: 0px;'>Assistente Virtual</p>",
    unsafe_allow_html=True,
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    usuario = st.selectbox("Usuário:", ["b1 (Bombeiro1)", "b2 (Bombeiro2)"])
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha in ["senha1", "senha2"]:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario.split(" ")[0]
            st.rerun()
        else:
            st.error("Senha incorreta.")
else:
    username = st.session_state["usuario"]
    st.success(f"Bem-vindo, {username}!")

    # Inicializa o histórico se não existir
    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    # Exibe o histórico de conversas anteriores na tela
    for item in st.session_state["historico"]:
        with st.chat_message(item["role"]):
            st.write(item["content"])

    # Formulário organizado: Pergunta em cima, upload embaixo
    with st.form("chat_form", clear_on_submit=True):
        pergunta = st.text_area("Digite sua dúvida ou descrição dos fatos:", height=90)
        uploaded_file = st.file_uploader(
            "Anexar foto da ocorrência (opcional)", type=["jpg", "png", "jpeg"]
        )
        enviar = st.form_submit_button("Enviar Pergunta")

    if enviar and pergunta.strip():
        # Salva e exibe a pergunta do usuário no histórico
        st.session_state["historico"].append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.write(pergunta)

        with st.spinner("Analisando ocorrência..."):
            try:
                contexto_brigada = (
                    "Você é um colega de equipe experiente e prestativo para bombeiros civis. "
                    "REGRAS DE OURO:\n"
                    "1. Nunca comece com frases robóticas como 'Como assistente técnico...' ou 'Esclareço que...'. Vá direto ao ponto.\n"
                    "2. Seja extremamente objetivo, humano e natural. Use poucas palavras.\n"
                    "3. Se o assunto for balões, chame de 'Pássaro de Fogo', diga que é crime pela Lei 9.605/98 (Art. 42) "
                    "com pena de 1 a 3 anos, e seja breve.\n"
                    "4. Se for sobre outros assuntos (como EPI), defina o item de forma curta e direta, sem misturar leis de balões."
                )

                model = genai.GenerativeModel("gemini-2.5-flash")

                if uploaded_file is not None:
                    imagem = Image.open(uploaded_file)
                    response = model.generate_content([contexto_brigada, imagem, pergunta])
                else:
                    response = model.generate_content(
                        f"{contexto_brigada} | Pergunta: {pergunta}"
                    )

                resposta_texto = response.text

                # Salva e exibe a resposta da IA no histórico
                st.session_state["historico"].append(
                    {"role": "assistant", "content": resposta_texto}
                )
                with st.chat_message("assistant"):
                    st.write(resposta_texto)

                # Grava os dados diretamente no Supabase na tabela correta
               # Grava os dados diretamente no Supabase na tabela correta
                try:
                    print("TENTANDO SALVAR NO SUPABASE...")
                    supabase.table("interacoes").insert({
                        "usuario": username,
                        "pergunta": pergunta,
                        "resposta": resposta_texto,
                        "data": datetime.now().isoformat(),
                    }, returning="minimal").execute()
                    print("SALVOU COM SUCESSO!")
                except Exception as db_err:
                    print(f"ERRO EXATO DO BANCO: {db_err}")

            except Exception as e:
                st.error(f"Erro na comunicação com a API: {e}")
    elif enviar:
        st.warning("Por favor, digite a descrição ou dúvida antes de enviar.")

    if st.button("Sair"):
        st.session_state["autenticado"] = False
        st.session_state["historico"] = []
        st.rerun()