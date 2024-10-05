import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Chave de API do Google Generative AI
genai.configure(api_key='AIzaSyBxd0joqcMIzaTJyTbDX7kvOkwzvrhDdhw')  # Substitua 'YOUR_API_KEY' pela sua chave API

# Função para carregar a Bíblia em formato .txt
def carregar_biblia(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return f.read()

# Carregue a Bíblia de um arquivo .txt
biblia_texto = carregar_biblia('biblia.txt')

# Limitar o tamanho do texto que será enviado para a API
def limitar_texto(texto, limite= 400000):
    if len(texto) > limite:
        return texto[:limite] + "..."  # Retorna uma parte do texto com um aviso de truncamento
    return texto

# Função para processar a pergunta do usuário e gerar a resposta
def responder_pergunta(pergunta):
    mensagem = f"Você é Gideon uma consciência artificial interativa programada para agir como um assistente bíblico. Responda à pergunta com base no texto da Bíblia: '{pergunta}' usando o seguinte conteúdo da Bíblia: {limitar_texto(biblia_texto)}"
    
    for _ in range(3):  # Tente 3 vezes
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(mensagem)

            # Extrair o texto gerado da resposta
            generated_text = response.candidates[0].content.parts[0].text
            
            return generated_text  # Retorna o texto gerado pela IA
            
        except Exception as e:
            if "429" in str(e):  # Verifica se o erro é 429
                print("Limite de requisições atingido. Aguardando antes de tentar novamente.")
                time.sleep(10)  # Espera 10 segundos antes de tentar novamente
            else:
                print(f"Erro ao gerar resposta: {e}")
                return "Desculpe, não consegui responder sua pergunta."

    return "Desculpe, não consegui responder sua pergunta após várias tentativas."

# Rota para receber perguntas do usuário
@app.route('/perguntar', methods=['POST'])
def perguntar():
    dados = request.get_json()
    pergunta = dados.get('pergunta')

    if not pergunta:
        return jsonify({'erro': 'Por favor, envie uma pergunta válida.'}), 400

    try:
        print(f"Pergunta recebida: {pergunta}")  # Log da pergunta recebida
        resposta = responder_pergunta(pergunta)
        print(f"Resposta gerada: {resposta}")  # Log da resposta gerada
        return jsonify({'resposta': resposta})
    except Exception as e:
        print(f"Erro ao processar a pergunta: {e}")  # Log de erro
        return jsonify({'erro': 'Erro ao processar a pergunta. Tente novamente mais tarde.'}), 500

# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
