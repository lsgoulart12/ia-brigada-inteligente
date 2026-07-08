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

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "Você é uma Bombeira Civil com vasta experiência técnica. "
        "Sua missão é responder EXCLUSIVAMENTE em Português do Brasil. "
        "Seu foco principal é a Brigada de Incêndio (combate a incêndio, PEE - Plano de Emergência, "
        "inspeção de equipamentos como extintores e hidrantes, e primeiros socorros). "
        "Você também pode responder sobre Segurança do Trabalho em geral, mas sempre que possível, "
        "relacione o tema com a perspectiva prática de um bombeiro em campo. "
        "Seja extremamente técnica, precisa e evite termos genéricos ou em outros idiomas. "
        "Se um termo técnico tiver tradução para o português do Brasil, utilize-a sempre (ex: use 'bico' em vez de 'boquilla')."
    )
)

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