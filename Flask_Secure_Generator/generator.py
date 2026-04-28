import os
import shutil
from jinja2 import Environment, FileSystemLoader
from parser import OpenAPIParser

class FlaskGenerator:
    def __init__(self, openapi_path, output_dir):
        self.openapi_path = openapi_path
        self.output_dir = output_dir
        self.parser = OpenAPIParser(openapi_path)
        
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self):
        # 1. Parse Data
        info = self.parser.get_info()
        models = self.parser.get_models()
        
        # 2. Setup output directories
        app_dir = os.path.join(self.output_dir, 'app')
        api_dir = os.path.join(app_dir, 'api', 'v1')
        core_dir = os.path.join(app_dir, 'core')
        models_dir = os.path.join(app_dir, 'models')
        
        static_dir = os.path.join(app_dir, 'static')
        
        for d in [api_dir, core_dir, models_dir, static_dir]:
            os.makedirs(d, exist_ok=True)
            
        # 3. Generate files
        self._render_template('requirements.txt.j2', os.path.join(self.output_dir, 'requirements.txt'), info=info, models=models)
        self._render_template('run.py.j2', os.path.join(self.output_dir, 'run.py'), info=info, models=models)
        self._render_template('install_and_run.bat.j2', os.path.join(self.output_dir, 'install_and_run.bat'), info=info, models=models)
        self._render_template('frontend.py.j2', os.path.join(self.output_dir, 'frontend_client.py'), info=info, models=models)
        
        # app module
        self._render_template('__init__.py.j2', os.path.join(app_dir, '__init__.py'), info=info, models=models)
        
        # core module
        self._render_template('config.py.j2', os.path.join(core_dir, 'config.py'), info=info, models=models)
        self._render_template('extensions.py.j2', os.path.join(core_dir, 'extensions.py'), info=info, models=models)
        open(os.path.join(core_dir, '__init__.py'), 'w').close()
        
        # models module
        self._render_template('models.py.j2', os.path.join(models_dir, 'models.py'), info=info, models=models)
        open(os.path.join(models_dir, '__init__.py'), 'w').close()
        
        # api/v1 module
        self._render_template('routes.py.j2', os.path.join(api_dir, 'routes.py'), info=info, models=models)
        self._render_template('controllers.py.j2', os.path.join(api_dir, 'controllers.py'), info=info, models=models)
        open(os.path.join(api_dir, '__init__.py'), 'w').close()
        open(os.path.join(app_dir, 'api', '__init__.py'), 'w').close()
        
        # 4. Copy openapi spec for swagger UI
        ext = os.path.splitext(self.openapi_path)[1]
        shutil.copy2(self.openapi_path, os.path.join(static_dir, f'swagger{ext}'))
        
        print(f"Succes: Code genere avec succes dans {self.output_dir}")

    def _render_template(self, template_name, output_path, **context):
        template = self.env.get_template(template_name)
        content = template.render(**context)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
