import argparse
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

def convert_to_pixel_art(input_path, output_path, pixel_size, colors=0, dither=False, 
                         grid=False, grid_color=(30, 30, 30), grid_thickness=1,
                         smooth_radius=0.5, contrast=1.2, brightness=1.1):
    """
    Преобразует изображение в эстетичный пиксель-арт с дополнительной обработкой
    
    :param input_path: Путь к исходному изображению
    :param output_path: Путь для сохранения результата
    :param pixel_size: Размер одного пикселя
    :param colors: Количество цветов в палитре (0 - без ограничения)
    :param dither: Использовать диффузию ошибок
    :param grid: Добавить сетку между пикселями
    :param grid_color: Цвет сетки (RGB)
    :param grid_thickness: Толщина линий сетки
    :param smooth_radius: Радиус сглаживания перед обработкой
    :param contrast: Коэффициент контраста (1.0 = без изменений)
    :param brightness: Коэффициент яркости (1.0 = без изменений)
    """
    try:
        # Открываем и конвертируем в RGB
        img = Image.open(input_path).convert('RGB')
        orig_width, orig_height = img.size
        
        # Предварительное сглаживание для удаления шума
        if smooth_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=smooth_radius))
        
        # Вычисляем целевые размеры для пикселизации
        small_width = max(1, orig_width // pixel_size)
        small_height = max(1, orig_height // pixel_size)
        
        # Уменьшаем изображение с сохранением пропорций
        small_img = img.resize((small_width, small_height), Image.LANCZOS)
        
        # Ограничиваем палитру цветов при необходимости
        if colors > 0:
            if dither:
                small_img = small_img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, 
                                              dither=Image.Dither.FLOYDSTEINBERG).convert('RGB')
            else:
                small_img = small_img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, 
                                              dither=Image.Dither.NONE).convert('RGB')
        
        # Масштабируем обратно до оригинального размера
        result = small_img.resize((orig_width, orig_height), Image.NEAREST)
        
        # Добавляем сетку для разделения пикселей
        if grid:
            draw = ImageDraw.Draw(result)
            # Вертикальные линии
            for x in range(0, orig_width, pixel_size):
                draw.line([(x, 0), (x, orig_height)], fill=grid_color, width=grid_thickness)
            # Горизонтальные линии
            for y in range(0, orig_height, pixel_size):
                draw.line([(0, y), (orig_width, y)], fill=grid_color, width=grid_thickness)
        
        # Пост-обработка для улучшения визуального восприятия
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(contrast)
        
        enhancer = ImageEnhance.Brightness(result)
        result = enhancer.enhance(brightness)
        
        # Сохраняем результат
        result.save(output_path)
        print(f"✨ Эстетичный пиксель-арт успешно создан и сохранен в {output_path}")
        print(f"📊 Оригинальный размер: {orig_width}x{orig_height} → Пикселизация: {small_width}x{small_height}")
        
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл {input_path} не найден")
    except Exception as e:
        print(f"⚠️ Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='🎨 Продвинутый конвертер в пиксель-арт')
    
    parser.add_argument('-i', '--input', required=True, help='Путь к исходному изображению')
    parser.add_argument('-o', '--output', default='art_pixel_perfect.png', 
                        help='Путь для сохранения результата (рекомендуется .png)')
    parser.add_argument('-p', '--pixel_size', type=int, default=8,
                        help='Размер одного пикселя (по умолчанию: 8)')
    
    # Дополнительные настройки обработки
    parser.add_argument('-c', '--colors', type=int, default=32,
                        help='Количество цветов в палитре (0 - без ограничения, по умолчанию: 32)')
    parser.add_argument('--dither', action='store_true',
                        help='Использовать диффузию для плавных переходов')
    parser.add_argument('--grid', action='store_true',
                        help='Добавить сетку между пикселями')
    parser.add_argument('--grid-color', type=int, nargs=3, default=[20, 20, 30],
                        help='Цвет сетки в RGB (по умолчанию: 20 20 30)')
    parser.add_argument('--grid-thickness', type=int, default=1,
                        help='Толщина линий сетки (по умолчанию: 1)')
    
    # Параметры улучшения качества
    parser.add_argument('--smooth', type=float, default=0.5,
                        help='Степень сглаживания перед обработкой (0.0-2.0, по умолчанию: 0.5)')
    parser.add_argument('--contrast', type=float, default=1.2,
                        help='Коэффициент контраста (по умолчанию: 1.2)')
    parser.add_argument('--brightness', type=float, default=1.1,
                        help='Коэффициент яркости (по умолчанию: 1.1)')
    
    args = parser.parse_args()
    
    convert_to_pixel_art(
        input_path=args.input,
        output_path=args.output,
        pixel_size=args.pixel_size,
        colors=args.colors,
        dither=args.dither,
        grid=args.grid,
        grid_color=tuple(args.grid_color),
        grid_thickness=args.grid_thickness,
        smooth_radius=args.smooth,
        contrast=args.contrast,
        brightness=args.brightness
    )