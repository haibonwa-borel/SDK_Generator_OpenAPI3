using Microsoft.OpenApi.Models;
using Microsoft.OpenApi.Readers;
using System;
using System.IO;

namespace SDKGenerator.Generators
{
    public class SdkGeneratorEngine
    {
        private readonly string _inputFilePath;
        private readonly string _outputDir;
        private readonly string _sdkName;
        private readonly Action<string> _logger;

        public SdkGeneratorEngine(string inputFilePath, string outputDir, string sdkName, Action<string> logger)
        {
            _inputFilePath = inputFilePath;
            _outputDir = outputDir;
            _sdkName = sdkName;
            _logger = logger;
        }

        public void Generate()
        {
            _logger("Lecture du fichier OpenAPI...");
            using var stream = File.OpenRead(_inputFilePath);
            var reader = new OpenApiStreamReader();
            var document = reader.Read(stream, out var diagnostic);

            if (diagnostic.Errors.Count > 0)
            {
                foreach (var error in diagnostic.Errors)
                {
                    _logger($"Erreur OpenAPI : {error.Message}");
                }
                throw new Exception("Le fichier OpenAPI contient des erreurs.");
            }

            _logger($"API chargée : {document.Info?.Title ?? "Sans Titre"} v{document.Info?.Version ?? "1.0"}");
            _logger($"Endpoints trouvés : {document.Paths.Count}");

            // Créer la structure de dossiers
            Directory.CreateDirectory(_outputDir);
            Directory.CreateDirectory(Path.Combine(_outputDir, "backend"));
            Directory.CreateDirectory(Path.Combine(_outputDir, "frontend"));

            _logger("Génération du Backend FastAPI...");
            var backendGen = new PythonBackendGenerator(document, _outputDir, _logger);
            backendGen.Generate();

            _logger("Génération du Frontend Tkinter...");
            var frontendGen = new PythonFrontendGenerator(document, _outputDir, _logger);
            frontendGen.Generate();

            _logger("Génération des fichiers racines (requirements.txt, run.bat)...");
            GenerateRootFiles();

            _logger("=== Génération terminée ! ===");
        }

        private void GenerateRootFiles()
        {
            // requirements.txt
            string reqPath = Path.Combine(_outputDir, "requirements.txt");
            File.WriteAllText(reqPath, "fastapi\nuvicorn\npydantic\nrequests\nhttpx\n");
            _logger(" - requirements.txt généré.");

            // run.bat
            string batPath = Path.Combine(_outputDir, "run.bat");
            string batContent = @"@echo off
echo ==============================================
echo Demarrage du SDK %SDK_NAME%
echo ==============================================
echo 1. Installation des dependances...
pip install -r requirements.txt

echo 2. Demarrage du Backend FastAPI (en arriere-plan)...
start cmd /k ""uvicorn backend.main:app --reload""

echo Patientez 3 secondes pour que le serveur demarre...
timeout /t 3 >nul

echo 3. Demarrage du Frontend Tkinter...
python frontend/main.py
".Replace("%SDK_NAME%", _sdkName);
            File.WriteAllText(batPath, batContent);
            _logger(" - run.bat généré.");
        }
    }
}
