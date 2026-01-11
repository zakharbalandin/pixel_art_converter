"""Tests for the pixel art converter module"""

import io
import os
import sys

import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter import PixelArtConverter


class TestPixelArtConverter:
    """Test suite for PixelArtConverter class"""

    def test_initialization_default(self):
        """Test default initialization"""
        converter = PixelArtConverter()
        assert converter.pixel_size == 8
        assert converter.palette_name == "retro"

    def test_pixel_size_clamping(self):
        """Test pixel size is clamped to valid range"""
        converter_min = PixelArtConverter(pixel_size=0)
        converter_max = PixelArtConverter(pixel_size=100)
        assert converter_min.pixel_size == 1
        assert converter_max.pixel_size == 64

    def test_convert_rgb_image(self):
        """Test converting an RGB image"""
        converter = PixelArtConverter(pixel_size=8, palette="retro")
        img = Image.new("RGB", (100, 100), color="red")
        result = converter.convert(img)
        assert result.size == (100, 100)
        assert result.mode == "RGB"

    def test_convert_rgba_image(self):
        """Test converting an RGBA image preserves alpha"""
        converter = PixelArtConverter(pixel_size=8, palette="retro")
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        result = converter.convert(img)
        assert result.size == (100, 100)
        assert result.mode == "RGBA"

    def test_available_palettes(self):
        """Test getting available palettes"""
        palettes = PixelArtConverter.get_available_palettes()
        assert "gameboy" in palettes
        assert "retro" in palettes
        assert "original" in palettes

    def test_convert_from_bytes(self):
        """Test converting from bytes"""
        converter = PixelArtConverter(pixel_size=8, palette="retro")
        img = Image.new("RGB", (100, 100), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        result_bytes = converter.convert_from_bytes(buffer.getvalue())
        result_img = Image.open(io.BytesIO(result_bytes))
        assert result_img.size == (100, 100)
