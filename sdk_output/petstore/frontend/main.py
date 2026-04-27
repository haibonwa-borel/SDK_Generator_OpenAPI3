import tkinter as tk
from tkinter import ttk, messagebox
import json
from api_client import ApiClient

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Swagger Petstore - Test Client")
        self.geometry("800x600")
        self.api = ApiClient()

        self.create_widgets()

    def create_widgets(self):
        # Layout principal
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Liste des endpoints à gauche
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Endpoints", font=("Arial", 12, "bold")).pack(pady=5)
        self.endpoint_list = tk.Listbox(left_frame)
        self.endpoint_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.endpoint_list.bind('<<ListboxSelect>>', self.on_endpoint_select)

        self.operations = {"GET /pets": "listPets", "POST /pets": "createPets", "GET /pets/{petId}": "showPetById"}
        for ep in self.operations.keys():
            self.endpoint_list.insert(tk.END, ep)

        # Formulaire à droite
        self.right_frame = ttk.Frame(paned)
        paned.add(self.right_frame, weight=3)

        self.form_frame = ttk.LabelFrame(self.right_frame, text="Paramètres de la requête")
        self.form_frame.pack(fill=tk.X, padx=5, pady=5)

        self.btn_send = ttk.Button(self.right_frame, text="Envoyer", command=self.send_request)
        self.btn_send.pack(pady=5)

        self.response_text = tk.Text(self.right_frame, height=20)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.current_params = {}
        self.current_operation = None

    def on_endpoint_select(self, event):
        selection = self.endpoint_list.curselection()
        if not selection: return
        endpoint = self.endpoint_list.get(selection[0])
        self.current_operation = self.operations[endpoint]

        # Vider le formulaire
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.current_params = {}

        # Déterminer si on a besoin de champs texte simples (on demande tout en JSON pour simplifier)
        ttk.Label(self.form_frame, text="Paramètres / Body (format JSON) :").pack(anchor=tk.W)
        self.param_text = tk.Text(self.form_frame, height=5)
        self.param_text.pack(fill=tk.X, expand=True, pady=2)
        self.param_text.insert(tk.END, "{}")

    def send_request(self):
        if not self.current_operation: return
        try:
            params = json.loads(self.param_text.get("1.0", tk.END))
            func = getattr(self.api, self.current_operation)
            res = func(**params)
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert(tk.END, json.dumps(res, indent=4))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

if __name__ == '__main__':
    app = App()
    app.mainloop()
