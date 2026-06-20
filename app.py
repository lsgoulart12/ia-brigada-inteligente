import os
import streamlit as tf
import google.generativeai as genai
from PIL import Image

# 1. Configura a chave de API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. Configura o modelo
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. Interface visual
tf.title("🔥 IA Brigada Inteligente")
tf.subheader("Assistente virtual para suporte técnico e operacionais.")

# 4. Entradas do usuário
user_question = tf.text_input("Digite sua dúvida ou descrição da foto:")

# Criando o botão para anexar fotos
uploaded_file = tf.file_uploader("Anexe uma foto da situação (ex: extintores):", type=["jpg", "jpeg", "png"])

if tf.button("Analisar"):
    if uploaded_file is not None:
        # Processa a imagem
        img = Image.open(uploaded_file)
        
        # Gera conteúdo com imagem
        response = model.generate_content([user_question, img])
        tf.write(response.text)
    elif user_question:
        # Gera conteúdo apenas texto
        response = model.generate_content(user_question)
        tf.write(response.text)
    else:
        tf.warning("Por favor, digite uma pergunta ou envie uma imagem.")