import datetime
import google.generativeai as genai
import pandas as pd
from supabase import Client, create_client
import streamlit as st

# --- CONFIGURAÇÃO DE SEGURANÇA E CONEXÃO ---
# Garantimos que as chaves estão lidas sem espaços extras
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
st.image("logo_brigada.png.png", width=150)

st.subheader("Assistente Técnico Especializado - Brigada de Incêndio")

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

    # --- UPLOAD DE FOTO (O que você pediu de volta) ---
    uploaded_file = st.file_uploader("Enviar foto da ocorrência", type=["jpg", "jpeg", "png"])
    
    # --- PERGUNTAS E IA ---
    pergunta = st.text_input("Digite sua dúvida:")
    if st.button("Enviar Pergunta"):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            resposta = model.generate_content(f"Contexto: Pássaro de fogo=balão (crime art 42 Lei 9605/98). Pergunta: {pergunta}").text
            st.write(resposta)
            
            # Salvar
            supabase.table("interacoes").insert({"usuario": username, "pergunta": pergunta, "timestamp": datetime.datetime.now().isoformat()}).execute()
        except Exception as e:
            st.error(f"Erro na execução: {e}")

    # --- DASHBOARD ---
    try:
        dados = supabase.table("interacoes").select("*").execute()
        if dados.data:
            df = pd.DataFrame(dados.data)
            st.bar_chart(df["pergunta"].value_counts())
    except:
        st.error("Erro ao carregar dashboard.")