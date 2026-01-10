"""Pytest configuration and fixtures"""

import io
import os
import sys
import tempfile

import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import Conversion, User, db


@pytest.fixture
def app():
    """Create application for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "UPLOAD_FOLDER": os.path.join(tmpdir, "uploads"),
            "RESULT_FOLDER": os.path.join(tmpdir, "results"),
        }

        app = create_app(config)

        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_rgba_image():
    """Create a sample RGBA image for testing"""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@pytest.fixture
def authenticated_client(client, app):
    """Create an authenticated test client"""
    with app.app_context():
        from werkzeug.security import generate_password_hash

        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpass123"),
        )
        db.session.add(user)
        db.session.commit()

        with client.session_transaction() as sess:
            sess["user_id"] = user.id

        yield client
