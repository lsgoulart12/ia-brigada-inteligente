import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client, Client
import pandas as pd
import datetime
import google.generativeai as genai

# --- CONFIGURAÇÃO GEMINI ---
GEMINI_API_KEY = "AQ.Ab8RN6J5UQCm@m7PMa7WAKa51piCX8FGsbDExyuX8oYdKzf79A"
genai.configure(api_key=GEMINI_API_KEY)

# --- CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://seu-projeto-aqui.supabase.co"
SUPABASE_KEY = "sb_publishable_lI8HcYnr6pnQXdRUHrn1vQ_hldR_fIx"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- LOGO ---
st.image("logo.png", use_container_width=True)

st.title("IA BRIGADA")
st.subheader("Assistente Virtual para Bombeiros Civis")

# --- LOGIN ---
names = ["Bombeiro1", "Bombeiro2"]
usernames = ["b1", "b2"]
passwords = ["senha1", "senha2"]

authenticator = stauth.Authenticate(
    names, usernames, passwords,
    "brigada_cookie", "chave_assinatura", cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.success(f"Bem-vindo, {name}!")

    # --- REGISTRO DE PERGUNTAS ---
    pergunta = st.text_input("Digite sua pergunta:")
    if st.button("Enviar"):
        supabase.table("interacoes").insert({
            "usuario": username,
            "pergunta": pergunta,
            "timestamp": datetime.datetime.now().isoformat()
        }).execute()
        st.info("Pergunta registrada com sucesso!")

    # --- DASHBOARD ---
    st.subheader("📊 Análise de Interações")
    dados = supabase.table("interacoes").select("*").execute()
    df = pd.DataFrame(dados.data)

    if not df.empty:
        st.write("Total de acessos:", df["usuario"].nunique())
        st.write("Perguntas mais frequentes:")
        st.bar_chart(df["pergunta"].value_counts())

elif authentication_status is False:
    st.error("Usuário ou senha incorretos.")
elif authentication_status is None:
    st.warning("Por favor, insira suas credenciais.")
