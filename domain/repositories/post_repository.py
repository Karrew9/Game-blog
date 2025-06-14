import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict

from sqlalchemy.orm import Session

from domain.entities.post import Post
from infrastructure.database.models import PostModel
from infrastructure.file_storage import save_uploaded_file

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class PostRepository(ABC):
    @abstractmethod
    def find_by_id(self, post_id: int) -> Optional[Post]:
        pass

    @abstractmethod
    def find_all(self) -> List[Post]:
        pass

    @abstractmethod
    def find_by_author(self, author_id: int) -> List[Post]:
        pass

    @abstractmethod
    def save(self, post: Post) -> Post:
        pass

    @abstractmethod
    def delete(self, post_id: int) -> None:
        pass


    def create_post_in_db(
            db: Session,
            title: str,
            blocks: List[Dict],
            author_id: int,
            image_files: Optional[Dict] = None
    ) -> PostModel:
        """
        Создает новый пост в базе данных

        Args:
            db: Сессия базы данных
            title: Заголовок поста
            blocks: Список блоков контента
            author_id: ID автора
            image_files: Словарь с файлами изображений (ключ - индекс блока)

        Returns:
            Созданный пост
        """
        try:
            # Обрабатываем изображения
            processed_blocks = []
            for i, block in enumerate(blocks):
                if block['type'] == 'image' and image_files and str(i) in image_files:
                    file = image_files[str(i)]
                    # Сохраняем файл и обновляем URL
                    filename = save_uploaded_file(file)
                    block['content']['url'] = f"/{UPLOAD_FOLDER}/{filename}"

                processed_blocks.append(block)

            # Создаем пост
            new_post = PostModel(
                title=title,
                blocks=processed_blocks,
                author_id=author_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(new_post)
            db.commit()
            db.refresh(new_post)

            return new_post

        except Exception as e:
            db.rollback()
            raise e

    def update_post(
            db: Session,
            post_id: int,
            title: str,
            blocks: List[Dict],
            author_id: int,
            image_files: Optional[Dict] = None
    ) -> Optional[PostModel]:
        """
        Обновляет существующий пост в базе данных

        Args:
            db: Сессия базы данных
            post_id: ID поста для обновления
            title: Новый заголовок
            blocks: Новые блоки контента
            author_id: ID автора (для проверки прав)
            image_files: Словарь с файлами изображений (ключ - индекс блока)

        Returns:
            Обновленный пост или None, если пост не найден или нет прав
        """
        try:
            # Находим пост
            post = db.query(PostModel).filter(PostModel.id == post_id).first()
            if not post:
                return None

            # Проверяем права
            if post.author_id != author_id:
                return None

            # Обрабатываем изображения
            processed_blocks = []
            for i, block in enumerate(blocks):
                if block['type'] == 'image':
                    # Если есть новое изображение
                    if image_files and str(i) in image_files:
                        file = image_files[str(i)]
                        filename = save_uploaded_file(file)
                        block['content']['url'] = f"/{UPLOAD_FOLDER}/{filename}"
                    # Иначе сохраняем существующее изображение
                    elif 'content' in block and 'url' in block['content']:
                        pass  # Сохраняем существующий URL
                    else:
                        block['content']['url'] = ""

                processed_blocks.append(block)

            # Обновляем пост
            post.title = title
            post.blocks = processed_blocks
            post.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(post)

            return post

        except Exception as e:
            db.rollback()
            raise e

    def save_uploaded_file(file) -> str:
        """
        Сохраняет загруженный файл на сервер

        Args:
            file: Файл для сохранения

        Returns:
            Имя сохраненного файла
        """
        # Создаем папку, если ее нет
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Генерируем уникальное имя файла
        ext = file.filename.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("Недопустимый тип файла")

        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return filename