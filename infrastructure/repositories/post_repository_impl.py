from typing import List, Optional
from sqlalchemy.orm import Session

from domain.entities.post import Post
from domain.repositories.post_repository import PostRepository
from infrastructure.database.models import PostModel


class PostRepositoryImpl(PostRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, post_id: int) -> Optional[Post]:
        post_model = self.session.query(PostModel).filter_by(id=post_id).first()
        return self._convert_to_entity(post_model) if post_model else None

    def find_all(self) -> List[Post]:
        post_models = self.session.query(PostModel).all()
        return [self._convert_to_entity(post_model) for post_model in post_models]

    def find_by_author(self, author_id: int) -> List[Post]:
        post_models = self.session.query(PostModel).filter_by(author_id=author_id).all()
        return [self._convert_to_entity(post_model) for post_model in post_models]

    def save(self, post: Post) -> Post:
        if post.id is None:
            post_model = PostModel(
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                created_at=post.created_at
            )
            self.session.add(post_model)
            self.session.commit()
            self.session.refresh(post_model)
            return self._convert_to_entity(post_model)
        else:
            post_model = self.session.query(PostModel).filter_by(id=post.id).first()
            if post_model:
                post_model.title = post.title
                post_model.content = post.content
                self.session.commit()
                return self._convert_to_entity(post_model)
            raise ValueError(f"Post with id {post.id} not found")

    def delete(self, post_id: int) -> None:
        post_model = self.session.query(PostModel).filter_by(id=post_id).first()
        if post_model:
            self.session.delete(post_model)
            self.session.commit()

    @staticmethod
    def _convert_to_entity(post_model: PostModel) -> Post:
        return Post(
            id=post_model.id,
            title=post_model.title,
            content=post_model.content,
            author_id=post_model.author_id,
            created_at=post_model.created_at
        )