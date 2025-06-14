from datetime import datetime
from typing import List, Optional

from domain.entities.comment import Comment
from domain.repositories.comment_repository import CommentRepository
from domain.repositories.user_repository import UserRepository
from domain.repositories.post_repository import PostRepository
from application.dto.comment_dto import CommentCreateDTO, CommentDTO
from core.logger import logger


class CommentService:
    def __init__(
            self,
            comment_repository: CommentRepository,
            user_repository: UserRepository,
            post_repository: PostRepository
    ):
        self.comment_repository = comment_repository
        self.user_repository = user_repository
        self.post_repository = post_repository

    def create_comment(self, comment_dto: CommentCreateDTO) -> CommentDTO:
        logger.info(f"Creating comment for post: {comment_dto.post_id}")

        # Проверяем, что автор и пост существуют
        author = self.user_repository.find_by_id(comment_dto.author_id)
        if not author:
            raise ValueError(f"User with id {comment_dto.author_id} not found")

        post = self.post_repository.find_by_id(comment_dto.post_id)
        if not post:
            raise ValueError(f"Post with id {comment_dto.post_id} not found")

        comment = Comment(
            id=None,
            content=comment_dto.content,
            author_id=comment_dto.author_id,
            post_id=comment_dto.post_id,
            created_at=datetime.now()
        )

        saved_comment = self.comment_repository.save(comment)
        return self._convert_to_dto(saved_comment)

    def get_comment_by_id(self, comment_id: int) -> Optional[CommentDTO]:
        comment = self.comment_repository.find_by_id(comment_id)
        return self._convert_to_dto(comment) if comment else None

    def get_all_comments(self) -> List[CommentDTO]:
        comments = self.comment_repository.find_all()
        return [self._convert_to_dto(comment) for comment in comments]

    def get_comments_by_post(self, post_id: int) -> List[CommentDTO]:
        comments = self.comment_repository.find_by_post(post_id)
        return [self._convert_to_dto(comment) for comment in comments]

    def delete_comment(self, comment_id: int) -> None:
        self.comment_repository.delete(comment_id)

    @staticmethod
    def _convert_to_dto(comment: Comment) -> CommentDTO:
        return CommentDTO(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            post_id=comment.post_id,
            created_at=comment.created_at
        )