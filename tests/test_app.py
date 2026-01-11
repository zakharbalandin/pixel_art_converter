"""Tests for the Flask web application"""

import io

import pytest
from PIL import Image


class TestIndexPage:
    """Test index page functionality"""

    def test_index_loads(self, client):
        """Test that index page loads"""
        response = client.get("/")
        assert response.status_code == 200

    def test_api_palettes(self, client):
        """Test palettes API endpoint"""
        response = client.get("/api/palettes")
        assert response.status_code == 200
        json_data = response.get_json()
        assert "palettes" in json_data


class TestConversion:
    """Test image conversion functionality"""

    def test_convert_no_file(self, client):
        """Test conversion without file"""
        response = client.post("/convert", data={}, content_type="multipart/form-data")
        assert response.status_code == 400

    def test_convert_image(self, client, sample_image):
        """Test successful image conversion"""
        data = {
            "image": (sample_image, "test.png"),
            "pixel_size": "8",
            "palette": "retro",
        }
        response = client.post(
            "/convert", data=data, content_type="multipart/form-data"
        )
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["success"] is True


class TestErrorHandling:
    """Test error handling"""

    def test_404_error(self, client):
        """Test 404 error page"""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
