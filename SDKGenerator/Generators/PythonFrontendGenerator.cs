using Microsoft.OpenApi.Models;
using System;
using System.IO;
using System.Linq;
using System.Text;

namespace SDKGenerator.Generators
{
    public class PythonFrontendGenerator
    {
        private readonly OpenApiDocument _document;
        private readonly string _outputDir;
        private readonly Action<string> _logger;

        public PythonFrontendGenerator(OpenApiDocument document, string outputDir, Action<string> logger)
        {
            _document = document;
            _outputDir = outputDir;
            _logger = logger;
        }

        public void Generate()
        {
            GenerateApiClient();
            GenerateTkinterApp();
        }

        private void GenerateApiClient()
        {
            var apiClientPath = Path.Combine(_outputDir, "frontend", "api_client.py");
            var sb = new StringBuilder();

            sb.AppendLine("import requests");
            sb.AppendLine();
            sb.AppendLine("class ApiClient:");
            sb.AppendLine("    def __init__(self, base_url=\"http://127.0.0.1:8000\"):");
            sb.AppendLine("        self.base_url = base_url");
            sb.AppendLine();

            foreach (var pathKvp in _document.Paths)
            {
                string path = pathKvp.Key;
                foreach (var opKvp in pathKvp.Value.Operations)
                {
                    string method = opKvp.Key.ToString().ToLower();
                    string operationId = NormalizeName(opKvp.Value.OperationId ?? $"{method}_{path.Replace("/", "_").Replace("{", "").Replace("}", "").Trim('_')}", false);

                    // Parameters
                    var methodParams = new System.Collections.Generic.List<string>();
                    var queryParams = new System.Collections.Generic.List<string>();
                    var pathParams = new System.Collections.Generic.List<string>();
                    bool hasBody = false;

                    foreach (var param in opKvp.Value.Parameters)
                    {
                        methodParams.Add($"{param.Name}=None");
                        if (param.In == ParameterLocation.Query) queryParams.Add($"'{param.Name}': {param.Name}");
                        else if (param.In == ParameterLocation.Path) pathParams.Add(param.Name);
                    }

                    if (opKvp.Value.RequestBody != null)
                    {
                        methodParams.Add("body=None");
                        hasBody = true;
                    }

                    sb.AppendLine($"    def {operationId}(self, {string.Join(", ", methodParams)}):");
                    
                    // formatting path
                    string pyPath = path;
                    foreach(var p in pathParams)
                    {
                        pyPath = pyPath.Replace("{" + p + "}", $"{{{p}}}");
                    }
                    if (pathParams.Count > 0)
                        sb.AppendLine($"        url = f\"{{self.base_url}}{pyPath}\"");
                    else
                        sb.AppendLine($"        url = f\"{{self.base_url}}{path}\"");

                    string reqArgs = "url";
                    if (queryParams.Count > 0)
                    {
                        sb.AppendLine($"        params = {{{string.Join(", ", queryParams)}}}");
                        reqArgs += ", params=params";
                    }
                    if (hasBody)
                    {
                        reqArgs += ", json=body";
                    }

                    sb.AppendLine($"        response = requests.{method}({reqArgs})");
                    sb.AppendLine($"        response.raise_for_status()");
                    sb.AppendLine($"        return response.json()");
                    sb.AppendLine();
                }
            }

            File.WriteAllText(apiClientPath, sb.ToString());
            _logger(" - frontend/api_client.py généré.");
        }

        private void GenerateTkinterApp()
        {
            var mainPath = Path.Combine(_outputDir, "frontend", "main.py");
            var sb = new StringBuilder();

            sb.AppendLine("import tkinter as tk");
            sb.AppendLine("from tkinter import ttk, messagebox");
            sb.AppendLine("import json");
            sb.AppendLine("from api_client import ApiClient");
            sb.AppendLine();
            sb.AppendLine("class App(tk.Tk):");
            sb.AppendLine("    def __init__(self):");
            sb.AppendLine("        super().__init__()");
            string title = _document.Info?.Title ?? "SDK Client";
            sb.AppendLine($"        self.title(\"{title} - Test Client\")");
            sb.AppendLine("        self.geometry(\"800x600\")");
            sb.AppendLine("        self.api = ApiClient()");
            sb.AppendLine();
            sb.AppendLine("        self.create_widgets()");
            sb.AppendLine();
            sb.AppendLine("    def create_widgets(self):");
            sb.AppendLine("        # Layout principal");
            sb.AppendLine("        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)");
            sb.AppendLine("        paned.pack(fill=tk.BOTH, expand=True)");
            sb.AppendLine();
            sb.AppendLine("        # Liste des endpoints à gauche");
            sb.AppendLine("        left_frame = ttk.Frame(paned)");
            sb.AppendLine("        paned.add(left_frame, weight=1)");
            sb.AppendLine();
            sb.AppendLine("        ttk.Label(left_frame, text=\"Endpoints\", font=(\"Arial\", 12, \"bold\")).pack(pady=5)");
            sb.AppendLine("        self.endpoint_list = tk.Listbox(left_frame)");
            sb.AppendLine("        self.endpoint_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)");
            sb.AppendLine("        self.endpoint_list.bind('<<ListboxSelect>>', self.on_endpoint_select)");
            sb.AppendLine();
            
            var endpoints = new System.Collections.Generic.List<string>();
            foreach (var pathKvp in _document.Paths)
            {
                foreach (var opKvp in pathKvp.Value.Operations)
                {
                    string method = opKvp.Key.ToString().ToUpper();
                    string operationId = NormalizeName(opKvp.Value.OperationId ?? $"{method.ToLower()}_{pathKvp.Key.Replace("/", "_").Replace("{", "").Replace("}", "").Trim('_')}", false);
                    endpoints.Add($"\"{method} {pathKvp.Key}\": \"{operationId}\"");
                }
            }

            sb.AppendLine($"        self.operations = {{{string.Join(", ", endpoints)}}}");
            sb.AppendLine("        for ep in self.operations.keys():");
            sb.AppendLine("            self.endpoint_list.insert(tk.END, ep)");
            sb.AppendLine();

            sb.AppendLine("        # Formulaire à droite");
            sb.AppendLine("        self.right_frame = ttk.Frame(paned)");
            sb.AppendLine("        paned.add(self.right_frame, weight=3)");
            sb.AppendLine();
            sb.AppendLine("        self.form_frame = ttk.LabelFrame(self.right_frame, text=\"Paramètres de la requête\")");
            sb.AppendLine("        self.form_frame.pack(fill=tk.X, padx=5, pady=5)");
            sb.AppendLine();
            sb.AppendLine("        self.btn_send = ttk.Button(self.right_frame, text=\"Envoyer\", command=self.send_request)");
            sb.AppendLine("        self.btn_send.pack(pady=5)");
            sb.AppendLine();
            sb.AppendLine("        self.response_text = tk.Text(self.right_frame, height=20)");
            sb.AppendLine("        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)");
            sb.AppendLine();
            sb.AppendLine("        self.current_params = {}");
            sb.AppendLine("        self.current_operation = None");
            sb.AppendLine();

            sb.AppendLine("    def on_endpoint_select(self, event):");
            sb.AppendLine("        selection = self.endpoint_list.curselection()");
            sb.AppendLine("        if not selection: return");
            sb.AppendLine("        endpoint = self.endpoint_list.get(selection[0])");
            sb.AppendLine("        self.current_operation = self.operations[endpoint]");
            sb.AppendLine();
            sb.AppendLine("        # Vider le formulaire");
            sb.AppendLine("        for widget in self.form_frame.winfo_children():");
            sb.AppendLine("            widget.destroy()");
            sb.AppendLine("        self.current_params = {}");
            sb.AppendLine();
            sb.AppendLine("        # Déterminer si on a besoin de champs texte simples (on demande tout en JSON pour simplifier)");
            sb.AppendLine("        ttk.Label(self.form_frame, text=\"Paramètres / Body (format JSON) :\").pack(anchor=tk.W)");
            sb.AppendLine("        self.param_text = tk.Text(self.form_frame, height=5)");
            sb.AppendLine("        self.param_text.pack(fill=tk.X, expand=True, pady=2)");
            sb.AppendLine("        self.param_text.insert(tk.END, \"{}\")");
            sb.AppendLine();

            sb.AppendLine("    def send_request(self):");
            sb.AppendLine("        if not self.current_operation: return");
            sb.AppendLine("        try:");
            sb.AppendLine("            params = json.loads(self.param_text.get(\"1.0\", tk.END))");
            sb.AppendLine("            func = getattr(self.api, self.current_operation)");
            sb.AppendLine("            res = func(**params)");
            sb.AppendLine("            self.response_text.delete(\"1.0\", tk.END)");
            sb.AppendLine("            self.response_text.insert(tk.END, json.dumps(res, indent=4))");
            sb.AppendLine("        except Exception as e:");
            sb.AppendLine("            messagebox.showerror(\"Erreur\", str(e))");
            sb.AppendLine();

            sb.AppendLine("if __name__ == '__main__':");
            sb.AppendLine("    app = App()");
            sb.AppendLine("    app.mainloop()");

            File.WriteAllText(mainPath, sb.ToString());
            _logger(" - frontend/main.py généré.");
        }

        private string NormalizeName(string name, bool isClass)
        {
            if (string.IsNullOrEmpty(name)) return "Unknown";
            name = name.Replace("-", "_").Replace(".", "_");
            if (isClass)
            {
                var parts = name.Split('_');
                return string.Join("", parts.Select(p => p.Length > 0 ? char.ToUpper(p[0]) + p.Substring(1) : ""));
            }
            return name;
        }
    }
}
