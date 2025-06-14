from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


@dataclass
class PostCreateDTO:
    title: str
    content: str
    author_id: int


@dataclass
class PostDTO:
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime

class PostUpdateDTO(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    is_published: Optional[bool] = None
    cover_image_url: Optional[str] = None

    @field_validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v) < 5:
                raise ValueError('Title must be at least 5 characters long')
            if len(v) > 100:
                raise ValueError('Title must be less than 100 characters')
        return v

    @field_validator('content')
    def validate_content(cls, v):
        if v is not None:
            if len(v) < 50:
                raise ValueError('Content must be at least 50 characters long')
            if len(v) > 10000:
                raise ValueError('Content must be less than 10,000 characters')
        return v

    @field_validator('category')
    def validate_category(cls, v):
        if v is not None and len(v) > 30:
            raise ValueError('Category must be less than 30 characters')
        return v

    @field_validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            for tag in v:
                if len(tag) > 20:
                    raise ValueError('Tag must be less than 20 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Обновленный заголовок поста",
                "content": "Это обновленное содержимое поста...",
                "category": "Игры",
                "tags": ["гейминг", "новинки", "2024"],
                "is_published": True,
                "cover_image_url": "https://example.com/new-cover.jpg"
            }
        }