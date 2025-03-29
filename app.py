from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# Inicializa o banco
def init_db():
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL,
            categoria TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/mensagem", methods=["POST"])
def mensagem():
    texto = request.form.get("Body").strip()
    resposta = MessagingResponse()

    try:
        if texto.lower().startswith("gasto"):
            partes = texto.split(" ", 2)
            if len(partes) < 3:
                resposta.message("Formato inválido. Use: Gasto 20 mercado")
            else:
                valor = float(partes[1].replace(",", "."))
                categoria = partes[2].strip()
                data = date.today().isoformat()
                conn = sqlite3.connect("gastos.db")
                c = conn.cursor()
                c.execute("INSERT INTO gastos (valor, categoria, data) VALUES (?, ?, ?)", (valor, categoria, data))
                conn.commit()
                conn.close()
                resposta.message(f"Gasto de R${valor:.2f} em '{categoria}' registrado!")

        elif "total hoje" in texto.lower():
            data = date.today().isoformat()
            conn = sqlite3.connect("gastos.db")
            c = conn.cursor()
            c.execute("SELECT SUM(valor) FROM gastos WHERE data = ?", (data,))
            total = c.fetchone()[0] or 0
            conn.close()
            resposta.message(f"Total de gastos (hoje): R${total:.2f}")

        elif "gastos do dia" in texto.lower():
            partes = texto.lower().split("gastos do dia")
            if len(partes) > 1:
                data_str = partes[1].strip()
                data_formatada = datetime.strptime(data_str, "%d/%m").date().isoformat()
                conn = sqlite3.connect("gastos.db")
                c = conn.cursor()
                c.execute("SELECT valor, categoria FROM gastos WHERE data = ?", (data_formatada,))
                registros = c.fetchall()
                total = sum(r[0] for r in registros)
                if registros:
                    linhas = [f"- R${v:.2f} {cat}" for v, cat in registros]
                    resposta.message(f"📅 Gastos de {data_str}:
" + "\n".join(linhas) + f"\nTotal: R${total:.2f}")
                else:
                    resposta.message(f"Nenhum gasto encontrado para o dia {data_str}.")
                conn.close()

        else:
            resposta.message("Comando não reconhecido. Exemplos:
Gasto 25 mercado
Total hoje
Gastos do dia 25/03")

    except Exception as e:
        resposta.message("Erro ao processar a mensagem. Certifique-se de que o formato está correto.")

    return str(resposta)

# Observação: o resumo automático do fim do dia precisa de um agendador separado rodando em background
# Como o Render não roda jobs agendados automaticamente, essa parte precisa ser feita com um cron externo
# ou outro serviço como UptimeRobot, Zapier ou GitHub Actions diariamente chamando uma rota separada (ex: /resumo).

@app.route("/resumo", methods=["GET"])
def resumo_do_dia():
    data = date.today().isoformat()
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("SELECT categoria, SUM(valor) FROM gastos WHERE data = ? GROUP BY categoria", (data,))
    dados = c.fetchall()
    conn.close()
    if dados:
        linhas = [f"- {cat.capitalize()}: R${total:.2f}" for cat, total in dados]
        total_geral = sum(total for _, total in dados)
        return f"📊 Resumo do dia {datetime.today().strftime('%d/%m')}\n" + "\n".join(linhas) + f"\nTotal: R${total_geral:.2f}"
    else:
        return "Nenhum gasto registrado hoje."

if __name__ == "__main__":
    app.run()
