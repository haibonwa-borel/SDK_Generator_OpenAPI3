from werkzeug.security import generate_password_hash, check_password_hash
from app.core.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(255))
    
    price = db.Column(db.Float)
    
    in_stock = db.Column(db.Boolean)
    

    def to_dict(self):
        return {
            'id': self.id,
            
            'name': self.name,
            
            'price': self.price,
            
            'in_stock': self.in_stock,
            
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    title = db.Column(db.String(255))
    
    description = db.Column(db.String(255))
    

    def to_dict(self):
        return {
            'id': self.id,
            
            'title': self.title,
            
            'description': self.description,
            
        }
