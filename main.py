import google.generativeai as genai
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import bcrypt
import time


app = Flask(__name__)
CORS(app)
app.secret_key = 'Zzdtt09$$##@@~~'


# Configure the API key for Google Generative AI
genai.configure(api_key='AIzaSyBxd0joqcMIzaTJyTbDX7kvOkwzvrhDdhw')  # Replace with your API key


# Function to connect to SQLite database
def connect_db():
    return sqlite3.connect('/tmp/salomao2.db')




# Function to load the Bible text from a .txt file
def load_bible(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


bible_text = load_bible('biblia.txt')


def limit_text(text, limit=400000):
    return text[:limit] + "..." if len(text) > limit else text


# Function to process user questions and generate responses
def answer_question(question):
    message = f"Sua pergunta: {question}\n Resposta baseada na Bíblia: {limit_text(bible_text)}"
    
    for _ in range(3):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(message)
            generated_text = response.candidates[0].content.parts[0].text
            return generated_text
            
        except Exception as e:
            if "429" in str(e):  # Rate limit error
                time.sleep(10)
            else:
                return "Erro ao responder sua pergunta."


    return "Não consegui gerar uma resposta."


# Create database tables
def create_tables():
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pergunta TEXT,
            resposta TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_chats (
            user_id INTEGER,
            chat_id INTEGER,
            PRIMARY KEY (user_id, chat_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
        )
    ''')


    db.commit()
    cursor.close()
    db.close()


# User registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')


    if not username or not password:
        return jsonify({'message': 'username e senha são obrigatórios.'}), 400


    db = connect_db()
    cursor = db.cursor()


    try:
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({'message': 'username já cadastrado.'}), 400


        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        db.commit()


        return jsonify({'message': 'Usuário registrado com sucesso.'}), 201
    except Exception as e:
        return jsonify({'message': 'Erro inesperado, tente novamente mais tarde.'}), 500
    finally:
        cursor.close()
        db.close()


# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')


    if not username or not password:
        return jsonify({'message': 'username e senha são obrigatórios.'}), 400
    
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
        
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
        session['user_id'] = user[0]
        return jsonify({'message': 'Login bem-sucedido.'}), 200
        
    return jsonify({'message': 'username ou senha incorretos.'}), 401


# User question route
@app.route('/perguntar', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('pergunta')
    user_id = session.get('user_id')


    if not question:
        return jsonify({'erro': 'Pergunta inválida.'}), 400


    answer = answer_question(question)
    
    db = connect_db()
    cursor = db.cursor()


    try:
        cursor.execute("INSERT INTO chats (user_id, pergunta, resposta) VALUES (?, ?, ?)", (user_id, question, answer))
        chat_id = cursor.lastrowid
        cursor.execute("INSERT INTO user_chats (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id))
        db.commit()
    except Exception as e:
        return jsonify({'erro': 'Erro ao salvar o chat.'}), 500
    finally:
        cursor.close()
        db.close()


    return jsonify({'resposta': answer})


# Route to get chat history
@app.route('/historico', methods=['GET'])
def history():
    user_id = session.get('user_id')


    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT pergunta, resposta, timestamp FROM chats WHERE user_id = ?", (user_id,))
    chats = cursor.fetchall()


    history = [{'pergunta': row[0], 'resposta': row[1], 'timestamp': row[2]} for row in chats]


    cursor.close()
    db.close()


    return jsonify(history)


# Initialize database and server
if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000)