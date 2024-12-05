import streamlit as st
from openai import OpenAI
import pdfkit
import requests
import time
import sys
import base64
import threading

print(sys.path)

# Configuração da API OpenAI
client = OpenAI(api_key="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")

# Configuração da Evolution API
EVOLUTION_API_KEY = "3509BC09DCA2-467B-86F7-BF3AD7E6D2DA"
INSTANCE_NAME = "BrunÃo2"
EVOLUTION_URL = "https://api.iagoflow.com"

# Função para gerar textos usando o OpenAI
def get_chat_completion(prompt, role="user", progress_bar=None):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é o mais poderoso especialista em copywriting, especialista em textos persuasivos para qualquer tipo de conteúdo."},
            {"role": role, "content": prompt}
        ]
    )
    if progress_bar:
        progress_bar.progress(1.0)
    return response.choices[0].message.content

# Prompts para cada tipo de copy
def get_prompts_by_category(category, idea):
    prompts = {
        "Redes sociais": {
            "Criador": f"Crie um post criativo e envolvente para redes sociais com base na ideia: {idea}.",
            "Revisor": "Revise o texto do post, melhore a clareza e torne-o mais atrativo para o público.",
            "Supervisor": "Dê feedback sobre como o texto pode ser mais eficaz para redes sociais.",
            "Finalizador": "Ajuste o texto do post de acordo com o feedback fornecido."
        },
        "Anúncios": {
            "Criador": f"Crie uma copy persuasiva para um anúncio com base na ideia: {idea}.",
            "Revisor": "Revise o texto do anúncio, melhorando o apelo emocional e a clareza.",
            "Supervisor": "Forneça feedback sobre como o texto pode ser mais convincente para conversões.",
            "Finalizador": "Finalize a copy do anúncio, incorporando o feedback fornecido."
        },
        "Títulos para blog": {
            "Criador": f"Crie 10 títulos altamente cativantes para um blog baseado na ideia: {idea}.",
            "Revisor": "Revise os títulos, melhorando sua atratividade e precisão.",
            "Supervisor": "Forneça feedback sobre como os títulos podem ser mais impactantes para SEO.",
            "Finalizador": "Finalize os títulos com base no feedback fornecido."
        },
        "Artigos para blog": {
            "Criador": f"Crie um artigo completo e informativo para um blog com base na ideia: {idea}.",
            "Revisor": "Revise o artigo, melhorando a clareza e a coesão das ideias.",
            "Supervisor": "Forneça feedback sobre como o artigo pode ser mais envolvente e informativo.",
            "Finalizador": "Finalize o artigo com base no feedback fornecido."
        },
        "Títulos para YouTube": {
            "Criador": f"Crie 10 títulos cativantes e otimizados para YouTube com base na ideia: {idea}.",
            "Revisor": "Revise os títulos, melhorando sua atratividade e relevância para SEO.",
            "Supervisor": "Dê feedback sobre como os títulos podem atrair mais cliques.",
            "Finalizador": "Finalize os títulos com base no feedback fornecido."
        },
        "Descrições para YouTube": {
            "Criador": f"Crie uma descrição envolvente e detalhada para um vídeo do YouTube com base na ideia: {idea}.",
            "Revisor": "Revise a descrição, melhorando sua clareza e impacto.",
            "Supervisor": "Dê feedback sobre como a descrição pode ser mais persuasiva.",
            "Finalizador": "Finalize a descrição com base no feedback fornecido."
        }
    }
    return prompts[category]

# Função principal para o fluxo de trabalho de copywriting
def copywriting_workflow(category, idea):
    workflow_responses = {}
    prompts = get_prompts_by_category(category, idea)

    # Barra de progresso geral
    progress = st.progress(0)

    for i, (etapa, prompt) in enumerate(prompts.items()):
        st.write(f"Gerando conteúdo: {etapa}...")
        etapa_progress = st.progress(0)
        
        if i == 0:
            texto = get_chat_completion(prompt, progress_bar=etapa_progress)
        else:
            texto = get_chat_completion(prompt + f"\nTexto anterior: {workflow_responses[list(prompts.keys())[i-1]]}", progress_bar=etapa_progress)
        
        workflow_responses[etapa] = texto
        progress.progress((i + 1) / len(prompts))
        time.sleep(1)

    return workflow_responses

# Função para criar um PDF com os textos gerados
def generate_pdf(responses):
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #333366; }
            h2 { color: #666699; }
        </style>
    </head>
    <body>
        <h1>Resultados das Copys Geradas</h1>
    """

    for etapa, texto in responses.items():
        html_content += f"<h2>{etapa}</h2><p>{texto}</p>"

    html_content += "</body></html>"

    pdf = pdfkit.from_string(html_content, False)
    return pdf

# Função para enviar mensagem para o WhatsApp
def send_whatsapp_message(name, number, message):
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "number": number,
        "text": message,
        "delay": 1
    }
    requests.post(url, json=payload, headers=headers)

# Função para enviar mensagem após um atraso
def send_delayed_message(name, number, message, delay):
    time.sleep(delay)
    send_whatsapp_message(name, number, message)

# Streamlit Interface
st.title("Gerador de Copywriting com PDF 📲")

# Entrada do usuário
user_name = st.text_input("Digite seu nome:")
user_whatsapp = st.text_input("Digite seu número de WhatsApp (incluindo código do país):", value="55")
category = st.selectbox("Selecione o tipo de Copy:", ["Redes sociais", "Anúncios", "Títulos para blog", "Artigos para blog", "Títulos para YouTube", "Descrições para YouTube"])
idea = st.text_area("Descreva sua ideia para a copy:")

if st.button("Gerar e Baixar Copy"):
    if not user_name or not user_whatsapp or not idea:
        st.error("Por favor, preencha todos os campos!")
    else:
        try:
            st.write("Iniciando processo de geração de copy...")
            responses = copywriting_workflow(category, idea)

            # Gerar PDF
            with st.spinner("Gerando PDF..."):
                pdf_content = generate_pdf(responses)
            
            if pdf_content:
                b64 = base64.b64encode(pdf_content).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="Copys_Geradas.pdf">Baixar Copys em PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Copy gerada com sucesso! Clique no link acima para baixar o PDF.")
            else:
                st.error("Erro ao gerar o PDF.")

            # Enviar mensagem no WhatsApp após 1 minuto (em background)
            message = f"Fala, {user_name}! Aqui é o IA.go. E aí, gostou das Copys?"
            threading.Thread(target=send_delayed_message, args=(user_name, user_whatsapp, message, 60)).start()

        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")
