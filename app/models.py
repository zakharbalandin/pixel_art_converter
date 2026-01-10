"""
Database Models

This module defines the database models for the Pixel Art Converter application.
Uses SQLAlchemy for ORM with PostgreSQL support.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and tracking conversions."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to conversions
    conversions = db.relationship('Conversion', backref='user', lazy=True)
    
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password: str):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'conversion_count': len(self.conversions)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Conversion(db.Model):
    """Model to track image conversions."""
    
    __tablename__ = 'conversions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    output_filename = db.Column(db.String(255), nullable=False)
    original_width = db.Column(db.Integer)
    original_height = db.Column(db.Integer)
    output_width = db.Column(db.Integer)
    output_height = db.Column(db.Integer)
    pixel_size = db.Column(db.Integer, default=10)
    color_count = db.Column(db.Integer, default=16)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time_ms = db.Column(db.Float)
    
    def to_dict(self) -> dict:
        """Convert conversion record to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'output_filename': self.output_filename,
            'original_size': f"{self.original_width}x{self.original_height}",
            'output_size': f"{self.output_width}x{self.output_height}",
            'pixel_size': self.pixel_size,
            'color_count': self.color_count,
            'created_at': self.created_at.isoformat(),
            'processing_time_ms': self.processing_time_ms
        }
    
    def __repr__(self):
        return f'<Conversion {self.id}: {self.original_filename}>'


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
