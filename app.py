import streamlit as st
import google.generativeai as genai

# Configuração da chave API vinda do Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inicialização do modelo
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🔥 IA Brigada Inteligente")
st.write("Assistente virtual para suporte técnico e operacional.")

# Entrada de texto
user_input = st.text_input("Digite sua dúvida:")

# Botão de análise
if st.button("Analisar"):
    if user_input:
        try:
            with st.spinner("Consultando a IA..."):
                response = model.generate_content(user_input)
                st.markdown("### Resposta da IA:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
    else:
        st.warning("Por favor, digite uma dúvida.")