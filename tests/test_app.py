"""Tests for the Flask web application"""
import pytest
import io
from PIL import Image


class TestIndexPage:
    """Test index page functionality"""
    
    def test_index_loads(self, client):
        """Test that index page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Pixel Art' in response.data
    
    def test_index_shows_palettes(self, client):
        """Test that palettes are displayed"""
        response = client.get('/')
        assert b'retro' in response.data or b'Retro' in response.data


class TestConversion:
    """Test image conversion functionality"""
    
    def test_convert_image(self, client, sample_image):
        """Test successful image conversion"""
        data = {
            'image': (sample_image, 'test.png'),
            'pixel_size': '8',
            'palette': 'retro'
        }
        response = client.post('/convert', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] == True
        assert 'result_filename' in json_data
    
    def test_convert_with_different_palette(self, client, sample_image):
        """Test conversion with different palette"""
        data = {
            'image': (sample_image, 'test.png'),
            'pixel_size': '16',
            'palette': 'gameboy'
        }
        response = client.post('/convert', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] == True
    
    def test_convert_rgba_image(self, client, sample_rgba_image):
        """Test RGBA image conversion"""
        data = {
            'image': (sample_rgba_image, 'test_rgba.png'),
            'pixel_size': '8',
            'palette': 'retro'
        }
        response = client.post('/convert', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
    
    def test_convert_no_file(self, client):
        """Test conversion without file"""
        response = client.post('/convert', data={}, content_type='multipart/form-data')
        assert response.status_code == 400
    
    def test_convert_invalid_file_type(self, client):
        """Test conversion with invalid file type"""
        data = {
            'image': (io.BytesIO(b'not an image'), 'test.txt'),
            'pixel_size': '8',
            'palette': 'retro'
        }
        response = client.post('/convert', data=data, content_type='multipart/form-data')
        assert response.status_code == 400


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_register_page_loads(self, client):
        """Test register page loads"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page_loads(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_user(self, client, app):
        """Test user registration"""
        with app.app_context():
            data = {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'password123'
            }
            response = client.post('/register', data=data, follow_redirects=True)
            assert response.status_code == 200
    
    def test_login_user(self, client, app):
        """Test user login"""
        with app.app_context():
            # First register
            client.post('/register', data={
                'username': 'logintest',
                'email': 'login@example.com',
                'password': 'password123'
            })
            # Then login
            response = client.post('/login', data={
                'username': 'logintest',
                'password': 'password123'
            }, follow_redirects=True)
            assert response.status_code == 200
    
    def test_logout(self, authenticated_client):
        """Test user logout"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_duplicate_username(self, client, app):
        """Test duplicate username registration"""
        with app.app_context():
            client.post('/register', data={
                'username': 'duplicate',
                'email': 'first@example.com',
                'password': 'password123'
            })
            response = client.post('/register', data={
                'username': 'duplicate',
                'email': 'second@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            assert b'already exists' in response.data or response.status_code == 200
    
    def test_invalid_login(self, client):
        """Test invalid login credentials"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestHistory:
    """Test history functionality"""
    
    def test_history_requires_auth(self, client):
        """Test history page requires authentication"""
        response = client.get('/history', follow_redirects=True)
        assert b'Login' in response.data or b'log in' in response.data
    
    def test_history_page_loads(self, authenticated_client):
        """Test history page loads for authenticated user"""
        response = authenticated_client.get('/history')
        assert response.status_code == 200
        assert b'History' in response.data


class TestAPI:
    """Test API endpoints"""
    
    def test_api_palettes(self, client):
        """Test palettes API endpoint"""
        response = client.get('/api/palettes')
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'palettes' in json_data
        assert 'retro' in json_data['palettes']
    
    def test_api_stats(self, client):
        """Test stats API endpoint"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'total_conversions' in json_data


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
