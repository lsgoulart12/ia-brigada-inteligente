import streamlit as tf
import google.generativeai as genai
import os
from PIL import Image

# 1. Configuração de Segurança: Busca a chave nos Secrets do Streamlit Cloud
# Se não encontrar, tenta buscar em uma variável de ambiente (uso local)
try:
    api_key = tf.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    tf.error("Erro: A chave GEMINI_API_KEY não foi encontrada. Configure-a nos 'Secrets' do Streamlit Cloud.")
    tf.stop()

genai.configure(api_key=api_key)

# 2. Configuração do Modelo: Usando a versão mais estável
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. Interface Visual
tf.title("🔥 IA Brigada Inteligente")
tf.subheader("Assistente virtual para suporte técnico e operacional.")

user_question = tf.text_input("Digite sua dúvida ou descrição da foto:")
uploaded_file = tf.file_uploader("Anexe uma foto da situação (ex: extintores):", type=["jpg", "jpeg", "png"])

# 4. Lógica de Execução
if tf.button("Analisar"):
    if not user_question and not uploaded_file:
        tf.warning("Por favor, digite algo ou envie uma imagem para analisar.")
    else:
        with tf.spinner("Analisando com IA..."):
            try:
                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([user_question, img])
                else:
                    response = model.generate_content(user_question)
                
                tf.markdown("### Resposta da IA:")
                tf.write(response.text)
            except Exception as e:
                tf.error(f"Ocorreu um erro ao consultar a IA: {e}")