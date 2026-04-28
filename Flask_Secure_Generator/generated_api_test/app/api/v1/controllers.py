from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from app.core.extensions import db
from app.models.models import User

from app.models.models import Product

from app.models.models import Category


class AuthController:
    @staticmethod
    def register():
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'msg': 'Missing username or password'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'msg': 'Username already exists'}), 400

        user = User(username=data['username'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'msg': 'User created successfully'}), 201

    @staticmethod
    def login():
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'msg': 'Missing username or password'}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'msg': 'Bad username or password'}), 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh():
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return jsonify(access_token=access_token)

    @staticmethod
    def get_me():
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        return jsonify(user.to_dict())


class ProductController:
    @staticmethod
    def get_all():
        items = Product.query.all()
        return jsonify([item.to_dict() for item in items])

    @staticmethod
    def get_by_id(id):
        item = Product.query.get_or_404(id)
        return jsonify(item.to_dict())

    @staticmethod
    def create():
        data = request.get_json()
        item = Product()
        
        if 'name' in data:
            item.name = data['name']
        
        if 'price' in data:
            item.price = data['price']
        
        if 'in_stock' in data:
            item.in_stock = data['in_stock']
        
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

    @staticmethod
    def update(id):
        item = Product.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            item.name = data['name']
        
        if 'price' in data:
            item.price = data['price']
        
        if 'in_stock' in data:
            item.in_stock = data['in_stock']
        
        db.session.commit()
        return jsonify(item.to_dict())

    @staticmethod
    def delete(id):
        item = Product.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

class CategoryController:
    @staticmethod
    def get_all():
        items = Category.query.all()
        return jsonify([item.to_dict() for item in items])

    @staticmethod
    def get_by_id(id):
        item = Category.query.get_or_404(id)
        return jsonify(item.to_dict())

    @staticmethod
    def create():
        data = request.get_json()
        item = Category()
        
        if 'title' in data:
            item.title = data['title']
        
        if 'description' in data:
            item.description = data['description']
        
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

    @staticmethod
    def update(id):
        item = Category.query.get_or_404(id)
        data = request.get_json()
        
        if 'title' in data:
            item.title = data['title']
        
        if 'description' in data:
            item.description = data['description']
        
        db.session.commit()
        return jsonify(item.to_dict())

    @staticmethod
    def delete(id):
        item = Category.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204
