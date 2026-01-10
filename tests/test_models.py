"""
Tests for Database Models

Tests the User and Conversion models.
"""

import pytest
from datetime import datetime


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, app):
        """Test creating a new user."""
        from app.models import db, User
        
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='securepassword'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.is_active is True
    
    def test_password_hashing(self, app):
        """Test that password is hashed."""
        from app.models import User
        
        with app.app_context():
            user = User(
                username='hashtest',
                email='hash@example.com',
                password='mypassword'
            )
            
            # Password should be hashed, not stored as plaintext
            assert user.password_hash != 'mypassword'
            assert len(user.password_hash) > 20
    
    def test_password_verification(self, app):
        """Test password verification."""
        from app.models import User
        
        with app.app_context():
            user = User(
                username='verifytest',
                email='verify@example.com',
                password='correctpassword'
            )
            
            assert user.check_password('correctpassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_to_dict(self, app):
        """Test user serialization."""
        from app.models import db, User
        
        with app.app_context():
            user = User(
                username='dicttest',
                email='dict@example.com',
                password='password'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            assert user_dict['username'] == 'dicttest'
            assert user_dict['email'] == 'dict@example.com'
            assert 'password' not in user_dict
            assert 'password_hash' not in user_dict
    
    def test_user_repr(self, app):
        """Test user string representation."""
        from app.models import User
        
        with app.app_context():
            user = User(
                username='reprtest',
                email='repr@example.com',
                password='password'
            )
            
            assert 'reprtest' in repr(user)


class TestConversionModel:
    """Test cases for Conversion model."""
    
    def test_create_conversion(self, app):
        """Test creating a conversion record."""
        from app.models import db, Conversion
        
        with app.app_context():
            conversion = Conversion(
                original_filename='test.png',
                output_filename='test_pixel.png',
                original_width=100,
                original_height=100,
                output_width=100,
                output_height=100,
                pixel_size=10,
                color_count=16,
                processing_time_ms=50.5
            )
            db.session.add(conversion)
            db.session.commit()
            
            assert conversion.id is not None
            assert conversion.original_filename == 'test.png'
            assert conversion.processing_time_ms == 50.5
    
    def test_conversion_with_user(self, app):
        """Test conversion associated with user."""
        from app.models import db, User, Conversion
        
        with app.app_context():
            # Create user
            user = User(
                username='convuser',
                email='conv@example.com',
                password='password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create conversion
            conversion = Conversion(
                user_id=user.id,
                original_filename='user_image.png',
                output_filename='user_image_pixel.png',
                original_width=200,
                original_height=200,
                output_width=200,
                output_height=200
            )
            db.session.add(conversion)
            db.session.commit()
            
            # Check relationship
            assert len(user.conversions) == 1
            assert user.conversions[0].original_filename == 'user_image.png'
    
    def test_conversion_to_dict(self, app):
        """Test conversion serialization."""
        from app.models import db, Conversion
        
        with app.app_context():
            conversion = Conversion(
                original_filename='dict.png',
                output_filename='dict_pixel.png',
                original_width=50,
                original_height=50,
                output_width=50,
                output_height=50,
                pixel_size=5,
                color_count=8
            )
            db.session.add(conversion)
            db.session.commit()
            
            conv_dict = conversion.to_dict()
            
            assert conv_dict['original_filename'] == 'dict.png'
            assert conv_dict['original_size'] == '50x50'
            assert conv_dict['pixel_size'] == 5
    
    def test_conversion_timestamp(self, app):
        """Test that timestamp is set automatically."""
        from app.models import db, Conversion
        
        with app.app_context():
            conversion = Conversion(
                original_filename='time.png',
                output_filename='time_pixel.png',
                original_width=10,
                original_height=10,
                output_width=10,
                output_height=10
            )
            db.session.add(conversion)
            db.session.commit()
            
            assert conversion.created_at is not None
            assert isinstance(conversion.created_at, datetime)


class TestDatabaseIntegrity:
    """Test database integrity constraints."""
    
    def test_unique_username(self, app):
        """Test that username must be unique."""
        from app.models import db, User
        from sqlalchemy.exc import IntegrityError
        
        with app.app_context():
            user1 = User(
                username='unique',
                email='unique1@example.com',
                password='password'
            )
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(
                username='unique',
                email='unique2@example.com',
                password='password'
            )
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_unique_email(self, app):
        """Test that email must be unique."""
        from app.models import db, User
        from sqlalchemy.exc import IntegrityError
        
        with app.app_context():
            user1 = User(
                username='emailtest1',
                email='same@example.com',
                password='password'
            )
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(
                username='emailtest2',
                email='same@example.com',
                password='password'
            )
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
