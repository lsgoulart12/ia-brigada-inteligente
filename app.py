import streamlit as st
import os
from google.generativeai import GenerativeModel
import google.generativeai as genai

# Configuração da página do Streamlit
st.set_page_config(
    page_title="IA Brigada",
    page_icon="🧯",
    layout="centered"
)

# Título do Aplicativo
st.title("🧯 IA Brigada")
st.markdown("Assistente virtual especializado para Bombeiros Civis. Tire suas dúvidas rápidas sobre procedimentos de emergência, equipamentos e normas.")

# Configuração da API do Gemini
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("Chave API não configurada corretamente. Adicione a GEMINI_API_KEY nos secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# Configuração do Modelo com instrução de sistema otimizada para respostas curtas e diretas
model = GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="REGRA PRINCIPAL: Seja extremamente curta, técnica, direta e vá direto ao ponto, sem enrolação. Você é uma Bombeira Civil com vasta experiência. Sua missão é responder EXCLUSIVAMENTE em Português do Brasil. Seu foco principal é a Brigada de Incêndio (combate a princípios de incêndio, Plano de Emergência, inspeção de equipamentos como extintores e hidrantes, e primeiros socorros)."
)

# Inicializa o histórico de chat na sessão se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens anteriores do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário (chat input)
if prompt := st.chat_input("Digite sua dúvida de emergência ou inspeção..."):
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera a resposta utilizando o Gemini
    with st.chat_message("assistant"):
        with st.spinner("Consultando protocolos..."):
            try:
                # Inicia o chat mantendo o histórico da sessão
                chat = model.start_chat(history=[
                    {"role": m["role"], "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ])
                response = chat.send_message(prompt)
                response_text = response.text
                st.markdown(response_text)
                
                # Adiciona a resposta ao histórico
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar a resposta: {e}")