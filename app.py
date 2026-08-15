from datetime import datetime
from PIL import Image
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
          # Contexto focado em objetividade e precisão técnica
          instrucao_sistema = (
              "Você é um assistente técnico sênior para bombeiros civis e brigadistas. "
              "REGRAS DE RESPOSTA:\n"
              "1. Seja direto, conciso e estritamente objetivo.\n"
              "2. Responda APENAS o que foi perguntado, sem adicionar informações ou leis não solicitadas.\n"
              "3. Se a pergunta for sobre balões ou soltar balões, utilize estritamente o jargão 'Pássaro de Fogo' "
              "e cite a Lei de Crimes Ambientais (Lei nº 9.605/98, Art. 42), com pena de 1 a 3 anos ou multa. "
              "Se a pergunta for sobre outro tema (como EPI, resgate, etc.), foque exclusivamente no assunto perguntado."
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
          st.error(
              f"Erro na comunicação com a API: {e}. Verifique sua chave nos"
              " Secrets."
          )
    else:
      st.warning("Por favor, digite uma pergunta antes de enviar.")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()