from PIL import Image
import datetime
import google.generativeai as genai
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

# Configuração da chave API
try:
  API_KEY = st.secrets["GEMINI_API_KEY"].strip()
  genai.configure(api_key=API_KEY)
except Exception:
  pass

# --- INTERFACE LIMPA (Sem o triângulo) ---
st.image("logo_brigada.png.png", width=120)
st.title("IA BRIGADA")
st.subheader("Assistente virtual")

if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
  usuario = st.selectbox("Usuário:", ["b1 (Bombeiro1)", "b2 (Bombeiro2)","b3 (Bombeiro3)"])
  senha = st.text_input("Senha:", type="password")
  if st.button("Entrar"):
    if senha in ["senha1", "senha2","senha3"]:
      st.session_state["autenticado"] = True
      st.session_state["usuario"] = usuario.split(" ")[0]
      st.rerun()
    else:
      st.error("Senha incorreta.")
else:
  username = st.session_state["usuario"]
  st.success(f"Bem-vindo, {username}!")

  # Formulário limpo com upload discreto (estilo clipe/arquivo leve)
  with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
      # Ícone/botão discreto para anexo
      uploaded_file = st.file_uploader(
          "📎", type=["jpg", "png", "jpeg"], label_visibility="collapsed"
      )
    with col2:
      pergunta = st.text_area("Digite sua dúvida técnica:", height=80)
st.write("Anexar foto da ocorrência (opcional)")
enviar = st.form_submit_button("Enviar Pergunta")

  if enviar:
    if pergunta.strip():
      with st.spinner("Analisando ocorrência..."):
        try:
          # Contexto fixo da brigada (Jargão e Lei preservados)
          contexto_brigada = (
              "Você é um assistente técnico sênior para bombeiros civis e brigadistas. "
              "Jargão operacional obrigatório: 'Pássaro de Fogo' refere-se a balões. "
              "Base legal obrigatória: Lei de Crimes Ambientais (Lei nº 9.605/98, Art. 42), "
              "com pena de detenção de 1 a 3 anos ou multa, ou ambas. "
              "Tratativa de fiança: Explicite que pode ser arbitrada pela autoridade policial em casos "
              "de menor potencial, mas elevada ou mantida em prisão preventiva em casos de incêndio severo ou risco."
          )

          model = genai.GenerativeModel("gemini-1.5-flash")

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
          st.error(
              "Erro 401: A chave atual não é compatível com o Gemini. Por"
              " favor, gere uma chave nova no Google AI Studio que comece com"
              " 'AIzaSy'."
          )
    else:
      st.warning("Por favor, digite uma pergunta antes de enviar.")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()