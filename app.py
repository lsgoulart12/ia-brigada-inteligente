import base64
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

LOGO_PATH = Path(__file__).with_name("logo_brigada.png.png")


def render_brand_header() -> None:
    """Mantém a marca visível enquanto o histórico do chat é rolado."""
    try:
        logo_base64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    except OSError:
        logo_base64 = ""

    st.markdown(
        f"""
        <div class="brand-header">
            <div class="brand-logo-frame">
                <img src="data:image/png;base64,{logo_base64}" alt="Tetraedro do fogo">
            </div>
            <div>
                <div class="brand-title">IA BRIGADA</div>
                <div class="brand-subtitle">Assistente Virtual</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
        :root {
            --brand-red: #e85d3f;
            --brand-ink: #17212b;
            --brand-muted: #66727d;
            --brand-line: #e7ebee;
        }

        [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: transparent;
        }

        .block-container {
            max-width: 780px;
            padding-top: 0.5rem;
            padding-bottom: 5.5rem;
        }

        .brand-header {
            align-items: center;
            background: var(--background-color);
            border-bottom: 1px solid var(--brand-line);
            display: flex;
            gap: 0.8rem;
            padding: 0.65rem 0 0.7rem;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .brand-logo-frame {
            align-items: center;
            background: var(--secondary-background-color);
            border: 1px solid #f0c1b5;
            border-radius: 14px;
            box-shadow: 0 5px 16px rgba(232, 93, 63, 0.18), 0 1px 3px rgba(23, 33, 43, 0.12);
            display: flex;
            height: 48px;
            justify-content: center;
            overflow: hidden;
            width: 48px;
        }

        .brand-logo-frame img {
            display: block;
            height: 100%;
            object-fit: contain;
            padding: 4px;
            width: 100%;
        }

        .brand-title {
            color: var(--text-color);
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            line-height: 1.1;
        }

        .brand-subtitle {
            color: var(--brand-muted);
            font-size: 0.82rem;
            margin-top: 0.2rem;
        }

        [data-testid="stChatMessage"] {
            padding-bottom: 0.35rem;
            padding-top: 0.35rem;
        }

        [data-testid="stFileUploader"] section {
            align-items: center;
            background: transparent;
            border: 0;
            display: flex;
            min-height: 0;
            padding: 0;
        }

        [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none;
        }

        [data-testid="stFileUploader"] button {
            border: 1px solid #d7dee3;
            border-radius: 8px;
            color: var(--brand-muted);
            font-size: 0.78rem;
            min-height: 1.9rem;
            padding: 0.1rem 0.65rem;
        }

        [data-testid="stFileUploader"] small {
            display: none;
        }

        [data-testid="stTextArea"] textarea {
            min-height: 74px;
        }

        [data-testid="stChatInput"] {
            padding-top: 0.35rem;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# Configuração segura das APIs e Supabase
try:
    API_KEY = st.secrets["GEMINI_API_KEY"].strip()
    genai.configure(api_key=API_KEY)

    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Diagnóstico visual das credenciais carregadas pelo Streamlit.
    st.write(f"URL do Supabase: {SUPABASE_URL}")
    st.write(
        "Chave do Supabase: Carregada com sucesso"
        if SUPABASE_KEY
        else "Chave não encontrada!"
    )
except Exception as config_err:
    API_KEY = None
    supabase = None
    st.warning(f"Configuração indisponível: {config_err}")


def salvar_interacao(usuario: str, pergunta: str, resposta: str) -> bool:
    """Insere uma interação e mantém o chat funcionando se o banco falhar."""
    if supabase is None:
        st.warning("O histórico não foi salvo: o Supabase não está configurado.")
        return False

    registro = [
        {
            "usuario": str(usuario).strip(),
            "pergunta": str(pergunta).strip(),
            "resposta": str(resposta).strip(),
        }
    ]

    try:
        supabase.table("historico_chat").insert(registro).execute()
        return True
    except Exception as db_err:
        erro = getattr(db_err, "message", None) or str(db_err)
        codigo = getattr(db_err, "code", None)
        detalhes = getattr(db_err, "details", None)
        dica = getattr(db_err, "hint", None)
        diagnostico = " | ".join(
            parte
            for parte in (
                f"código={codigo}" if codigo else "",
                erro,
                f"detalhes={detalhes}" if detalhes else "",
                f"dica={dica}" if dica else "",
            )
            if parte
        )
        print(f"Erro ao salvar interação no Supabase: {diagnostico}")
        st.error(
            "A resposta foi gerada, mas o histórico não foi salvo. "
            f"Detalhes: {diagnostico}"
        )
        return False

# --- IDENTIDADE VISUAL PERSISTENTE ---
render_brand_header()

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    with st.form("login_form", clear_on_submit=False):
        usuario = st.selectbox("Usuário:", ["b1 (Bombeiro1)", "b2 (Bombeiro2)"])
        senha = st.text_input("Senha:", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        if senha in ["senha1", "senha2"]:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario.split(" ")[0]
            st.rerun()
        else:
            st.error("Senha incorreta.")
else:
    username = st.session_state["usuario"]
    st.caption(f"Conectado como {username}")

    # Inicializa o histórico se não existir
    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    # Exibe o histórico de conversas anteriores na tela
    for item in st.session_state["historico"]:
        avatar = str(LOGO_PATH) if item["role"] == "assistant" else None
        with st.chat_message(item["role"], avatar=avatar):
            st.write(item["content"])

    entrada = st.chat_input(
        "Digite sua dúvida ou descrição dos fatos...",
        accept_file=True,
        file_type=["jpg", "png", "jpeg"],
    )
    pergunta = entrada.text if entrada is not None else ""
    uploaded_file = entrada.files[0] if entrada is not None and entrada.files else None
    enviar = entrada is not None

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
                    "5. Sempre que explicar o uso de extintores, inclua obrigatoriamente: girar o pino (rompendo o lacre), dar um jato de teste para verificar a pressão, e direcionar para a base do fogo Varra o jato de um lado para o outro na base do fogo.\n"
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
                with st.chat_message("assistant", avatar=str(LOGO_PATH)):
                    st.write(resposta_texto)

                salvar_interacao(
                    usuario=username,
                    pergunta=pergunta,
                    resposta=resposta_texto,
                )
            except Exception as e:
                st.error(f"Erro ao processar a pergunta: {e}")
