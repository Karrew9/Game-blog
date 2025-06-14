from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.comment import Comment


class CommentRepository(ABC):
    @abstractmethod
    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        pass

    @abstractmethod
    def find_all(self) -> List[Comment]:
        pass

    @abstractmethod
    def find_by_post(self, post_id: int) -> List[Comment]:
        pass

    @abstractmethod
    def find_by_author(self, author_id: int) -> List[Comment]:
        pass

    @abstractmethod
    def save(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    def delete(self, comment_id: int) -> None:
        pass