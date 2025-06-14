from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreateDTO(UserBase):
    password: str

class UserDTO(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserUpdateDTO(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    @field_validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if len(v) > 50:
                raise ValueError('Username must be less than 50 characters')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
        return v

    @field_validator('bio')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must be less than 500 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_username",
                "email": "new@example.com",
                "password": "newsecurepassword123",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Обновленная информация обо мне"
            }
        }