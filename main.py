import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import threading
import sqlite3


class CorreiosTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Correios Tracker")

        self.style = ttk.Style()
        self.style.theme_use("winnative")

        self.db_conn = sqlite3.connect('correios.db')
        self.criar_db()

        self.codigo_rastreamento_label = tk.Label(
            self.root, text="Código de rastreamento:")
        self.root.resizable(False, False)
        self.codigo_entry = tk.Entry(self.root, width=50)
        self.rastreio_button = tk.Button(
            self.root, text="Rastrear", command=self.rastrear_click)
        self.resultado_text = tk.Text(
            self.root, width=60, height=15, wrap="word", state="normal")
        self.resultado_text.tag_configure("error", foreground="red")
        self.carregamento_label = tk.Label(self.root, text="Carregando...")

        self.carregamento_label.grid(
            row=0, column=1, padx=10, pady=10, columnspan=2, sticky="w")
        self.codigo_rastreamento_label.grid(
            row=1, column=1, padx=10, pady=10, sticky="w")
        self.codigo_entry.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.rastreio_button.grid(
            row=1, column=3, padx=10, pady=10, sticky="w")
        self.resultado_text.grid(
            row=2, column=1, padx=10, pady=10, columnspan=3, sticky="w")

        self.codigo_cadastro_label = tk.Label(
            self.root, text="Cadastrar novo código:")
        self.codigo_cadastro_entry = tk.Entry(self.root, width=50)
        self.cadastrar_button = tk.Button(
            self.root, text="Cadastrar", command=self.cadastrar_codigo)

        self.codigo_cadastro_label.grid(
            row=3, column=1, padx=10, pady=10, sticky="w")
        self.codigo_cadastro_entry.grid(
            row=3, column=2, padx=10, pady=10, sticky="w")
        self.cadastrar_button.grid(
            row=3, column=3, padx=10, pady=10, sticky="w")

        self.notificacao_update()

    def criar_db(self):
        cursor = self.db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rastreios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT
            )
        """)
        self.db_conn.commit()

    def inserir_codigo(self, codigo):
        cursor = self.db_conn.cursor()
        cursor.execute("""
            INSERT INTO rastreios (codigo) VALUES (?)
        """, (codigo,))
        self.db_conn.commit()

    def pegar_codigos(self):
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT codigo FROM rastreios
        """)
        return [row[0] for row in cursor.fetchall()]

    def cadastrar_codigo(self):
        novo_codigo = self.codigo_cadastro_entry.get()
        if novo_codigo:
            self.inserir_codigo(novo_codigo)
            self.codigo_cadastro_entry.delete(0, tk.END)
            messagebox.showinfo("Sucesso", "Código cadastrado com sucesso!")
        else:
            messagebox.showerror("Erro", "Insira um código válido para cadastrar.")

    def atualizar_codigos_cadastrados(self):
        codigos_cadastrados = self.pegar_codigos()
        self.resultado_text.config(state="normal")
        self.resultado_text.delete("1.0", tk.END)
        for codigo in codigos_cadastrados:
            result = self.rastrear_encomenda(codigo)
            if not result[0].get("error"):
                for evento in result:
                    formatted_evento = self.format_evento(evento)
                    self.resultado_text.insert(tk.END, formatted_evento)
        self.resultado_text.config(state="disabled")
        
        
        threading.Timer(900, self.atualizar_codigos_cadastrados).start()

    def notificacao_update(self):
        threading.Timer(0, self.atualizar_codigos_cadastrados).start()

    def format_evento(self, evento):
        formatted_evento = f"Data: {evento['data']} {evento['hora']}\n"
        formatted_evento += f"Local: {evento['local']}\n"
        formatted_evento += f"Status: {evento['status']}\n"
        if evento.get('subStatus'):
            formatted_evento += f"SubStatus: {evento['subStatus']}\n"
        formatted_evento += "-" * 40 + "\n"
        return formatted_evento

    def rastrear_encomenda(self, codigo_rastreamento):
        url = f"https://api.linketrack.com/track/json?user=teste&token=1abcd00b2731640e886fb41a8a9671ad1434c599dbaa0a0de9a5aa619f29a83f&codigo={codigo_rastreamento}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "erro" in data:
                return [{"error": "Código de rastreamento inválido."}]
            else:
                eventos = data.get("eventos", [])
                eventos_formatados = []
                for i in eventos:
                    data_evento = i.get("data", "")
                    hora_evento = i.get("hora", "")
                    local_evento = i.get("local", "")
                    status_evento = i.get("status", "")
                    sub_status_evento = i.get("subStatus", "")

                    evento_formatado = {
                        "data": data_evento,
                        "hora": hora_evento,
                        "local": local_evento,
                        "status": status_evento,
                        "subStatus": sub_status_evento
                    }
                    eventos_formatados.append(evento_formatado)
                return eventos_formatados
        except requests.exceptions.HTTPError as e:
            messagebox.showerror(
                "Erro", "Erro ao tentar se conectar com o servidor.")
            return [{"error": f"Erro ao tentar se conectar com o servidor. {str(e)} "}]

    def rastrear_click(self):
        codigo = self.codigo_entry.get()
        self.carregamento_label.grid()
        self.resultado_text.config(state="normal")
        self.resultado_text.delete("1.0", tk.END)

        if codigo:
            result = self.rastrear_encomenda(codigo)
            if result[0].get("error"):
                self.resultado_text.insert(tk.END, result[0]["error"], "error")
            else:
                for evento in result:
                    formatted_evento = self.format_evento(evento)
                    self.resultado_text.insert(tk.END, formatted_evento)
        else:
            messagebox.showerror(
                "Erro", "Insira um código de rastreamento válido.")

        self.resultado_text.config(state="disabled")
        self.carregamento_label.grid_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = CorreiosTracker(root)
    root.mainloop()
