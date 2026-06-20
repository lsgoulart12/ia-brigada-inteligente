import os
import streamlit as tf
from google import genai
from google.genai import types
from PIL import Image  # Biblioteca para processar a foto que o usuário enviar

# 1. Configura a chave de API diretamente no ambiente
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6JuZX_yxPgOxuqZGezFpLnbhooAaAWmH9QkEGrHni9ieg"

# 2. Inicializa o cliente do Gemini
client = genai.Client()

# 3. Interface visual com os emotes de Brigada
tf.title("🧯👨‍🚒 IA Brigada Inteligente")
tf.subheader("Assistente virtual para suporte técnico e vistoria de riscos operacionais.")

# 4. Entradas do usuário: Texto E/OU Imagem de inspeção
user_question = tf.text_input("Digite sua dúvida ou descreva o que está na foto:")

# Criando o botão para anexar fotos de irregularidades (fios, tomadas, extintores)
uploaded_file = tf.file_uploader("Anexe uma foto da situação suspeita para inspeção visual:", type=["jpg", "jpeg", "png"])

# Exibe a foto na tela se o usuário fizer o upload
imagem_analise = None
if uploaded_file:
    imagem_analise = Image.open(uploaded_file)
    tf.image(imagem_analise, caption="Foto enviada para vistoria da Brigada", use_container_width=True)

# 5. Processamento e regras da Brigada
if user_question or imagem_analise:
    try:
        # Criamos a lista de conteúdos. O Gemini aceita texto e imagem juntos na mesma lista!
        conteudo_enviado = []
        
        if user_question:
            conteudo_enviado.append(user_question)
            
        if imagem_analise:
            conteudo_enviado.append(imagem_analise)
            # Se o usuário mandou a foto mas não escreveu nada, damos um empurrãozinho na pergunta
            if not user_question:
                conteudo_enviado.append("Analise esta imagem sob a ótica de segurança do trabalho e riscos de incêndio. O que há de errado ou perigoso aqui?")

        # Chamada da API passando o texto e a foto juntos
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=conteudo_enviado,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Você é um assistente especialista em segurança do trabalho, prevenção e combate a incêndio, e brigada civil. "
                    "Se o usuário enviar uma foto de uma irregularidade (fiação, tomada, obstrução), analise visualmente os riscos de curto-circuito, "
                    "princípio de incêndio ou acidentes e indique a conduta preventiva correta imediatamente."
                )
            )
        )
        
        tf.write("### 🤖 Avaliação Técnica:")
        tf.write(response.text)
        
    except Exception as e:
        tf.error(f"Erro ao processar a solicitação técnica: {e}")