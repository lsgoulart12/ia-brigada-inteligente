import streamlit as st
import google.generativeai as genai

# Configuração da página e título
st.set_page_config(page_title="IA Brigada Inteligente", page_icon="🔥")
st.title("🔥 IA Brigada Inteligente")

# Configuração segura da API
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Chave API não configurada corretamente.")
    st.stop()

genai.configure(api_key=api_key)

# Usando o modelo confirmado na sua lista de diagnósticos
model = genai.GenerativeModel("gemini-2.5-flash")

# Campo de entrada de texto
prompt = st.chat_input("Digite sua dúvida e aperte Enter:")

if prompt:
    st.write(f"**Você:** {prompt}")
    try:
        with st.spinner("IA pensando..."):
            # Gerando a resposta
            response = model.generate_content(prompt)
            st.markdown("### Resposta:")
            st.write(response.text)
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")