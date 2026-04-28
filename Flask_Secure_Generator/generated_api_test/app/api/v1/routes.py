from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.core.extensions import limiter
from .controllers import AuthController

from .controllers import ProductController

from .controllers import CategoryController


api_bp = Blueprint('api', __name__)

# Auth Routes
@api_bp.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    return AuthController.register()

@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    return AuthController.login()

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    return AuthController.refresh()

@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    return AuthController.get_me()


# Product CRUD Routes
@api_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    return ProductController.get_all()

@api_bp.route('/products/<int:id>', methods=['GET'])
@jwt_required()
def get_product(id):
    return ProductController.get_by_id(id)

@api_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    return ProductController.create()

@api_bp.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    return ProductController.update(id)

@api_bp.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    return ProductController.delete(id)

# Category CRUD Routes
@api_bp.route('/categorys', methods=['GET'])
@jwt_required()
def get_categorys():
    return CategoryController.get_all()

@api_bp.route('/categorys/<int:id>', methods=['GET'])
@jwt_required()
def get_category(id):
    return CategoryController.get_by_id(id)

@api_bp.route('/categorys', methods=['POST'])
@jwt_required()
def create_category():
    return CategoryController.create()

@api_bp.route('/categorys/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    return CategoryController.update(id)

@api_bp.route('/categorys/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    return CategoryController.delete(id)
