"""Tests for the pixel art converter module"""
import pytest
from PIL import Image
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter import PixelArtConverter


class TestPixelArtConverter:
    """Test suite for PixelArtConverter class"""
    
    def test_initialization_default(self):
        """Test default initialization"""
        converter = PixelArtConverter()
        assert converter.pixel_size == 8
        assert converter.palette_name == 'retro'
    
    def test_initialization_custom(self):
        """Test custom initialization"""
        converter = PixelArtConverter(pixel_size=16, palette='gameboy')
        assert converter.pixel_size == 16
        assert converter.palette_name == 'gameboy'
    
    def test_pixel_size_clamping(self):
        """Test pixel size is clamped to valid range"""
        converter_min = PixelArtConverter(pixel_size=0)
        converter_max = PixelArtConverter(pixel_size=100)
        assert converter_min.pixel_size == 1
        assert converter_max.pixel_size == 64
    
    def test_convert_rgb_image(self):
        """Test converting an RGB image"""
        converter = PixelArtConverter(pixel_size=8, palette='retro')
        img = Image.new('RGB', (100, 100), color='red')
        result = converter.convert(img)
        assert result.size == (100, 100)
        assert result.mode == 'RGB'
    
    def test_convert_rgba_image(self):
        """Test converting an RGBA image preserves alpha"""
        converter = PixelArtConverter(pixel_size=8, palette='retro')
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        result = converter.convert(img)
        assert result.size == (100, 100)
        assert result.mode == 'RGBA'
    
    def test_convert_grayscale_image(self):
        """Test converting a grayscale image"""
        converter = PixelArtConverter(pixel_size=8, palette='grayscale')
        img = Image.new('L', (100, 100), color=128)
        result = converter.convert(img)
        assert result.size == (100, 100)
    
    def test_original_palette(self):
        """Test original palette (no color reduction)"""
        converter = PixelArtConverter(pixel_size=8, palette='original')
        img = Image.new('RGB', (100, 100), color='blue')
        result = converter.convert(img)
        assert result.size == (100, 100)
    
    def test_available_palettes(self):
        """Test getting available palettes"""
        palettes = PixelArtConverter.get_available_palettes()
        assert 'gameboy' in palettes
        assert 'nes' in palettes
        assert 'grayscale' in palettes
        assert 'retro' in palettes
        assert 'original' in palettes
    
    def test_convert_from_bytes(self):
        """Test converting from bytes"""
        converter = PixelArtConverter(pixel_size=8, palette='retro')
        img = Image.new('RGB', (100, 100), color='green')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        result_bytes = converter.convert_from_bytes(buffer.getvalue())
        result_img = Image.open(io.BytesIO(result_bytes))
        assert result_img.size == (100, 100)
    
    def test_output_size(self):
        """Test custom output size"""
        converter = PixelArtConverter(pixel_size=8, palette='retro')
        img = Image.new('RGB', (100, 100), color='red')
        result = converter.convert(img, output_size=(200, 200))
        assert result.size == (200, 200)
    
    def test_find_closest_color(self):
        """Test color matching"""
        converter = PixelArtConverter(palette='gameboy')
        color = (50, 100, 50)
        closest = converter._find_closest_color(color, converter.palette)
        assert isinstance(closest, tuple)
        assert len(closest) == 3


class TestConverterEdgeCases:
    """Test edge cases for converter"""
    
    def test_very_small_image(self):
        """Test converting a very small image"""
        converter = PixelArtConverter(pixel_size=8)
        img = Image.new('RGB', (4, 4), color='red')
        result = converter.convert(img)
        assert result.size == (4, 4)
    
    def test_large_pixel_size(self):
        """Test with pixel size larger than image"""
        converter = PixelArtConverter(pixel_size=50)
        img = Image.new('RGB', (30, 30), color='blue')
        result = converter.convert(img)
        assert result.size == (30, 30)
    
    def test_non_square_image(self):
        """Test non-square image"""
        converter = PixelArtConverter(pixel_size=8)
        img = Image.new('RGB', (200, 100), color='green')
        result = converter.convert(img)
        assert result.size == (200, 100)
    
    def test_all_palettes(self):
        """Test all palettes produce valid output"""
        img = Image.new('RGB', (50, 50), color='purple')
        for palette in PixelArtConverter.get_available_palettes():
            converter = PixelArtConverter(pixel_size=8, palette=palette)
            result = converter.convert(img)
            assert result.size == (50, 50)
