import datetime
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from supabase import Client, create_client

# ==========================================
# CONFIGURAÇÕES E CONEXÃO COM O BANCO DE DADOS
# ==========================================

try:
  SUPABASE_URL = st.secrets["SUPABASE_URL"]
  SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
  supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
  st.error("Erro crítico de configuração de credenciais.")
  st.stop()

# ==========================================
# CONFIGURAÇÃO DE AUTENTICAÇÃO
# ==========================================

names = ["Bombeiro Civil", "Supervisor"]
usernames = ["bombeiro", "supervisor"]
passwords = ["senha123", "senha123"]

authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    cookie_name="brigada_cookie",
    key="chave_assinatura_secreta",
    cookie_expiry_days=30,
)

name, authentication_status, username = authenticator.login("Login", "main")

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================

st.title("IA BRIGADA")
st.subheader("Assistente Virtual para Bombeiros Civis - Estúdios Globo")

if authentication_status:
  st.success(f"Bem-vindo(a), {name}!")

  # ------------------------------------------
  # MÓDULO: CADASTRO DE OCORRÊNCIAS COM BLINDAGEM
  # ------------------------------------------
  st.markdown("### Novo Registro de Ocorrência")

  titulo = st.text_input("Título da Ocorrência")
  descricao = st.text_area("Descrição Detalhada")
  local = st.text_input("Local (ex: CC3, Estúdios)")

  if st.button("Salvar Registro"):
    if titulo.strip() and descricao.strip() and local.strip():
      try:
        # Bloco seguro contra falhas de conexão no banco
        supabase.table("registros_brigada").insert({
            "titulo": titulo.strip(),
            "descricao": descricao.strip(),
            "local": local.strip(),
        }).execute()
        st.success("Registro salvo com segurança no banco de dados.")
      except Exception as ex:
        st.error(f"Erro ao comunicar com o banco de dados: {ex}")
    else:
      st.warning("Preencha todos os campos obrigatórios corretamente.")

  # ------------------------------------------
  # MÓDULO: DASHBOARD E CONSULTA DE DADOS
  # ------------------------------------------
  st.markdown("---")
  st.markdown("### Registros Recentes da Brigada")

  try:
    resposta = supabase.table("registros_brigada").select("*").execute()
    df = pd.DataFrame(resposta.data)

    if not df.empty:
      st.dataframe(df)
    else:
      st.info("Nenhum registro encontrado no banco de dados.")
  except Exception as ex:
    st.warning("Não foi possível carregar os registros no momento.")

  authenticator.logout("Sair", "main")

elif authentication_status is False:
  st.error("Usuário ou senha incorretos.")
elif authentication_status is None:
  st.warning("Insira suas credenciais de acesso.")