from datetime import datetime
from typing import List, Optional

from domain.entities.post import Post
from domain.repositories.post_repository import PostRepository
from domain.repositories.user_repository import UserRepository
from application.dto.post_dto import PostCreateDTO, PostDTO
from core.logger import logger


class PostService:
    def __init__(
            self,
            post_repository: PostRepository,
            user_repository: UserRepository
    ):
        self.post_repository = post_repository
        self.user_repository = user_repository

    def create_post(self, post_dto: PostCreateDTO) -> PostDTO:
        logger.info(f"Creating post with title: {post_dto.title}")

        # Проверяем, что автор существует
        author = self.user_repository.find_by_id(post_dto.author_id)
        if not author:
            raise ValueError(f"User with id {post_dto.author_id} not found")

        post = Post(
            id=None,
            title=post_dto.title,
            content=post_dto.content,
            author_id=post_dto.author_id,
            created_at=datetime.now()
        )

        saved_post = self.post_repository.save(post)
        return self._convert_to_dto(saved_post)

    def get_post_by_id(self, post_id: int) -> Optional[PostDTO]:
        post = self.post_repository.find_by_id(post_id)
        return self._convert_to_dto(post) if post else None

    def get_all_posts(self) -> List[PostDTO]:
        posts = self.post_repository.find_all()
        return [self._convert_to_dto(post) for post in posts]

    def get_posts_by_author(self, author_id: int) -> List[PostDTO]:
        posts = self.post_repository.find_by_author(author_id)
        return [self._convert_to_dto(post) for post in posts]

    def delete_post(self, post_id: int) -> None:
        self.post_repository.delete(post_id)

    @staticmethod
    def _convert_to_dto(post: Post) -> PostDTO:
        return PostDTO(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            created_at=post.created_at
        )

    async def get_latest_posts(self, limit: int = 5) -> List[PostDTO]:
        posts = self.post_repository.find_all()
        sorted_posts = sorted(posts, key=lambda x: x.created_at, reverse=True)
        return [self._convert_to_dto(post) for post in sorted_posts[:limit]]