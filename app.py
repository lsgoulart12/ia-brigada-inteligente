import datetime
import google.generativeai as genai
import pandas as pd
from supabase import Client, create_client
import streamlit as st

# --- CONFIGURAÇÃO DE SEGURANÇA E CONEXÃO ---
try:
  GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
  SUPABASE_URL = st.secrets["SUPABASE_URL"]
  SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

  genai.configure(api_key=GEMINI_API_KEY)
  supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
  st.error(f"Erro crítico de configuração de credenciais: {e}")
  st.stop()

# --- INTERFACE ---
st.title("▲ IA BRIGADA")
st.subheader("Assistente Virtual")

# --- LOGIN SIMPLIFICADO DIRETO NO CÓDIGO ---
usuario = st.selectbox("Selecione o Usuário:", ["b1 (Bombeiro1)", "b2 (Bombeiro2)"])
senha = st.text_input("Senha:", type="password")

if st.button("Entrar"):
  if senha == "senha1" or senha == "senha2":
    st.session_state["autenticado"] = True
    st.session_state["usuario"] = usuario.split(" ")[0]
    st.rerun()
  else:
    st.error("Senha incorreta.")

if st.session_state.get("autenticado", False):
  username = st.session_state["usuario"]
  st.success(f"Bem-vindo, {username}!")

  # --- REGISTRO DE PERGUNTAS ---
  pergunta = st.text_input("Digite sua pergunta:")
  if st.button("Enviar Pergunta"):
    if pergunta.strip():
      try:
        supabase.table("interacoes").insert({
            "usuario": username,
            "pergunta": pergunta,
            "timestamp": datetime.datetime.now().isoformat(),
        }).execute()
        st.info("Pergunta registrada com sucesso no Supabase!")
      except Exception as db_error:
        st.error(f"Erro ao salvar no banco: {db_error}")
    else:
      st.warning("Digite algo antes de enviar.")

  # --- DASHBOARD ---
  st.subheader("📊 Análise de Interações")
  try:
    dados = supabase.table("interacoes").select("*").execute()
    if dados.data:
      df = pd.DataFrame(dados.data)
      if not df.empty:
        st.write("Total de acessos:", df["usuario"].nunique())
        st.write("Perguntas mais frequentes:")
        st.bar_chart(df["pergunta"].value_counts())
    else:
      st.info("Ainda não há interações registradas.")
  except Exception as dash_error:
    st.error(f"Erro ao carregar o dashboard: {dash_error}")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()