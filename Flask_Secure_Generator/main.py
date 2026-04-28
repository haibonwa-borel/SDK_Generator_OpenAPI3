import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import threading
from generator import FlaskGenerator

# Configuration de base CustomTkinter
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class GeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flask Secure SDK Generator")
        self.root.geometry("650x350")
        
        self.openapi_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self.root, text="Flask Secure SDK Generator", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # OpenAPI File Selection
        frame1 = ctk.CTkFrame(self.root, fg_color="transparent")
        frame1.pack(fill=tk.X, padx=40, pady=10)
        
        label1 = ctk.CTkLabel(frame1, text="Fichier OpenAPI:", width=120, anchor="w")
        label1.pack(side=tk.LEFT)
        
        entry1 = ctk.CTkEntry(frame1, textvariable=self.openapi_path, width=300)
        entry1.pack(side=tk.LEFT, padx=10)
        
        btn1 = ctk.CTkButton(frame1, text="Parcourir", command=self.browse_file, width=100)
        btn1.pack(side=tk.LEFT)
        
        # Output Directory Selection
        frame2 = ctk.CTkFrame(self.root, fg_color="transparent")
        frame2.pack(fill=tk.X, padx=40, pady=10)
        
        label2 = ctk.CTkLabel(frame2, text="Dossier de sortie:", width=120, anchor="w")
        label2.pack(side=tk.LEFT)
        
        entry2 = ctk.CTkEntry(frame2, textvariable=self.output_dir, width=300)
        entry2.pack(side=tk.LEFT, padx=10)
        
        btn2 = ctk.CTkButton(frame2, text="Parcourir", command=self.browse_dir, width=100)
        btn2.pack(side=tk.LEFT)
        
        # Generate Button
        self.generate_btn = ctk.CTkButton(self.root, text="Générer l'API Flask", command=self.generate, font=ctk.CTkFont(size=15, weight="bold"), height=40)
        self.generate_btn.pack(pady=30)
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.root, orientation="horizontal", width=400, mode='indeterminate')
        self.progress.set(0)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier OpenAPI",
            filetypes=(("YAML files", "*.yaml *.yml"), ("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.openapi_path.set(filename)
            
    def browse_dir(self):
        dirname = filedialog.askdirectory(title="Sélectionner le dossier de destination")
        if dirname:
            self.output_dir.set(dirname)
            
    def generate(self):
        if not self.openapi_path.get() or not self.output_dir.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier OpenAPI et un dossier de destination.")
            return
            
        self.generate_btn.configure(state="disabled")
        self.progress.pack(pady=10) # Show progress bar
        self.progress.start()
        
        # Run generation in a separate thread to keep UI responsive
        threading.Thread(target=self._run_generator, daemon=True).start()
        
    def _run_generator(self):
        try:
            generator = FlaskGenerator(self.openapi_path.get(), self.output_dir.get())
            generator.generate()
            self.root.after(0, self._on_success)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))
            
    def _on_success(self):
        self.progress.stop()
        self.progress.pack_forget() # Hide progress bar
        self.generate_btn.configure(state="normal")
        messagebox.showinfo("Succès", "Génération du backend Flask terminée avec succès !")
        
    def _on_error(self, error_msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.generate_btn.configure(state="normal")
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la génération:\n{error_msg}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Flask Secure SDK Generator")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--openapi", type=str, help="Path to OpenAPI file")
    parser.add_argument("--out", type=str, help="Output directory")
    
    args = parser.parse_args()
    
    if args.cli:
        if not args.openapi or not args.out:
            print("Erreur: --openapi et --out sont requis en mode CLI.")
            exit(1)
        generator = FlaskGenerator(args.openapi, args.out)
        generator.generate()
    else:
        root = ctk.CTk()
        app = GeneratorApp(root)
        root.mainloop()
