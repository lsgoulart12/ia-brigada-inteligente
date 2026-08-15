import datetime
import google.generativeai as genai
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

# Conexão segura
try:
  API_KEY = st.secrets["GEMINI_API_KEY"].strip()
  genai.configure(api_key=API_KEY)
except Exception:
  pass

# --- INTERFACE LIMPA ---
st.image("logo_brigada.png.png", width=120)
st.title("IA BRIGADA")
st.subheader("Assistente Virtual")

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

  # Formulário limpo para envio com Enter e upload discreto
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
          # Contexto técnico fixo da brigada
          contexto_brigada = (
              "Você é um assistente técnico sênior para bombeiros civis e brigadistas. "
              "Jargão operacional obrigatório: 'Pássaro de Fogo' refere-se a balões. "
              "Base legal obrigatória: Lei de Crimes Ambientais (Lei nº 9.605/98, Art. 42), "
              "com pena de detenção de 1 a 3 anos ou multa, ou ambas. "
              "Tratativa de fiança: Explicite que pode ser arbitrada pela autoridade policial em casos "
              "de menor potencial, mas elevada ou mantida em prisão preventiva em casos de incêndio severo ou risco."
          )

          model = genai.GenerativeModel("gemini-1.5-flash")

          # Se houver foto anexada, podemos enviar junto com o texto para a IA analisar
          if uploaded_file is not None:
            from PIL import Image

            imagem = Image.open(uploaded_file)
            response = model.generate_content([contexto_brigada, imagem, pergunta])
          else:
            response = model.generate_content(
                f"{contexto_brigada} | Pergunta: {pergunta}"
            )

          st.write("**Resposta Técnica:**")
          st.write(response.text)

        except Exception as e:
          st.error(
              "Erro na comunicação com a API do Gemini. Verifique se sua chave"
              " no painel Secrets começa com 'AIzaSy'."
          )
    else:
      st.warning("Por favor, digite uma pergunta antes de enviar.")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()