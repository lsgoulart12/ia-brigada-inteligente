from datetime import datetime
from PIL import Image
import google.generativeai as genai
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

# Configuração da chave API (compatível com as novas chaves)
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

  # Formulário limpo com upload discreto
  with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
      uploaded_file = st.file_uploader(
          "📎", type=["jpg", "png", "jpeg"], label_visibility="collapsed"
      )
    with col2:
      st.write("Anexar foto da ocorrência (opcional)")

    pergunta = st.text_area("Digite sua dúvida técnica:", height=80)
    enviar = st.form_submit_button("Enviar Pergunta")

  if enviar:
    if pergunta.strip():
      with st.spinner("Analisando ocorrência..."):
        try:
          # Instrução para ser estritamente objetivo e focado na pergunta
          instrucao_sistema = (
              "Você é um assistente técnico sênior para bombeiros civis e brigadistas. "
              "REGRAS DE RESPOSTA:\n"
              "1. Seja direto, conciso e estritamente objetivo.\n"
              "2. Responda APENAS o que foi perguntado, sem adicionar informações não solicitadas.\n"
              "3. Se a pergunta for sobre balões ou jargão, utilize o termo 'Pássaro de Fogo' e cite a Lei 9.605/98 Art. 42. "
              "Se a pergunta for sobre outro assunto (como EPI), foque exclusivamente nele sem misturar leis de balões."
          )

          model = genai.GenerativeModel("gemini-1.5-flash")

          if uploaded_file is not None:
            imagem = Image.open(uploaded_file)
            response = model.generate_content([instrucao_sistema, imagem, pergunta])
          else:
            response = model.generate_content(
                f"{instrucao_sistema} | Pergunta: {pergunta}"
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