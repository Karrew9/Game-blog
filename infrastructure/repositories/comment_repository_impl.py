from typing import List, Optional
from sqlalchemy.orm import Session

from domain.entities.comment import Comment
from domain.repositories.comment_repository import CommentRepository
from infrastructure.database.models import CommentModel


class CommentRepositoryImpl(CommentRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        comment_model = self.session.query(CommentModel).filter_by(id=comment_id).first()
        return self._convert_to_entity(comment_model) if comment_model else None

    def find_all(self) -> List[Comment]:
        comment_models = self.session.query(CommentModel).all()
        return [self._convert_to_entity(cm) for cm in comment_models]

    def find_by_post(self, post_id: int) -> List[Comment]:
        comment_models = self.session.query(CommentModel).filter_by(post_id=post_id).all()
        return [self._convert_to_entity(cm) for cm in comment_models]

    def find_by_author(self, author_id: int) -> List[Comment]:
        comment_models = self.session.query(CommentModel).filter_by(author_id=author_id).all()
        return [self._convert_to_entity(cm) for cm in comment_models]

    def save(self, comment: Comment) -> Comment:
        if comment.id is None:
            comment_model = CommentModel(
                content=comment.content,
                author_id=comment.author_id,
                post_id=comment.post_id,
                created_at=comment.created_at
            )
            self.session.add(comment_model)
            self.session.commit()
            self.session.refresh(comment_model)
            return self._convert_to_entity(comment_model)
        else:
            comment_model = self.session.query(CommentModel).filter_by(id=comment.id).first()
            if comment_model:
                comment_model.content = comment.content
                self.session.commit()
                return self._convert_to_entity(comment_model)
            raise ValueError(f"Comment with id {comment.id} not found")

    def delete(self, comment_id: int) -> None:
        comment_model = self.session.query(CommentModel).filter_by(id=comment_id).first()
        if comment_model:
            self.session.delete(comment_model)
            self.session.commit()

    @staticmethod
    def _convert_to_entity(comment_model: CommentModel) -> Comment:
        return Comment(
            id=comment_model.id,
            content=comment_model.content,
            author_id=comment_model.author_id,
            post_id=comment_model.post_id,
            created_at=comment_model.created_at
        )