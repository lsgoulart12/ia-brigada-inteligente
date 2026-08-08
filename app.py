import datetime
import google.generativeai as genai
import pandas as pd
from supabase import Client, create_client
import streamlit as st

# --- CONFIGURAÇÃO DE SEGURANÇA E CONEXÃO ---
try:
  API_KEY = st.secrets["GEMINI_API_KEY"].strip()
  URL = st.secrets["SUPABASE_URL"].strip()
  KEY = st.secrets["SUPABASE_KEY"].strip()

  genai.configure(api_key=API_KEY)
  supabase: Client = create_client(URL, KEY)
except Exception as e:
  st.error(f"Erro ao carregar configurações: {e}")
  st.stop()

# --- INTERFACE ---
try:
  st.image("logo_brigada.png.png", width=150)
except Exception:
  pass

st.subheader("Assistente Virtual")

# --- LOGIN ---
usuario = st.selectbox("Selecione o usuário:", ["b1 (Bombeiro1)", "b2 (Bombeiro2)"])
senha = st.text_input("Senha:", type="password")

if st.button("Entrar"):
  if senha in ["senha1", "senha2"]:
    st.session_state["autenticado"] = True
    st.session_state["usuario"] = usuario.split(" ")[0]
    st.rerun()
  else:
    st.error("Senha incorreta.")

if st.session_state.get("autenticado", False):
  username = st.session_state["usuario"]
  st.success(f"Bem-vindo, {username}!")

  # --- UPLOAD DE FOTO ---
  uploaded_file = st.file_uploader(
      "Enviar foto da ocorrência", type=["jpg", "jpeg", "png"]
  )

  # --- PERGUNTAS E IA ---
  pergunta = st.text_input("Digite sua dúvida:")
  if st.button("Enviar Pergunta"):
    if pergunta.strip():
      try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resposta = model.generate_content(
            f"Contexto: Pássaro de fogo=balão (crime art 42 Lei 9605/98). Pergunta:"
            f" {pergunta}"
        ).text
        st.write("**Resposta da IA:**")
        st.write(resposta)

        # Tenta salvar no Supabase (se a tabela existir)
        try:
          supabase.table("interacoes").insert({
              "usuario": username,
              "pergunta": pergunta,
              "timestamp": datetime.datetime.now().isoformat(),
          }).execute()
        except Exception:
          pass  # Evita crash se a tabela não estiver criada no banco
      except Exception as e:
        st.error(f"Erro ao processar com a IA: {e}")
    else:
      st.warning("Digite uma pergunta.")

  # --- DASHBOARD BLINDADO ---
  st.subheader("📊 Análise de Interações")
  try:
    response = supabase.table("interacoes").select("*").execute()
    if response.data and len(response.data) > 0:
      df = pd.DataFrame(response.data)
      if "pergunta" in df.columns:
        st.bar_chart(df["pergunta"].value_counts())
      else:
        st.info("Aguardando dados estruturados de interações.")
    else:
      st.info(
          "Nenhuma interação registrada ainda (ou tabela 'interacoes' pendente"
          " de criação no Supabase)."
      )
  except Exception:
    st.info(
        "Painel pronto. Certifique-se de criar a tabela 'interacoes' no seu"
        " painel do Supabase se desejar salvar histórico."
    )