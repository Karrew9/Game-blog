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

        try:
            processed_blocks = []
            for i, block in enumerate(blocks):
                if block['type'] == 'image' and image_files and str(i) in image_files:
                    file = image_files[str(i)]
                    filename = save_uploaded_file(file)
                    block['content']['url'] = f"/{UPLOAD_FOLDER}/{filename}"

                processed_blocks.append(block)

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

        try:
            post = db.query(PostModel).filter(PostModel.id == post_id).first()
            if not post:
                return None

            if post.author_id != author_id:
                return None

            processed_blocks = []
            for i, block in enumerate(blocks):
                if block['type'] == 'image':
                    if image_files and str(i) in image_files:
                        file = image_files[str(i)]
                        filename = save_uploaded_file(file)
                        block['content']['url'] = f"/{UPLOAD_FOLDER}/{filename}"
                    elif 'content' in block and 'url' in block['content']:
                        pass
                    else:
                        block['content']['url'] = ""

                processed_blocks.append(block)

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

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        ext = file.filename.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("Недопустимый тип файла")

        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return filename