import streamlit as st
import google.generativeai as genai

# Configuração da página do Streamlit
st.set_page_config(
    page_title="IA Brigada",
    page_icon="🧯",
    layout="centered"
)

# Configuração da chave de API do Gemini através dos segredos do Streamlit
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("Erro ao configurar a chave de API. Verifique os segredos (secrets) no Streamlit Cloud.")

# Configuração do modelo com instruções de sistema especializadas
generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

system_instruction = """
Você é um assistente virtual especializado e técnico para Bombeiros Civis. 
Seu objetivo é tirar dúvidas rápidas sobre procedimentos de emergência, combate a incêndio, resgate, equipamentos de segurança, normas regulamentadoras e rotinas operacionais (incluindo diretrizes de segurança em estúdios e centrais de resíduos, como áreas de corte a quente e inspeções preventivas).
Suas respostas devem ser sempre diretas, claras, muito explicativas e fundamentadas em boas práticas de segurança, priorizando a precisão técnica e a objetividade.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# Título e descrição da interface
st.markdown("## 🧯 IA Brigada")
st.markdown("Assistente virtual especializado para Bombeiros Civis. Tire suas dúvidas rápidas sobre procedimentos de emergência, equipamentos e normas.")

# Inicializa o histórico de conversas no session_state do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens anteriores na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto do usuário (barra de chat)
if prompt := st.chat_input("Digite sua dúvida de emergência ou inspeção..."):
    # Adiciona a mensagem do usuário ao histórico visual e à sessão
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepara o histórico no formato correto exigido pela API do Gemini (usando 'model' em vez de 'assistant')
    gemini_history = []
    for msg in st.session_state.messages:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })

    # Gera a resposta utilizando a API do Gemini
    with st.chat_message("assistant"):
        with st.spinner("Analisando procedimento..."):
            try:
                chat = model.start_chat(history=gemini_history[:-1])
                response = chat.send_message(prompt)
                bot_response = response.text
                
                st.markdown(bot_response)
                
                # Salva a resposta no histórico da sessão
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            except Exception as e:
                error_message = f"Ocorreu um erro ao gerar a resposta: {e}. (Se o erro persistir, aguarde 1 minuto devido ao limite de cota gratuita da API)."
                st.error(error_message)