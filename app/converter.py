"""
Pixel Art Converter Module

This module provides functionality to convert regular images to pixel art
by reducing resolution and applying color quantization.
"""

from PIL import Image
import os
from typing import Tuple, Optional


class PixelArtConverter:
    """
    A class to convert regular images to pixel art style.
    
    Attributes:
        pixel_size: The size of each "pixel" block in the output
        color_count: Number of colors to use in the output
    """
    
    def __init__(self, pixel_size: int = 10, color_count: int = 16):
        """
        Initialize the PixelArtConverter.
        
        Args:
            pixel_size: Size of each pixel block (default: 10)
            color_count: Number of colors for quantization (default: 16)
        """
        if pixel_size < 1:
            raise ValueError("Pixel size must be at least 1")
        if color_count < 2 or color_count > 256:
            raise ValueError("Color count must be between 2 and 256")
            
        self.pixel_size = pixel_size
        self.color_count = color_count
    
    def convert(self, input_path: str, output_path: str, 
                output_size: Optional[Tuple[int, int]] = None) -> dict:
        """
        Convert an image to pixel art.
        
        Args:
            input_path: Path to the input image
            output_path: Path where the output will be saved
            output_size: Optional tuple (width, height) for output size
            
        Returns:
            dict: Conversion statistics
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Open and convert to RGB
        with Image.open(input_path) as img:
            original_size = img.size
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate small size for pixelation
            small_width = max(1, img.width // self.pixel_size)
            small_height = max(1, img.height // self.pixel_size)
            
            # Resize down (creates pixel effect)
            small_img = img.resize(
                (small_width, small_height),
                Image.Resampling.NEAREST
            )
            
            # Apply color quantization
            quantized = small_img.quantize(colors=self.color_count)
            quantized = quantized.convert('RGB')
            
            # Determine output size
            if output_size:
                final_size = output_size
            else:
                final_size = original_size
            
            # Resize back up with nearest neighbor (keeps blocky look)
            result = quantized.resize(final_size, Image.Resampling.NEAREST)
            
            # Save the result
            result.save(output_path)
            
            return {
                'original_size': original_size,
                'output_size': final_size,
                'pixel_size': self.pixel_size,
                'color_count': self.color_count,
                'input_path': input_path,
                'output_path': output_path
            }
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get information about an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            dict: Image information
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
                'file_size': os.path.getsize(image_path)
            }


def convert_image(input_path: str, output_path: str, 
                  pixel_size: int = 10, color_count: int = 16) -> dict:
    """
    Convenience function to convert an image to pixel art.
    
    Args:
        input_path: Path to input image
        output_path: Path for output image
        pixel_size: Size of pixel blocks
        color_count: Number of colors
        
    Returns:
        dict: Conversion statistics
    """
    converter = PixelArtConverter(pixel_size=pixel_size, color_count=color_count)
    return converter.convert(input_path, output_path)
