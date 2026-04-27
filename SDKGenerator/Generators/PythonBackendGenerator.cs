using Microsoft.OpenApi.Models;
using System;
using System.IO;
using System.Linq;
using System.Text;

namespace SDKGenerator.Generators
{
    public class PythonBackendGenerator
    {
        private readonly OpenApiDocument _document;
        private readonly string _outputDir;
        private readonly Action<string> _logger;

        public PythonBackendGenerator(OpenApiDocument document, string outputDir, Action<string> logger)
        {
            _document = document;
            _outputDir = outputDir;
            _logger = logger;
        }

        public void Generate()
        {
            GenerateSchemas();
            GenerateMain();
        }

        private void GenerateSchemas()
        {
            var schemasPath = Path.Combine(_outputDir, "backend", "schemas.py");
            var sb = new StringBuilder();

            sb.AppendLine("from pydantic import BaseModel");
            sb.AppendLine("from typing import List, Optional, Any");
            sb.AppendLine();

            if (_document.Components?.Schemas != null)
            {
                foreach (var schemaKvp in _document.Components.Schemas)
                {
                    string className = NormalizeName(schemaKvp.Key, true);
                    var schema = schemaKvp.Value;

                    sb.AppendLine($"class {className}(BaseModel):");

                    if (schema.Properties != null && schema.Properties.Count > 0)
                    {
                        foreach (var propKvp in schema.Properties)
                        {
                            string propName = propKvp.Key;
                            string pyType = GetPythonType(propKvp.Value);
                            bool isRequired = schema.Required?.Contains(propName) == true;

                            if (isRequired)
                            {
                                sb.AppendLine($"    {propName}: {pyType}");
                            }
                            else
                            {
                                sb.AppendLine($"    {propName}: Optional[{pyType}] = None");
                            }
                        }
                    }
                    else
                    {
                        sb.AppendLine("    pass");
                    }
                    sb.AppendLine();
                }
            }

            File.WriteAllText(schemasPath, sb.ToString());
            _logger(" - backend/schemas.py généré.");
        }

        private void GenerateMain()
        {
            var mainPath = Path.Combine(_outputDir, "backend", "main.py");
            var sb = new StringBuilder();

            sb.AppendLine("from fastapi import FastAPI, HTTPException");
            sb.AppendLine("from fastapi.middleware.cors import CORSMiddleware");
            sb.AppendLine("import schemas");
            sb.AppendLine("from typing import List, Optional, Any");
            sb.AppendLine();
            
            string title = _document.Info?.Title ?? "API";
            string version = _document.Info?.Version ?? "1.0.0";
            
            sb.AppendLine($"app = FastAPI(title=\"{title}\", version=\"{version}\")");
            sb.AppendLine();
            sb.AppendLine("app.add_middleware(");
            sb.AppendLine("    CORSMiddleware,");
            sb.AppendLine("    allow_origins=[\"*\"],");
            sb.AppendLine("    allow_credentials=True,");
            sb.AppendLine("    allow_methods=[\"*\"],");
            sb.AppendLine("    allow_headers=[\"*\"],");
            sb.AppendLine(")");
            sb.AppendLine();

            foreach (var pathKvp in _document.Paths)
            {
                string path = pathKvp.Key;
                // FastAPI uses {param} for path variables, which matches OpenAPI
                string fastApiPath = path.Replace("{", "{").Replace("}", "}"); 

                foreach (var opKvp in pathKvp.Value.Operations)
                {
                    string method = opKvp.Key.ToString().ToLower();
                    string operationId = opKvp.Value.OperationId ?? $"{method}_{path.Replace("/", "_").Replace("{", "").Replace("}", "").Trim('_')}";
                    operationId = NormalizeName(operationId, false);

                    string responseModel = "Any";
                    // Try to guess response model
                    if (opKvp.Value.Responses.TryGetValue("200", out var response) || opKvp.Value.Responses.TryGetValue("201", out response))
                    {
                        if (response.Content.TryGetValue("application/json", out var mediaType))
                        {
                            if (mediaType.Schema?.Reference != null)
                            {
                                responseModel = "schemas." + NormalizeName(mediaType.Schema.Reference.Id, true);
                            }
                            else if (mediaType.Schema?.Type == "array" && mediaType.Schema.Items?.Reference != null)
                            {
                                responseModel = "List[schemas." + NormalizeName(mediaType.Schema.Items.Reference.Id, true) + "]";
                            }
                        }
                    }

                    sb.AppendLine($"@app.{method}(\"{fastApiPath}\", response_model={responseModel})");
                    
                    // Parameters
                    var methodParams = new System.Collections.Generic.List<string>();
                    
                    // Path and Query parameters
                    foreach (var param in opKvp.Value.Parameters)
                    {
                        string paramType = GetPythonType(param.Schema);
                        string paramDef = $"{param.Name}: {paramType}";
                        if (!param.Required) paramDef += " = None";
                        methodParams.Add(paramDef);
                    }

                    // Request body
                    if (opKvp.Value.RequestBody != null && opKvp.Value.RequestBody.Content.TryGetValue("application/json", out var reqBody))
                    {
                        if (reqBody.Schema?.Reference != null)
                        {
                            string reqModel = "schemas." + NormalizeName(reqBody.Schema.Reference.Id, true);
                            methodParams.Add($"body: {reqModel}");
                        }
                    }

                    sb.AppendLine($"async def {operationId}({string.Join(", ", methodParams)}):");
                    
                    // Mock implementation
                    sb.AppendLine($"    # Mock implementation for {method.ToUpper()} {path}");
                    if (method == "get")
                    {
                        if (responseModel.StartsWith("List["))
                        {
                            sb.AppendLine("    return []");
                        }
                        else if (responseModel != "Any")
                        {
                            sb.AppendLine($"    return {responseModel}()");
                        }
                        else
                        {
                            sb.AppendLine("    return {\"message\": \"Mocked response\"}");
                        }
                    }
                    else if (method == "post" || method == "put" || method == "patch")
                    {
                         sb.AppendLine("    return {\"status\": \"success\", \"message\": \"Resource created/updated\"}");
                    }
                    else if (method == "delete")
                    {
                         sb.AppendLine("    return {\"status\": \"success\", \"message\": \"Resource deleted\"}");
                    }
                    
                    sb.AppendLine();
                }
            }

            File.WriteAllText(mainPath, sb.ToString());
            _logger(" - backend/main.py généré.");
        }

        private string GetPythonType(OpenApiSchema schema)
        {
            if (schema == null) return "Any";
            if (schema.Reference != null) return "schemas." + NormalizeName(schema.Reference.Id, true);

            switch (schema.Type)
            {
                case "string": return "str";
                case "integer": return "int";
                case "number": return "float";
                case "boolean": return "bool";
                case "array":
                    return $"List[{GetPythonType(schema.Items)}]";
                default:
                    return "Any";
            }
        }

        private string NormalizeName(string name, bool isClass)
        {
            if (string.IsNullOrEmpty(name)) return "Unknown";
            name = name.Replace("-", "_").Replace(".", "_");
            if (isClass)
            {
                // PascalCase
                var parts = name.Split('_');
                return string.Join("", parts.Select(p => p.Length > 0 ? char.ToUpper(p[0]) + p.Substring(1) : ""));
            }
            return name;
        }
    }
}
