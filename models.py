"""Database Models for Pixel Art Converter"""

import os
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    conversions = db.relationship("Conversion", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username}>"


class Conversion(db.Model):
    __tablename__ = "conversions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    original_filename = db.Column(db.String(256), nullable=False)
    original_size = db.Column(db.Integer)
    original_width = db.Column(db.Integer)
    original_height = db.Column(db.Integer)
    pixel_size = db.Column(db.Integer, default=8)
    palette = db.Column(db.String(50), default="retro")
    settings = db.Column(db.JSON, default={})
    result_filename = db.Column(db.String(256))
    result_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time_ms = db.Column(db.Integer)
    status = db.Column(db.String(20), default="pending")
    error_message = db.Column(db.Text)

    def __repr__(self):
        return f"<Conversion {self.id}: {self.original_filename}>"


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def get_database_url():
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/pixel_art_db",
    )
