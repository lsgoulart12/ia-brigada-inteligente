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

# --- INTERFACE E LOGOTIPO ---
try:
  st.image("logo_brigada.png.png", width=150)
except Exception:
  pass

st.title("▲ IA BRIGADA")
st.subheader("Assistente Técnico Especializado - Brigada de Incêndio")

# --- LOGIN SIMPLIFICADO ---
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

  # --- INSTRUÇÃO DE SISTEMA PARA A IA (CONTEXTO OPERACIONAL E LEGAL) ---
  system_instruction = (
      "Você é um assistente técnico sênior especializado para bombeiros civis e brigadistas em grandes complexos (como estúdios de TV). "
      "Diretrizes obrigatórias de vocabulário e legislação brasileira:\n"
      "1. Terminologia: Na gíria operacional e preventiva, 'pássaro de fogo' refere-se a balões (soltura de balões).\n"
      "2. Base Legal: Soltar balões é crime ambiental inafiançável na delegacia em muitas situações de flagrante grave ou causa dano severo (Art. 42 da Lei de Crimes Ambientais - Lei nº 9.605/98), além de incorrer no Código Penal dependendo do risco gerado a vidas e patrimônio.\n"
      "3. Tratativa de Fiança: Explique tecnicamente que a fiança para crimes ambientais relacionados a balões pode ser arbitrada pela autoridade policial em casos de menor potencial ofensivo, mas em casos de queda com incêndio de grandes proporções ou risco iminente, o valor é elevado ou a prisão preventiva é mantida pelo juiz em audiência de custódia.\n"
      "Forneça sempre respostas técnicas, normativas e objetivas para o operador de brigada."
  )

  # --- INTERAÇÃO COM GEMINI E SUPABASE ---
  pergunta = st.text_input("Digite sua dúvida técnica ou ocorrência:")
  if st.button("Enviar Pergunta"):
    if pergunta.strip():
      try:
        # Configura o modelo com o contexto especializado da brigada
        generation_config = {"temperature": 0.3}
        modelo = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config=generation_config,
        )

        resposta_ia = modelo.generate_content(pergunta).text

        st.write("**Resposta Técnica da IA:**")
        st.write(resposta_ia)

        # Salva a interação no Supabase
        supabase.table("interacoes").insert({
            "usuario": username,
            "pergunta": pergunta,
            "resposta": resposta_ia,
            "timestamp": datetime.datetime.now().isoformat(),
        }).execute()

        st.success("Ocorrência/pergunta registrada com sucesso no Supabase!")
      except Exception as db_error:
        st.error(f"Erro ao processar com a IA ou salvar no banco: {db_error}")
    else:
      st.warning("Por favor, digite uma pergunta.")

  # --- DASHBOARD ---
  st.subheader("📊 Análise de Interações e Ocorrências")
  try:
    dados = supabase.table("interacoes").select("*").execute()
    if dados.data:
      df = pd.DataFrame(dados.data)
      if not df.empty:
        st.write("Total de acessos:", df["usuario"].nunique())
        st.write("Perguntas mais frequentes:")
        st.bar_chart(df["pergunta"].value_counts())
    else:
      st.info("Ainda não há interações registradas no banco.")
  except Exception as dash_error:
    st.error(f"Erro ao carregar o dashboard: {dash_error}")

  if st.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()