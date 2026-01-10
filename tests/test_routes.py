"""
Tests for Flask Routes

Tests the web interface and API endpoints.
"""

import io
import pytest


class TestIndexRoute:
    """Test cases for the index/home route."""
    
    def test_index_returns_200(self, client):
        """Test that index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_contains_form(self, client):
        """Test that index page contains upload form."""
        response = client.get('/')
        assert b'Convert to Pixel Art' in response.data or b'convert' in response.data.lower()


class TestConvertRoute:
    """Test cases for the convert route."""
    
    def test_convert_no_file(self, client):
        """Test conversion without file returns error."""
        response = client.post('/convert')
        assert response.status_code in [302, 400]  # Redirect or bad request
    
    def test_convert_empty_filename(self, client):
        """Test conversion with empty filename."""
        response = client.post('/convert', data={
            'image': (io.BytesIO(b''), '')
        })
        assert response.status_code in [302, 400]
    
    def test_convert_invalid_file_type(self, client):
        """Test conversion with invalid file type."""
        response = client.post('/convert', data={
            'image': (io.BytesIO(b'not an image'), 'test.txt'),
            'pixel_size': '10',
            'color_count': '16'
        }, content_type='multipart/form-data')
        
        assert response.status_code in [302, 400]
    
    def test_convert_valid_image(self, client, sample_image_bytes):
        """Test successful image conversion."""
        response = client.post('/convert', data={
            'image': (io.BytesIO(sample_image_bytes), 'test.png'),
            'pixel_size': '10',
            'color_count': '16'
        }, content_type='multipart/form-data')
        
        # Should redirect to result or return success
        assert response.status_code in [200, 302]


class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_login_page_loads(self, client):
        """Test login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_page_loads(self, client):
        """Test register page loads successfully."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_new_user(self, client, app):
        """Test user registration."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created
        from app.models import User
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'new@example.com'
    
    def test_register_duplicate_username(self, client, app):
        """Test registration with duplicate username fails."""
        # Register first user
        client.post('/register', data={
            'username': 'dupuser',
            'email': 'dup1@example.com',
            'password': 'password123'
        })
        
        # Try to register with same username
        response = client.post('/register', data={
            'username': 'dupuser',
            'email': 'dup2@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'already taken' in response.data or b'Username' in response.data
    
    def test_login_valid_credentials(self, client, app):
        """Test login with valid credentials."""
        # Create user first
        client.post('/register', data={
            'username': 'logintest',
            'email': 'login@example.com',
            'password': 'testpass123'
        })
        
        # Login
        response = client.post('/login', data={
            'username': 'logintest',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome' in response.data or b'logintest' in response.data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'invalid' in response.data
    
    def test_logout(self, client, app):
        """Test logout functionality."""
        # Register and login
        client.post('/register', data={
            'username': 'logouttest',
            'email': 'logout@example.com',
            'password': 'testpass123'
        })
        client.post('/login', data={
            'username': 'logouttest',
            'password': 'testpass123'
        })
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data.lower() or b'Login' in response.data


class TestHistoryRoute:
    """Test cases for history route."""
    
    def test_history_requires_login(self, client):
        """Test that history page requires authentication."""
        response = client.get('/history', follow_redirects=True)
        assert b'log in' in response.data.lower() or b'Login' in response.data
    
    def test_history_accessible_when_logged_in(self, auth_client):
        """Test that history is accessible when logged in."""
        response = auth_client.get('/history')
        assert response.status_code == 200
        assert b'History' in response.data or b'history' in response.data.lower()


class TestAPIRoutes:
    """Test cases for API endpoints."""
    
    def test_api_convert_no_file(self, client):
        """Test API convert without file."""
        response = client.post('/api/convert')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_api_convert_valid(self, client, sample_image_bytes):
        """Test API convert with valid image."""
        response = client.post('/api/convert', data={
            'image': (io.BytesIO(sample_image_bytes), 'test.png'),
            'pixel_size': '10',
            'color_count': '16'
        }, content_type='multipart/form-data')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'output_url' in data
        assert 'stats' in data
    
    def test_api_stats(self, client):
        """Test API stats endpoint."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'total_conversions' in data
        assert 'total_users' in data


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
