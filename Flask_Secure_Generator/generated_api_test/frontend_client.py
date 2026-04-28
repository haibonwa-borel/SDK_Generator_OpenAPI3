import customtkinter as ctk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:5000/api/v1"

class FrontendApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Client API - Sample Product API")
        self.geometry("800x600")
        
        self.token = None
        self.current_frame = None
        
        self.show_login_frame()

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ctk.CTkFrame(self)
        self.current_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        ctk.CTkLabel(self.current_frame, text="Connexion", font=("Arial", 24)).pack(pady=20)
        
        self.username_entry = ctk.CTkEntry(self.current_frame, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self.current_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        
        ctk.CTkButton(self.current_frame, text="Se Connecter", command=self.login).pack(pady=10)
        ctk.CTkButton(self.current_frame, text="S'inscrire", command=self.register, fg_color="gray").pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            resp = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
                messagebox.showinfo("Succès", "Connexion réussie")
                self.show_dashboard()
            else:
                messagebox.showerror("Erreur", resp.json().get("msg", "Erreur de connexion"))
        except Exception as e:
            messagebox.showerror("Erreur de connexion", str(e))

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            resp = requests.post(f"{API_URL}/auth/register", json={"username": username, "password": password})
            if resp.status_code == 201:
                messagebox.showinfo("Succès", "Inscription réussie. Vous pouvez vous connecter.")
            else:
                messagebox.showerror("Erreur", resp.json().get("msg", "Erreur d'inscription"))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ctk.CTkFrame(self)
        self.current_frame.pack(fill="both", expand=True)
        
        # Tabs for each model
        self.tabview = ctk.CTkTabview(self.current_frame)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        
        self.tabview.add("Product")
        self.setup_product_tab(self.tabview.tab("Product"))
        
        self.tabview.add("Category")
        self.setup_category_tab(self.tabview.tab("Category"))
        
        
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    
    def setup_product_tab(self, parent):
        # Frame pour le formulaire d'ajout
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", pady=10)
        
        entries = {}
        
        ctk.CTkLabel(form_frame, text="name:").pack(side="left", padx=5)
        entries["name"] = ctk.CTkEntry(form_frame, width=100)
        entries["name"].pack(side="left", padx=5)
        
        ctk.CTkLabel(form_frame, text="price:").pack(side="left", padx=5)
        entries["price"] = ctk.CTkEntry(form_frame, width=100)
        entries["price"].pack(side="left", padx=5)
        
        ctk.CTkLabel(form_frame, text="in_stock:").pack(side="left", padx=5)
        entries["in_stock"] = ctk.CTkEntry(form_frame, width=100)
        entries["in_stock"].pack(side="left", padx=5)
        
        
        def add_item():
            data = {k: v.get() for k, v in entries.items() if v.get()}
            resp = requests.post(f"{API_URL}/products", json=data, headers=self.get_headers())
            if resp.status_code == 201:
                refresh_list()
                for v in entries.values():
                    v.delete(0, 'end')
            else:
                messagebox.showerror("Erreur", "Ajout impossible")

        ctk.CTkButton(form_frame, text="Ajouter", command=add_item).pack(side="left", padx=10)
        
        # Table pour afficher les données
        columns = ("id", "name", "price", "in_stock", )
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill="both", expand=True, pady=10)
        
        def refresh_list():
            for item in tree.get_children():
                tree.delete(item)
            try:
                resp = requests.get(f"{API_URL}/products", headers=self.get_headers())
                if resp.status_code == 200:
                    for row in resp.json():
                        values = (row.get("id", ""), row.get("name", ""), row.get("price", ""), row.get("in_stock", ""), )
                        tree.insert("", "end", values=values)
            except Exception as e:
                pass
                
        def delete_item():
            selected = tree.selection()
            if not selected:
                return
            item_id = tree.item(selected[0])['values'][0]
            resp = requests.delete(f"{API_URL}/products/{item_id}", headers=self.get_headers())
            if resp.status_code == 204:
                refresh_list()

        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x")
        ctk.CTkButton(action_frame, text="Rafraîchir", command=refresh_list).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Supprimer sélection", command=delete_item, fg_color="red").pack(side="left", padx=5)
        
        # Load initial data
        refresh_list()
    
    def setup_category_tab(self, parent):
        # Frame pour le formulaire d'ajout
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", pady=10)
        
        entries = {}
        
        ctk.CTkLabel(form_frame, text="title:").pack(side="left", padx=5)
        entries["title"] = ctk.CTkEntry(form_frame, width=100)
        entries["title"].pack(side="left", padx=5)
        
        ctk.CTkLabel(form_frame, text="description:").pack(side="left", padx=5)
        entries["description"] = ctk.CTkEntry(form_frame, width=100)
        entries["description"].pack(side="left", padx=5)
        
        
        def add_item():
            data = {k: v.get() for k, v in entries.items() if v.get()}
            resp = requests.post(f"{API_URL}/categorys", json=data, headers=self.get_headers())
            if resp.status_code == 201:
                refresh_list()
                for v in entries.values():
                    v.delete(0, 'end')
            else:
                messagebox.showerror("Erreur", "Ajout impossible")

        ctk.CTkButton(form_frame, text="Ajouter", command=add_item).pack(side="left", padx=10)
        
        # Table pour afficher les données
        columns = ("id", "title", "description", )
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill="both", expand=True, pady=10)
        
        def refresh_list():
            for item in tree.get_children():
                tree.delete(item)
            try:
                resp = requests.get(f"{API_URL}/categorys", headers=self.get_headers())
                if resp.status_code == 200:
                    for row in resp.json():
                        values = (row.get("id", ""), row.get("title", ""), row.get("description", ""), )
                        tree.insert("", "end", values=values)
            except Exception as e:
                pass
                
        def delete_item():
            selected = tree.selection()
            if not selected:
                return
            item_id = tree.item(selected[0])['values'][0]
            resp = requests.delete(f"{API_URL}/categorys/{item_id}", headers=self.get_headers())
            if resp.status_code == 204:
                refresh_list()

        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x")
        ctk.CTkButton(action_frame, text="Rafraîchir", command=refresh_list).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Supprimer sélection", command=delete_item, fg_color="red").pack(side="left", padx=5)
        
        # Load initial data
        refresh_list()
    

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = FrontendApp()
    app.mainloop()