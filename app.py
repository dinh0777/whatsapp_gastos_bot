from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gastos.db'
db = SQLAlchemy(app)

# Modelo de gasto
class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100), nullable=True)
    data = db.Column(db.Date, default=datetime.utcnow)

# Inicializar o banco de dados
with app.app_context():
    db.create_all()

@app.route("/mensagem", methods=['POST'])
def receber_mensagem():
    texto = request.form.get('Body').lower()
    resposta = MessagingResponse()

    if texto.startswith("gasto"):
        partes = texto.split()
        try:
            valor = float(partes[1].replace(",", "."))
            categoria = partes[2] if len(partes) > 2 else "geral"
            novo_gasto = Gasto(valor=valor, categoria=categoria, data=datetime.today().date())
            db.session.add(novo_gasto)
            db.session.commit()
            resposta.message(f"✅ Gasto de R${valor:.2f} em '{categoria}' registrado com sucesso!")
        except Exception as e:
            resposta.message("⚠️ Formato inválido. Use: 'Gasto 89,90 mercado'")
    
    elif texto == "total hoje":
        hoje = datetime.today().date()
        gastos = db.session.query(Gasto).filter(Gasto.data == hoje).all()
        if not gastos:
            resposta.message("📆 Nenhum gasto registrado hoje.")
        else:
            total = sum(g.valor for g in gastos)
            resposta.message(f"💰 Total de hoje: R${total:.2f}")
            for g in gastos:
                resposta.message(f"• {g.valor:.2f} ({g.categoria})")

    elif texto.startswith("gastos do dia"):
        try:
            data_str = texto.split("gastos do dia")[1].strip()
            data = datetime.strptime(data_str, "%d/%m").replace(year=datetime.now().year)
            gastos_dia = db.session.query(Gasto).filter(Gasto.data == data).all()
            if not gastos_dia:
                resposta.message(f"📆 Nenhum gasto registrado em {data_str}.")
            else:
                resposta.message(f"📆 Gastos de {data_str}:")
                for gasto in gastos_dia:
                    resposta.message(f"• {gasto.valor:.2f} ({gasto.categoria})")
        except:
            resposta.message("⚠️ Formato inválido. Tente: 'Gastos do dia 25/03'")

    else:
        resposta.message("🤖 Comandos disponíveis:\n"
                         "• Gasto 20,50 mercado\n"
                         "• Total hoje\n"
                         "• Gastos do dia 25/03")

    return str(resposta)

if __name__ == "__main__":
    app.run(debug=True)
