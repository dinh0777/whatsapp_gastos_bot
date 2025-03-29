from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Criar banco e tabela se não existirem
def init_db():
    conn = sqlite3.connect('gastos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL,
            descricao TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/mensagem', methods=['POST'])
def mensagem():
    texto = request.form.get('Body').strip()
    resposta = MessagingResponse()

    try:
        if texto.lower().startswith('gasto'):
            partes = texto.split(' ', 2)
            if len(partes) < 3:
                resposta.message("Formato inválido. Use: Gasto 20 mercado")
            else:
                valor_raw = partes[1].replace(',', '.')
                valor = float(valor_raw)
                descricao = partes[2]
                data = datetime.now().strftime('%Y-%m-%d')
                conn = sqlite3.connect('gastos.db')
                c = conn.cursor()
                c.execute('INSERT INTO gastos (valor, descricao, data) VALUES (?, ?, ?)', (valor, descricao, data))
                conn.commit()
                conn.close()
                resposta.message(f"Gasto de R${valor:.2f} em '{descricao}' registrado!")
        elif texto.lower() == 'total hoje':
            hoje = datetime.now().strftime('%Y-%m-%d')
            conn = sqlite3.connect('gastos.db')
            c = conn.cursor()
            c.execute('SELECT SUM(valor) FROM gastos WHERE data = ?', (hoje,))
            total = c.fetchone()[0] or 0
            conn.close()
            resposta.message(f"Total de gastos (hoje): R${total:.2f}")
        else:
            resposta.message("Comando não reconhecido. Envie por exemplo:\nGasto 25 padaria\nTotal hoje")
    except Exception as e:
        resposta.message("Ocorreu um erro ao processar a mensagem.")
    
    return str(resposta)

