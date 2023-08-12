import tkinter as tk
from tkinter import messagebox
import requests
import pprint


class CorreiosTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Correios Tracker")

        self.codigo_rastreamento_label = tk.Label(self.root, text="Código de rastreamento:")
        self.codigo_entry = tk.Entry(self.root, width=50)
        self.rastreio_button = tk.Button(self.root, text="Rastrear", command=self.rastrear_click)
        self.resultado_text = tk.Text(self.root, width=50, height=10, state="disabled")

        self.codigo_rastreamento_label.pack()
        self.codigo_entry.pack()
        self.rastreio_button.pack()
        self.resultado_text.pack()

    def rastrear_encomenda(self, codigo_rastreamento):
        url = f"https://api.linketrack.com/track/json?user=teste&token=1abcd00b2731640e886fb41a8a9671ad1434c599dbaa0a0de9a5aa619f29a83f&codigo={codigo_rastreamento}"

        response = requests.get(url)
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

    def rastrear_click(self):
        codigo = self.codigo_entry.get()
        if codigo:
            result = self.rastrear_encomenda(codigo)
            pp_result = pprint.pformat(result, depth=6)
            self.resultado_text.config(state=tk.NORMAL)
            self.resultado_text.delete("1.0", tk.END)
            self.resultado_text.insert(tk.END, pp_result)
            self.resultado_text.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Erro", "Insira um código de rastreamento válido.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CorreiosTracker(root)
    root.mainloop()
