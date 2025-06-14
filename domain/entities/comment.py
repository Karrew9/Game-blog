from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entities.post import Post
    from domain.entities.user import User


@dataclass
class Comment:
    id: Optional[int]
    content: str
    author_id: int
    post_id: int
    created_at: datetime
    author: Optional['User'] = None
    post: Optional['Post'] = None