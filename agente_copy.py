import streamlit as st
import openai
from fpdf import FPDF
import os
import requests
import time

# Configuração da API OpenAI
openai.api_key = "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"

# Configuração da Evolution API
EVOLUTION_API_KEY = "3509BC09DCA2-467B-86F7-BF3AD7E6D2DA"
INSTANCE_NAME = "BrunÃo2"
EVOLUTION_URL = "https://api.iagoflow.com"

# Função para gerar textos usando o OpenAI
def get_chat_completion(prompt, role="user"):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é o mais poderoso especialista em copywriting, especialista em textos persuasivos para qualquer tipo de conteúdo."},
            {"role": role, "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

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

    # Barra de progresso
    progress = st.progress(0)

    # Etapa 1: Criador
    st.write("Gerando conteúdo: Criador...")
    criador_text = get_chat_completion(prompts["Criador"])
    workflow_responses["Criador"] = criador_text
    progress.progress(25)
    time.sleep(1)

    # Etapa 2: Revisor
    st.write("Gerando conteúdo: Revisor...")
    revisor_text = get_chat_completion(prompts["Revisor"] + f"\nTexto: {criador_text}")
    workflow_responses["Revisor"] = revisor_text
    progress.progress(50)
    time.sleep(1)

    # Etapa 3: Supervisor
    st.write("Gerando conteúdo: Supervisor...")
    supervisor_feedback = get_chat_completion(prompts["Supervisor"] + f"\nTexto revisado: {revisor_text}")
    workflow_responses["Supervisor"] = supervisor_feedback
    progress.progress(75)
    time.sleep(1)

    # Etapa 4: Finalizador
    st.write("Gerando conteúdo: Finalizador...")
    final_text = get_chat_completion(prompts["Finalizador"] + f"\nTexto revisado: {revisor_text}\nFeedback: {supervisor_feedback}")
    workflow_responses["Finalizador"] = final_text
    progress.progress(100)

    return workflow_responses

# Função para criar um PDF com os textos gerados
def generate_pdf(responses, file_name="Copys_Geradas.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Resultados das Copys Geradas", ln=True, align='C')
    pdf.ln(10)

    for etapa, texto in responses.items():
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"{etapa}:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, texto)
        pdf.ln(5)

    pdf.output(file_name)
    return file_name

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
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200

# Streamlit Interface
st.title("Gerador de Copywriting com PDF e WhatsApp 📲")

# Entrada do usuário
user_name = st.text_input("Digite seu nome:")
user_whatsapp = st.text_input("Digite seu número de WhatsApp (incluindo código do país):", value="55")
category = st.selectbox("Selecione o tipo de Copy:", ["Redes sociais", "Anúncios", "Títulos para blog", "Artigos para blog", "Títulos para YouTube", "Descrições para YouTube"])
idea = st.text_area("Descreva sua ideia para a copy:")

if st.button("Gerar e Baixar Copy"):
    if not user_name or not user_whatsapp or not idea:
        st.error("Por favor, preencha todos os campos!")
    else:
        st.write("Iniciando processo de geração de copy...")
        responses = copywriting_workflow(category, idea)

        # Exibir resultados na interface
        st.subheader("Textos Gerados")
        for etapa, texto in responses.items():
            st.write(f"**{etapa}**: {texto}")

        # Gerar PDF
        pdf_file_name = generate_pdf(responses)
        with open(pdf_file_name, "rb") as pdf_file:
            st.download_button(
                label="Baixar Copys em PDF",
                data=pdf_file,
                file_name="Copys_Geradas.pdf",
                mime="application/pdf"
            )

        # Enviar mensagem no WhatsApp após 1 minuto
        message = f"Fala, {user_name}! Aqui é o IA.go. E aí, gostou das Copys?"
        time.sleep(60)  # Esperar 1 minuto
        if send_whatsapp_message(user_name, user_whatsapp, message):
            st.success("Mensagem enviada com sucesso para o WhatsApp!")
        else:
            st.error("Erro ao enviar mensagem para o WhatsApp.")
