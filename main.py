import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests


class CorreiosTracker:
    """
    CorreiosTracker é uma aplicaçã simples para rastrear pacotes suas encomendas com a API dos correios.

    Atributos:
        root: instância principal para a aplicação.
    """

    def __init__(self, root):
        """
        Inicializa a aplicação.

        Args:
            root: A instância principal Tkinter para a aplicação.
        """
        self.root = root
        self.root.title("Correios Tracker")

        self.style = tk.ttk.Style()
        self.style.theme_use("winnative")

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

    def format_evento(self, evento):
        """
        Formata o objeto com eventos para que fique mais legivel ao usuário.

        Args:
            evento (dict): dicionário contendo informações do evento de rastreamento.

        Returns:
            @str: Informações do evento de rastreamento formatadas.
        """
        formatted_evento = f"Data: {evento['data']} {evento['hora']}\n"
        formatted_evento += f"Local: {evento['local']}\n"
        formatted_evento += f"Status: {evento['status']}\n"
        if evento.get('subStatus'):
            formatted_evento += f"SubStatus: {evento['subStatus']}\n"
        formatted_evento += "-" * 40 + "\n"
        return formatted_evento

    def rastrear_encomenda(self, codigo_rastreamento):
        """
        Obtém informações do rastreamento para o código de rastreamento.

        Args:
            codigo_rastreamento (str): Codigo para efetuar o rastreio.

        Returns:
            array: Uma lista de dicionários contendo informações de eventos de rastreamento formatadas.
        """
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
        """
        Manipula o evento de clique.

        Obtém informações de rastreamento com base no código de rastreamento inserido e atualiza a interface de usuário retornando uma mensagem de erro ou atualizacao do codigo.
        """
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
