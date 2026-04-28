from flask import Flask
from app.core.config import Config
from app.core.extensions import db, jwt, limiter

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from app.api.v1.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Configure Swagger UI
    from flask_swagger_ui import get_swaggerui_blueprint
    import os
    
    SWAGGER_URL = '/api/docs'
    # We will determine the swagger file name based on what's in the static folder, or assume swagger.yaml/json
    # The generator will copy the openapi file as swagger.yaml or swagger.json
    API_URL = '/static/swagger.yaml' 
    if not os.path.exists(os.path.join(app.root_path, 'static', 'swagger.yaml')) and os.path.exists(os.path.join(app.root_path, 'static', 'swagger.json')):
        API_URL = '/static/swagger.json'
        
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "API Documentation"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Create Database tables
    with app.app_context():
        db.create_all()

    return app