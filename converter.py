"""
Pixel Art Converter Module
Converts images to pixel art style with configurable parameters
"""

import io
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image


class PixelArtConverter:
    """Main class for converting images to pixel art"""

    PALETTES = {
        "gameboy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
        "nes": [
            (0, 0, 0),
            (252, 252, 252),
            (188, 188, 188),
            (124, 124, 124),
            (164, 228, 252),
            (60, 188, 252),
            (0, 120, 248),
            (0, 0, 188),
            (184, 248, 216),
            (88, 216, 132),
            (0, 168, 68),
            (0, 104, 56),
            (248, 216, 120),
            (248, 184, 0),
            (172, 124, 0),
            (100, 76, 0),
            (248, 184, 184),
            (248, 120, 88),
            (216, 40, 0),
            (136, 20, 0),
            (216, 184, 248),
            (152, 120, 248),
            (104, 68, 252),
            (68, 40, 188),
        ],
        "grayscale": [(i, i, i) for i in range(0, 256, 32)],
        "retro": [
            (0, 0, 0),
            (255, 255, 255),
            (255, 0, 0),
            (0, 255, 255),
            (128, 0, 128),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 128, 0),
            (128, 64, 0),
            (255, 128, 128),
            (64, 64, 64),
            (128, 128, 128),
            (128, 255, 128),
            (128, 128, 255),
            (192, 192, 192),
        ],
    }

    def __init__(self, pixel_size: int = 8, palette: str = "retro"):
        self.pixel_size = max(1, min(64, pixel_size))
        self.palette_name = palette
        self.palette = self.PALETTES.get(palette, None)

    def _find_closest_color(
        self, color: Tuple[int, int, int], palette: List[Tuple[int, int, int]]
    ) -> Tuple[int, int, int]:
        min_distance = float("inf")
        closest = palette[0]
        for pal_color in palette:
            distance = sum((int(a) - int(b)) ** 2 for a, b in zip(color, pal_color))
            if distance < min_distance:
                min_distance = distance
                closest = pal_color
        return closest

    def _pixelate(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        small_width = max(1, width // self.pixel_size)
        small_height = max(1, height // self.pixel_size)
        small = image.resize((small_width, small_height), Image.Resampling.NEAREST)
        return small.resize((width, height), Image.Resampling.NEAREST)

    def _apply_palette(self, image: Image.Image) -> Image.Image:
        if self.palette is None:
            return image
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        for y in range(height):
            for x in range(width):
                original_color = tuple(img_array[y, x])
                new_color = self._find_closest_color(original_color, self.palette)
                img_array[y, x] = new_color
        return Image.fromarray(img_array)

    def convert(
        self, image: Image.Image, output_size: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        has_alpha = image.mode == "RGBA"
        if has_alpha:
            alpha = image.split()[3]
            image = image.convert("RGB")
        pixelated = self._pixelate(image)
        result = self._apply_palette(pixelated)
        if has_alpha:
            alpha_pixelated = self._pixelate(alpha.convert("RGB")).convert("L")
            result.putalpha(alpha_pixelated)
        if output_size:
            result = result.resize(output_size, Image.Resampling.NEAREST)
        return result

    def convert_from_bytes(self, image_bytes: bytes, output_format: str = "PNG") -> bytes:
        image = Image.open(io.BytesIO(image_bytes))
        result = self.convert(image)
        output_buffer = io.BytesIO()
        if result.mode == "RGBA" and output_format.upper() == "JPEG":
            result = result.convert("RGB")
        result.save(output_buffer, format=output_format)
        output_buffer.seek(0)
        return output_buffer.getvalue()

    @classmethod
    def get_available_palettes(cls) -> List[str]:
        return list(cls.PALETTES.keys()) + ["original"]


def convert_image(
    input_path: str, output_path: str, pixel_size: int = 8, palette: str = "retro"
) -> None:
    converter = PixelArtConverter(pixel_size=pixel_size, palette=palette)
    image = Image.open(input_path)
    result = converter.convert(image)
    result.save(output_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python converter.py <input> <o> [pixel_size] [palette]")
        print(f"Palettes: {PixelArtConverter.get_available_palettes()}")
        sys.exit(1)
    convert_image(
        sys.argv[1],
        sys.argv[2],
        int(sys.argv[3]) if len(sys.argv) > 3 else 8,
        sys.argv[4] if len(sys.argv) > 4 else "retro",
    )
