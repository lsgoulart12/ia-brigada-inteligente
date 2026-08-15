from datetime import datetime
from PIL import Image
import google.generativeai as genai
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

# Configuração segura da API
try:
  API_KEY = st.secrets["GEMINI_API_KEY"].strip()
  genai.configure(api_key=API_KEY)
except Exception:
  pass

# --- INTERFACE COM FONTES AJUSTADAS ---
st.image("logo_brigada.png.png", width=120)

# IA BRIGADA com o tamanho igual ao subheader antigo
st.markdown(
    "<h3 style='margin-bottom: 0px;'>IA BRIGADA</h3>", unsafe_allow_html=True
)

# Assistente Virtual com o tamanho menor, ajustado
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

  # Formulário organizado: Pergunta em cima, upload embaixo
  with st.form("chat_form", clear_on_submit=True):
    pergunta = st.text_area("Digite sua dúvida ou descrição dos fatos:", height=90)
    uploaded_file = st.file_uploader(
        "Anexar foto da ocorrência (opcional)", type=["jpg", "png", "jpeg"]
    )
    enviar = st.form_submit_button("Enviar Pergunta")

  if enviar:
    if pergunta.strip():
      with st.spinner("Analisando ocorrência..."):
        try:
          contexto_brigada = (
              "Você é um assistente técnico sênior para bombeiros civis e brigadistas. "
              "Se a pergunta for sobre balões ou soltar balões, utilize obrigatoriamente o jargão "
              "'Pássaro de Fogo' e cite a Lei de Crimes Ambientais (Lei nº 9.605/98, Art. 42), "
              "com pena de detenção de 1 a 3 anos ou multa, além de orientar sobre a fiança policial. "
              "Se a pergunta for sobre outros temas técnicos (como EPI, resgate, etc.), seja direto e responda "
              "estritamente ao assunto solicitado, sem misturar informações desnecessárias."
          )

          model = genai.GenerativeModel("gemini-2.5-flash")

          if uploaded_file is not None:
            imagem = Image.open(uploaded_file)
            response = model.generate_content([contexto_brigada, imagem, pergunta])
          else:
            response = model.generate_content(
                f"{contexto_brigada} | Pergunta: {pergunta}"
            )

          st.write("**Resposta Técnica:**")
          st.write(response.text)

        except Exception as e:
          st.error(f"Erro na comunicação com a API: {e}")
    else:
      st.warning("Por favor, digite a descrição ou dúvida antes de enviar.")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()