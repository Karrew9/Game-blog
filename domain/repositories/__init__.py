# Экспорт интерфейсов репозиториев
from .user_repository import UserRepository
from .post_repository import PostRepository
from .comment_repository import CommentRepository

__all__ = ["UserRepository", "PostRepository", "CommentRepository"]