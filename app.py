import base64
import traceback
from datetime import datetime
from pathlib import Path
from PIL import Image
import pandas as pd
from google import genai
import gspread
import streamlit as st

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

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

PLANILHA_URL = "https://docs.google.com/spreadsheets/d/1QC59C1cB8WXZKrY4RVJxH5ZS5Ju4_RDcTdR64VA7SQg/edit?gid=0#gid=0"


@st.cache_resource(show_spinner=False)
def conectar_google_sheets():
    """Autentica no Google Sheets usando os segredos do Streamlit."""
    credenciais = dict(st.secrets["gspread"])
    if "\\n" in credenciais.get("private_key", ""):
        credenciais["private_key"] = credenciais["private_key"].replace("\\n", "\n")
    return gspread.service_account_from_dict(credenciais)


def responder_gemini_rest(prompt_texto: str, historico=None):
    """Envia um prompt ao Gemini usando a biblioteca oficial atualizada."""
    try:
        mensagens = []
        for item in historico or []:
            if item["role"] in ["user", "assistant"]:
                mensagens.append(
                    {
                        "role": "model" if item["role"] == "assistant" else "user",
                        "parts": [{"text": item["content"]}],
                    }
                )
        mensagens.append({"role": "user", "parts": [{"text": prompt_texto}]})
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=mensagens,
        )
        return response.text
    except Exception as err:
        print(f"Erro detalhado do Gemini: {err}", flush=True)
        traceback.print_exc()
        st.error(f"Erro detalhado do Gemini: {err}")
        return None



try:
    cliente_google_sheets = conectar_google_sheets()
    planilha = cliente_google_sheets.open_by_url(PLANILHA_URL).sheet1
except Exception as config_err:
    planilha = None
    print(f"Erro ao conectar ao Google Sheets: {config_err}", flush=True)
    traceback.print_exc()


def salvar_interacao(usuario: str, pergunta: str, resposta: str) -> bool:
    """Adiciona uma interação à planilha e mantém o chat funcionando se falhar."""
    if planilha is None:
        st.warning("O histórico não foi salvo. Tente novamente mais tarde.")
        return False

    try:
        planilha.append_row([usuario, pergunta, resposta, str(datetime.now())])
        return True
    except Exception as sheet_err:
        print(f"Erro ao salvar interação no Google Sheets: {sheet_err}")
        st.error("A resposta foi gerada, mas não foi possível salvar o histórico.")
        return False


def cadastrar_extintor(usuario: str, local: str, tipo: str, identificacao: str, validade) -> bool:
    """Registra um extintor nas colunas reservadas da planilha."""
    if planilha is None:
        st.error("Não foi possível acessar a planilha para cadastrar o extintor.")
        return False

    try:
        planilha.append_row(
            ["", "", "", "", usuario, local, tipo, identificacao, validade.isoformat()]
        )
        carregar_extintores.clear()
        st.success("Extintor cadastrado com sucesso.")
        return True
    except Exception as extinguisher_err:
        print(f"Erro ao cadastrar extintor: {extinguisher_err}", flush=True)
        st.error("Não foi possível cadastrar o extintor.")
        return False


@st.cache_data(ttl=60, show_spinner=False)
def carregar_extintores() -> pd.DataFrame:
    """Carrega os extintores registrados nas colunas reservadas da planilha."""
    colunas = ["usuario", "local", "tipo", "identificacao", "validade"]
    if planilha is None:
        return pd.DataFrame(columns=colunas)

    try:
        registros = planilha.get_all_values()
    except Exception as sheet_err:
        print(f"Erro ao ler extintores: {sheet_err}", flush=True)
        return pd.DataFrame(columns=colunas)

    if not registros:
        return pd.DataFrame(columns=colunas)

    extintores = []
    linhas_planilha = []
    for numero_linha, registro in enumerate(registros, start=1):
        campos_extintor = registro[4:9] if len(registro) >= 9 else []
        if len(campos_extintor) == 5 and all(str(valor).strip() for valor in campos_extintor):
            extintores.append(campos_extintor)
            linhas_planilha.append(numero_linha)

    if not extintores:
        return pd.DataFrame(columns=colunas)

    return pd.DataFrame(extintores, columns=colunas, index=linhas_planilha)


def excluir_extintor(linha_planilha: int) -> bool:
    """Exclui o extintor correspondente à linha original da planilha."""
    if planilha is None:
        st.error("Não foi possível acessar a planilha para excluir o extintor.")
        return False

    try:
        planilha.delete_rows(linha_planilha)
        carregar_extintores.clear()
        return True
    except Exception as extinguisher_err:
        print(f"Erro ao excluir extintor: {extinguisher_err}", flush=True)
        st.error("Não foi possível excluir o extintor.")
        return False


def render_alerta_extintores() -> None:
    """Destaca extintores vencidos ou com validade nos próximos 15 dias."""
    extintores = carregar_extintores()
    if extintores.empty:
        return

    extintores = extintores.copy()
    extintores["validade"] = pd.to_datetime(extintores["validade"], errors="coerce")
    limite = pd.to_datetime(datetime.now() + pd.Timedelta(days=15))
    alerta = extintores[extintores["validade"].notna() & (extintores["validade"] <= limite)]
    if alerta.empty:
        return

    st.markdown(
        "<div style='color:#b42318;font-weight:700;'>Atenção: extintores vencidos ou com validade em até 15 dias.</div>",
        unsafe_allow_html=True,
    )
    cabecalho = st.columns([1, 2, 2, 2, 1])
    for coluna, titulo in zip(cabecalho, ["Usuário", "Local", "Tipo", "Identificação", "Ação"]):
        coluna.markdown(f"**{titulo}**")

    for _, extintor in alerta.iterrows():
        colunas = st.columns([1, 2, 2, 2, 1])
        colunas[0].markdown(f":red[{extintor['usuario']}]")
        colunas[1].markdown(f":red[{extintor['local']}]")
        colunas[2].markdown(f":red[{extintor['tipo']}]")
        colunas[3].markdown(f":red[{extintor['identificacao']}] - {extintor['validade']}")
        if colunas[4].button("Excluir", key=f"excluir_extintor_{extintor.name}"):
            if excluir_extintor(int(extintor.name)):
                st.rerun()


@st.cache_data(ttl=60, show_spinner=False)
def carregar_historico_analitico() -> pd.DataFrame:
    """Carrega os registros da planilha para os indicadores analíticos."""
    if planilha is None:
        return pd.DataFrame(columns=["usuario", "pergunta", "resposta", "data_hora"])

    registros = planilha.get_all_values()
    if not registros:
        return pd.DataFrame(columns=["usuario", "pergunta", "resposta", "data_hora"])

    historico = pd.DataFrame(registros)
    historico = historico.iloc[:, :4]
    historico.columns = ["usuario", "pergunta", "resposta", "data_hora"]
    return historico[historico["pergunta"].astype(str).str.strip().ne("")]


def classificar_categoria(pergunta: str) -> str:
    """Agrupa perguntas por tema operacional."""
    texto = str(pergunta).lower()
    categorias = {
        "Extintores": ["extintor", "classe de fogo", "agente extintor"],
        "EPI": ["epi", "capacete", "luva", "botina", "equipamento de proteção"],
        "Primeiros socorros": ["primeiros socorros", "desmaio", "ferimento", "queimadura"],
        "Incêndios": ["incêndio", "incendio", "fogo", "fumaça", "fumaca"],
        "Procedimentos": ["procedimento", "evacuação", "evacuacao", "emergência", "emergencia"],
    }
    for categoria, termos in categorias.items():
        if any(termo in texto for termo in termos):
            return categoria
    return "Outros"


def classificar_tipo_duvida(pergunta: str) -> str:
    """Separa orientação direta de confirmação de procedimento executado."""
    texto = str(pergunta).lower()
    termos_validacao = [
        "fiz",
        "realizei",
        "executei",
        "confirma",
        "está correto",
        "esta correto",
        "procedi",
        "deu certo",
    ]
    if any(termo in texto for termo in termos_validacao):
        return "Confirmação de procedimento"
    return "Orientação direta"


def render_dashboard_analitico() -> None:
    """Exibe os indicadores derivados do histórico do Google Sheets."""
    historico = carregar_historico_analitico()
    if historico.empty:
        st.info("Ainda não há registros para análise.")
        return

    historico["categoria"] = historico["pergunta"].map(classificar_categoria)
    historico["tipo_duvida"] = historico["pergunta"].map(classificar_tipo_duvida)

    st.subheader("Dashboard analítico")
    categorias = historico["categoria"].value_counts().rename("Quantidade")
    st.bar_chart(categorias)

    tipos_duvida = historico["tipo_duvida"].value_counts().rename("Quantidade")
    st.bar_chart(tipos_duvida)

# --- IDENTIDADE VISUAL PERSISTENTE ---
render_brand_header()

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    with st.form("login_form", clear_on_submit=False):
        usuario = st.selectbox(
            "Usuário:",
            [
                "b1 (Bombeiro1)",
                "b2 (Bombeiro2)",
                "b3 (Bombeiro3)",
                "b4 (Bombeiro4)",
                "b5 (Bombeiro5)",
                "b6 (Bombeiro6)",
                "administrador",
            ],
        )
        senha = st.text_input("Senha:", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        acesso_valido = (
            senha == "8920"
            if usuario == "administrador"
            else senha == usuario.split(" ")[0]
        )
        if acesso_valido:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario.split(" ")[0]
            st.session_state["administrador_autorizado"] = False
            st.rerun()
        else:
            st.error("Senha incorreta.")
else:
    username = st.session_state["usuario"]
    st.caption(f"Conectado como {username}")
    if username == "administrador":
        administrador = st.session_state.get("administrador_autorizado", False)
        if not administrador:
            senha_administrador = st.sidebar.text_input(
                "Senha administrativa",
                type="password",
            )
            if senha_administrador == "8920":
                st.session_state["administrador_autorizado"] = True
                administrador = True
    else:
        st.session_state["administrador_autorizado"] = False
        administrador = False

    # Inicializa o histórico se não existir
    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    # Exibe o histórico de conversas anteriores na tela
    for item in st.session_state["historico"]:
        avatar = str(LOGO_PATH) if item["role"] == "assistant" else None
        with st.chat_message(item["role"], avatar=avatar):
            st.write(item["content"])

    modo_cadastro = st.toggle("Cadastro rápido de extintor")
    if modo_cadastro:
        with st.form("cadastro_extintor_form", clear_on_submit=True):
            local_extintor = st.text_input("Local ou estúdio")
            tipo_extintor = st.selectbox(
                "Tipo de extintor",
                [
                    "Água Pressurizada (AP)",
                    "Pó Químico Seco BC (PQS BC)",
                    "Pó Químico ABC (PQS ABC)",
                    "Dióxido de Carbono (CO2)",
                    "Espuma Mecânica",
                    "Acetato de Potássio (Classe K / Cozinhas)",
                    "Pó Especial (para Classes D / Metais Combustíveis)",
                ],
            )
            identificacao_extintor = st.text_input("Número de identificação")
            validade_extintor = st.date_input("Data de validade")
            cadastrar = st.form_submit_button("Cadastrar extintor")

        if cadastrar:
            campos_preenchidos = all(
                [local_extintor.strip(), tipo_extintor, identificacao_extintor.strip()]
            )
            if not campos_preenchidos:
                st.error("Preencha todos os campos do extintor.")
            else:
                cadastrar_extintor(
                    username,
                    local_extintor.strip(),
                    tipo_extintor,
                    identificacao_extintor.strip(),
                    validade_extintor,
                )
        entrada = None
    else:
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
                    "4. Se for sobre outros assuntos (como EPI), defina o item de forma curta e direta, sem misturar leis de balões.\n"
                    "5. Use obrigatoriamente o histórico da conversa para interpretar perguntas de seguimento e manter o contexto do equipamento ou ocorrência mencionada. Nunca responda de forma genérica quando o histórico definir o cenário.\n"
                    "6. Em incêndio envolvendo equipamento elétrico, se o aparelho não foi desenergizado, indique obrigatoriamente extintor de CO2 ou PQS. Se foi desenergizado, retirado da tomada, pode indicar Água Pressurizada (AP), CO2 ou PQS.\n"
                    "7. Informe somente o procedimento técnico necessário, sem repetir instruções óbvias como girar o pino ou romper o lacre, salvo se forem estritamente necessárias.\n"
                )

                if uploaded_file is not None:
                    imagem = Image.open(uploaded_file)
                    resposta_texto = responder_gemini_rest(
                        f"{contexto_brigada} | Pergunta: {pergunta}",
                        st.session_state["historico"][:-1],
                    )
                else:
                    resposta_texto = responder_gemini_rest(
                        f"{contexto_brigada} | Pergunta: {pergunta}",
                        st.session_state["historico"][:-1],
                    )

                if resposta_texto is None:
                    st.stop()

                salvar_interacao(
                    usuario=username,
                    pergunta=pergunta,
                    resposta=resposta_texto,
                )

                # Salva e exibe a resposta da IA no histórico
                st.session_state["historico"].append(
                    {"role": "assistant", "content": resposta_texto}
                )
                with st.chat_message("assistant", avatar=str(LOGO_PATH)):
                    st.write(resposta_texto)
            except Exception as e:
                print(f"Erro ao processar pergunta: {e}", flush=True)
                traceback.print_exc()
                st.error("Não foi possível processar sua pergunta. Tente novamente.")

    if administrador:
        render_dashboard_analitico()
        render_alerta_extintores()
