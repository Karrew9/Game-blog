import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from domain.entities.comment import Comment
    from domain.entities.user import User



@dataclass
class Post:
    id: Optional[int]
    title: str
    content: str
    author_id: int
    created_at: datetime
    author: Optional['User'] = None
    comments: List['Comment'] = None

    def __post_init__(self):
        if self.comments is None:
            self.comments = []

