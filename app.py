from flask import Flask, request
from db import registrar_gasto, obter_total
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot de gastos rodando!"

@app.route("/mensagem", methods=["POST"])
def receber_mensagem():
    mensagem = request.form.get("Body", "").strip()
    resposta = processar_mensagem(mensagem)
    return resposta

def processar_mensagem(mensagem):
    if mensagem.lower().startswith("gasto"):
        partes = mensagem.split()
        if len(partes) >= 3:
            try:
                valor = float(partes[1].replace(",", "."))
                categoria = " ".join(partes[2:])
                registrar_gasto(valor, categoria)
                return f"Gasto de R${valor:.2f} em '{categoria}' registrado!"
            except ValueError:
                return "Formato inválido. Use: Gasto 25 mercado"
        else:
            return "Mensagem incompleta. Use: Gasto 25 mercado"
    elif "total hoje" in mensagem.lower():
        return obter_total("hoje")
    elif "total semana" in mensagem.lower():
        return obter_total("semana")
    elif "total mês" in mensagem.lower():
        return obter_total("mes")
    else:
        return "Comando não reconhecido. Use: 'Gasto 25 mercado', 'Total hoje', 'Total semana', 'Total mês'"

if __name__ == "__main__":
    app.run()
