from datetime import datetime
from PIL import Image
from google import genai
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

try:
  API_KEY = st.secrets["GEMINI_API_KEY"].strip()
  client = genai.Client(api_key=API_KEY)
except Exception:
  pass

# --- INTERFACE LIMPA ---
st.image("logo_brigada.png.png", width=120)
st.title("IA BRIGADA")
st.subheader("Assistente Técnico Especializado - Brigada de Incêndio")

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

  with st.form("chat_form", clear_on_submit=True):
    uploaded_file = st.file_uploader(
        "Anexar foto da ocorrência (opcional)", type=["jpg", "png", "jpeg"]
    )
    pergunta = st.text_area("Digite sua dúvida técnica:", height=80)
    enviar = st.form_submit_button("Enviar Pergunta")

  if enviar:
    if pergunta.strip():
      with st.spinner("Analisando ocorrência..."):
        try:
          contexto_brigada = (
              "Você é um assistente técnico sênior para bombeiros civis e"
              " brigadistas. Jargão operacional obrigatório: 'Pássaro de Fogo'"
              " refere-se a balões. Base legal obrigatória: Lei de Crimes"
              " Ambientais (Lei nº 9.605/98, Art. 42), com pena de detenção de"
              " 1 a 3 anos ou multa, ou ambas. Tratativa de fiança: Explicite"
              " que pode ser arbitrada pela autoridade policial em casos de"
              " menor potencial, mas elevada ou mantida em prisão preventiva em"
              " casos de incêndio severo ou risco."
          )

          contents = [contexto_brigada]
          if uploaded_file is not None:
            contents.append(Image.open(uploaded_file))
          contents.append(pergunta)

          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=contents
          )

          st.write("**Resposta Técnica:**")
          st.write(response.text)

        except Exception as e:
          st.error(f"Erro na comunicação com a API: {e}")
    else:
      st.warning("Por favor, digite uma pergunta antes de enviar.")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()