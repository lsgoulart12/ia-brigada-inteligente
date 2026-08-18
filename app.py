import streamlit as st
from google import genai
from PIL import Image

# Configuração inicial da página
st.set_page_config(
    page_title="Assistente Técnico - Bombeiro Civil",
    layout="wide"
)

# Inicialização e validação segura da API utilizando o pacote 'google-genai'
api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key and api_key.startswith("AIzaSy"):
    client = genai.Client(api_key=api_key)
else:
    st.error("Erro 401: A chave atual não é compatível com o Gemini. Por favor, configure uma chave válida no Google AI Studio que comece com 'AIzaSy'.")

st.title("Assistente Técnico - Brigada de Incêndio")

# Estrutura de colunas da interface
col1, col2 = st.columns([1, 2])

with col1:
    st.write("### Painel")
    st.markdown("Gerenciamento de ocorrências e diretrizes da brigada.")

with col2:
    # Formulário principal da aplicação
    with st.form("form_ocorrencia", clear_on_submit=False):
        
        # 1. Caixa de texto da dúvida técnica (posicionada em cima)
        pergunta = st.text_area("Digite sua dúvida técnica:", height=80)
        
        # 2. Campo de upload de foto (posicionado abaixo da caixa de texto, invertido)
        st.write("Anexar foto da ocorrência (opcional)")
        uploaded_file = st.file_uploader(
            "📎", 
            type=["jpg", "png", "jpeg"], 
            label_visibility="collapsed"
        )
        
        # 3. Botão de envio (obrigatoriamente na última linha do formulário)
        enviar = st.form_submit_button("Enviar Pergunta")

# Processamento após o clique no botão de envio
if enviar:
    if not api_key or not api_key.startswith("AIzaSy"):
        st.error("Erro 401: Chave de API inválida ou ausente. Verifique suas credenciais.")
    elif not pergunta.strip():
        st.warning("Por favor, digite sua dúvida antes de enviar.")
    else:
        with st.spinner("Analisando ocorrência..."):
            try:
                # Contexto fixo da brigada (Jargão e Lei preservados)
                contexto_brigada = (
                    "Você é um assistente técnico sênior para bombeiros civis e brigadistas, "
                    "especializado em normas de segurança, procedimentos de emergência e atendimento técnico. "
                )
                
                # Montagem do prompt com ou sem imagem compatível com a nova SDK
                prompt_completo = f"{contexto_brigada}\n\nDúvida do operador: {pergunta}"
                
                if uploaded_file is not None:
                    imagem = Image.open(uploaded_file)
                    conteudo = [prompt_completo, imagem]
                else:
                    conteudo = prompt_completo
                
                # Chamada do modelo utilizando a biblioteca moderna 'google-genai'
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=conteudo
                )
                
                # Exibição da resposta gerada
                st.markdown("### Resposta Técnica:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a solicitação: {e}")