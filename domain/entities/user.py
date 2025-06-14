import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Union
from fastapi import UploadFile

if TYPE_CHECKING:
    from domain.entities.post import Post
    from domain.entities.comment import Comment


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    posts: List['Post'] = field(default_factory=list)
    comments: List['Comment'] = field(default_factory=list)

    @property
    def avatar_display_url(self) -> str:
        return self.avatar_url or "/static/images/default-avatar.png"

    async def save_avatar(self, avatar_file: Union[UploadFile, None]) -> Optional[str]:
        if not avatar_file:
            return None

        if self.avatar_url and not self.avatar_url.startswith('/static/images/default-avatar'):
            try:
                old_path = self.avatar_url.lstrip('/')
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception as e:
                print(f"Error deleting old avatar: {e}")

        upload_dir = "static/uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)

        file_ext = os.path.splitext(avatar_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, filename)

        if isinstance(avatar_file, UploadFile):
            with open(file_path, "wb") as buffer:
                content = await avatar_file.read()
                buffer.write(content)
        else:
            with open(file_path, "wb") as buffer:
                buffer.write(avatar_file)

        self.avatar_url = f"/{upload_dir}/{filename}"
        return self.avatar_url