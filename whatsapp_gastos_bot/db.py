import sqlite3
import datetime

def conectar():
    conn = sqlite3.connect("gastos.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, valor REAL, categoria TEXT, data TEXT)")
    return conn

conn = conectar()

def registrar_gasto(valor, categoria):
    data = datetime.date.today().isoformat()
    conn.execute("INSERT INTO gastos (valor, categoria, data) VALUES (?, ?, ?)", (valor, categoria, data))
    conn.commit()

def obter_total(periodo):
    hoje = datetime.date.today()
    cursor = conn.cursor()

    if periodo == "hoje":
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE data = ?", (hoje.isoformat(),))
    elif periodo == "semana":
        inicio_semana = hoje - datetime.timedelta(days=hoje.weekday())
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE data >= ?", (inicio_semana.isoformat(),))
    elif periodo == "mes":
        inicio_mes = hoje.replace(day=1)
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE data >= ?", (inicio_mes.isoformat(),))
    else:
        return "Período inválido."

    total = cursor.fetchone()[0]
    return f"Total de gastos ({periodo}): R${total:.2f}" if total else f"Nenhum gasto registrado para {periodo}."
