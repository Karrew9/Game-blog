from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommentCreateDTO:
    content: str
    author_id: int
    post_id: int


@dataclass
class CommentDTO:
    id: int
    content: str
    author_id: int
    post_id: int
    created_at: datetime