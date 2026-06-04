# accounts/avatar_utils.py
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def generate_avatar_with_initials(initials, size=200, font_size=80):
    """
    Генерирует аватар с инициалами пользователя.
    """
    # Создаем изображение
    img = Image.new('RGB', (size, size), color=get_color_from_string(initials))
    draw = ImageDraw.Draw(img)
    
    try:
        # Пытаемся загрузить шрифт
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Если шрифт не найден, используем дефолтный
        font = ImageFont.load_default()
    
    # Рассчитываем позицию для текста
    text_bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) / 2
    y = (size - text_height) / 2
    
    # Рисуем текст
    draw.text((x, y), initials, fill="white", font=font)
    
    # Сохраняем в BytesIO
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return ContentFile(img_io.getvalue(), name=f'avatar_{initials}.png')


def get_color_from_string(text):
    """
    Генерирует цвет на основе строки.
    """
    import hashlib
    
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    # Берем первые 6 символов для цвета
    color = f"#{hash_hex[:6]}"
    
    # Делаем цвет мягче
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    # Осветляем
    r = min(r + 40, 255)
    g = min(g + 40, 255)
    b = min(b + 40, 255)
    
    return (r, g, b)


def create_default_avatar_for_profile(profile):
    """
    Создает и сохраняет дефолтный аватар для профиля.
    """
    initials = profile.get_initials()
    
    # Генерируем аватар
    avatar_content = generate_avatar_with_initials(initials)
    
    # Сохраняем в поле avatar
    filename = f'avatar_{profile.user.username}.png'
    profile.avatar.save(filename, avatar_content, save=True)
    
    return profile.avatar.url