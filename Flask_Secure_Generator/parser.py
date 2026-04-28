import yaml
import json
import os

class OpenAPIParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.spec = self._load_spec()

    def _load_spec(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            if self.file_path.endswith('.yaml') or self.file_path.endswith('.yml'):
                return yaml.safe_load(f)
            elif self.file_path.endswith('.json'):
                return json.load(f)
            else:
                raise ValueError("Unsupported file format. Please provide a YAML or JSON file.")

    def get_info(self):
        info = self.spec.get('info', {})
        return {
            'title': info.get('title', 'Generated Flask API'),
            'version': info.get('version', '1.0.0'),
            'description': info.get('description', '')
        }

    def get_models(self):
        """
        Extraire les schémas (modèles) pour générer les classes ORM et CRUD.
        Retourne une liste de dictionnaires avec le nom du modèle et ses champs.
        """
        schemas = self.spec.get('components', {}).get('schemas', {})
        models = []
        
        for name, details in schemas.items():
            # Skip common response models if any, or auth models that we might generate manually
            if name.lower() in ['user', 'login', 'token']:
                continue
                
            properties = details.get('properties', {})
            fields = []
            
            for prop_name, prop_details in properties.items():
                if prop_name == 'id':
                    continue # ID is usually auto-generated
                
                prop_type = prop_details.get('type', 'string')
                format_type = prop_details.get('format', '')
                
                # Mappage OpenAPI types -> SQLAlchemy types (basic)
                sa_type = 'db.String(255)'
                if prop_type == 'integer':
                    sa_type = 'db.Integer'
                elif prop_type == 'number':
                    sa_type = 'db.Float'
                elif prop_type == 'boolean':
                    sa_type = 'db.Boolean'
                elif prop_type == 'string' and format_type == 'date-time':
                    sa_type = 'db.DateTime'
                    
                fields.append({
                    'name': prop_name,
                    'type': prop_type,
                    'sa_type': sa_type
                })
                
            models.append({
                'name': name,
                'fields': fields
            })
            
        return models
