import datetime
import google.generativeai as genai
import pandas as pd
from supabase import Client, create_client
import streamlit as st

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="IA BRIGADA", layout="centered")

# --- BLOCO DE SEGURANÇA E CONEXÃO ---
# Garantimos a leitura das chaves diretamente dos secrets do Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"].strip()
    URL = st.secrets["SUPABASE_URL"].strip()
    KEY = st.secrets["SUPABASE_KEY"].strip()

    genai.configure(api_key=API_KEY)
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Erro ao inicializar serviços: {e}")

# --- INTERFACE ---
st.image("logo_brigada.png.png", width=120)
st.title("▲ IA BRIGADA")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    usuario = st.selectbox("Selecione o usuário:", ["b1 (Bombeiro1)", "b2 (Bombeiro2)"])
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == "senha1" or senha == "senha2":
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario.split(" ")[0]
            st.rerun()
        else:
            st.error("Senha incorreta.")
else:
    username = st.session_state["usuario"]
    st.success(f"Bem-vindo, {username}!")

    # Upload e Dúvida integrados
    uploaded_file = st.file_uploader("Adicionar foto da ocorrência (opcional)", type=["jpg", "png"])
    pergunta = st.text_area("Digite sua dúvida técnica:")

    if st.button("Enviar Pergunta"):
        if pergunta.strip():
            # Contexto fixo e imutável (Jargão e Lei)
            contexto = (
                "Você é um especialista em Brigada. Jargão: 'Pássaro de Fogo' é balão. "
                "Base legal: Lei 9.605/98 Art. 42 (crime ambiental). "
                "Informa sempre: pena de detenção de 1 a 3 anos ou multa, ou ambas. "
                "Sobre fiança: explicite que é arbitrada pela autoridade policial conforme o caso."
            )
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"{contexto} | Pergunta: {pergunta}")
                st.write("**Resposta:**", response.text)

                # Salvar no Supabase (silencioso para não sujar)
                try:
                    supabase.table("interacoes").insert({
                        "usuario": username,
                        "pergunta": pergunta,
                        "timestamp": datetime.datetime.now().isoformat()
                    }).execute()
                except:
                    pass
            except Exception:
                st.error("Erro na comunicação com a IA. Verifique sua chave API.")
        else:
            st.warning("Por favor, digite sua dúvida.")

    if st.button("Sair"):
        st.session_state["autenticado"] = False
        st.rerun()