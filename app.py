import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client, Client
import pandas as pd
import datetime

# --- CONFIGURAÇÃO SEGURA DO SUPABASE ---
# Pegando as credenciais de forma segura do st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- TÍTULO E CABEÇALHO ---
st.title("IA BRIGADA")
st.subheader("Assistente Virtual para Bombeiros Civis - Estúdios Globo")

# --- LOGIN ---
names = ["Bombeiro Civil", "Supervisor"]
usernames = ["bombeiro", "supervisor"]
# Senhas de exemplo (em produção real, use hashes de senha)
passwords = ["senha123", "senha123"]

authenticator = stauth.Authenticate(
    names, usernames, passwords,
    "brigada_cookie", "chave_assinatura_secreta", cookie_expiry_days=30
)

# Renderiza o widget de login na barra lateral ou na página principal
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.success(f"Bem-vindo(a), {name}!")

    # --- REGISTRO DE OCORRÊNCIAS / REGISTROS DA BRIGADA ---
    st.markdown("### 📝 Novo Registro de Ocorrência")
    
    titulo = st.text_input("Título da Ocorrência:")
    descricao = st.text_area("Descrição detalhada:")
    local = st.text_input("Local (ex: CC3, Estúdios):")

    if st.button("Salvar Registro"):
        if titulo and descricao and local:
            # Salvando na tabela correta que criamos no Supabase: registros_brigada
            supabase.table("registros_brigada").insert({
                "titulo": titulo,
                "descricao": descricao,
                "local": local
            }).execute()
            st.success("Registro salvo com segurança no banco de dados!")
        else:
            st.warning("Por favor, preencha todos os campos antes de enviar.")

    # --- DASHBOARD / ANÁLISE ---
    st.markdown("---")
    st.subheader("📊 Registros Recentes da Brigada")
    
    # Buscando dados da tabela registros_brigada
    resposta = supabase.table("registros_brigada").select("*").execute()
    df = pd.DataFrame(resposta.data)

    if not df.empty:
        st.dataframe(df) # Exibe a tabela completa de forma elegante
    else:
        st.info("Nenhum registro encontrado no banco de dados ainda.")

    # Botão de Logout oficial do authenticator
    authenticator.logout("Sair", "main")

elif authentication_status is False:
    st.error("Usuário ou senha incorretos.")
elif authentication_status is None:
    st.warning("Por favor, insira suas credenciais de acesso.")