# IA Brigada Inteligente

Assistente virtual para suporte técnico, prevenção e consulta de normas regulamentadoras aplicadas a brigadas de incêndio. O sistema utiliza a linguagem Python e a biblioteca Streamlit para construir a interface de interação com o usuário, conectando-se a modelos de linguagem para processamento de consultas operacionais.

---

## Segurança da Informação e Gestão de Credenciais

Alinhado com as boas práticas de Engenharia de Software e o princípio de Security by Design, o projeto adota medidas rígidas de proteção de dados:
* Gerenciamento de Credenciais: A chave de acesso à API (API Key) não é armazenada de forma estática no código-fonte. O sistema utiliza variáveis de ambiente protegidas por meio do mecanismo st.secrets do Streamlit, impedindo a exposição ou vazamento de credenciais em repositórios públicos do GitHub.
* Criptografia de Tráfego: Toda a comunicação entre o front-end e os serviços de processamento é realizada sob o protocolo HTTPS, garantindo a integridade e confidencialidade dos dados trafegados.

---

## Próximas Implementações

O cronograma de desenvolvimento prevê a expansão do assistente para os seguintes módulos técnicos:
* Interface Multi-Modal: Implementação de linhas de código para processamento de áudio, englobando a transcrição de voz para texto (Speech-to-Text) e conversão de texto para voz (Text-to-Speech).
* Visão Computacional: Inclusão de rotinas para análise técnica de imagens, permitindo a verificação visual de conformidade em equipamentos de combate a incêndio e sinalizações.
* Integração de Documentos (RAG): Arquitetura para leitura e indexação de arquivos PDF e transcrições de vídeos de treinamento, viabilizando consultas dinâmicas à base de dados local.

---

## Requisitos Técnicos

* Linguagem: Python
* Interface de Usuário: Streamlit
* Processamento: Google Gemini API
