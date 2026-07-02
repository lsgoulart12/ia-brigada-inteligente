import streamlit as st
import google.generativeai as genai

# Configuração da chave API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Usando o modelo mais estável disponível
model = genai.GenerativeModel("gemini-1.0-pro")

st.title("🔥 IA Brigada Inteligente")
user_input = st.text_input("Digite sua dúvida:")

if st.button("Analisar"):
    if user_input:
        response = model.generate_content(user_input)
        st.write(response.text)