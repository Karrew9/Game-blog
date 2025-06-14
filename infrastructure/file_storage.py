import os
import uuid
from fastapi import UploadFile
from typing import Optional

AVATAR_UPLOAD_DIR = "static/uploads/avatars"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def save_uploaded_file(
        file: UploadFile,
        upload_dir: str = AVATAR_UPLOAD_DIR,
        max_size: int = 5 * 1024 * 1024  # 5MB
) -> Optional[str]:
    """Сохраняет загруженный файл с проверками"""
    # Проверка типа файла
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Недопустимый тип изображения")

    # Проверка размера файла
    file.file.seek(0, 2)  # Перемещаемся в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Возвращаемся в начало

    if file_size > max_size:
        raise ValueError(f"Файл слишком большой. Максимум {max_size // 1024 // 1024}MB")

    # Создаем директорию, если не существует
    os.makedirs(upload_dir, exist_ok=True)

    # Генерируем уникальное имя файла
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return f"/{upload_dir}/{filename}"


def delete_file(file_url: str) -> bool:
    """Удаляет файл по его URL"""
    if not file_url or file_url.startswith(('http://', 'https://')):
        return False

    try:
        file_path = file_url.lstrip('/')
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False