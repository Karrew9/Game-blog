from datetime import datetime
from typing import Optional, List

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from application.dto.user_dto import UserCreateDTO, UserDTO
from core.logger import logger


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_dto: UserCreateDTO) -> UserDTO:
        logger.info(f"Creating user with username: {user_dto.username}")

        user = User(
            id=None,
            username=user_dto.username,
            email=user_dto.email,
            password_hash=self._hash_password(user_dto.password),
            created_at=datetime.now()
        )

        saved_user = self.user_repository.save(user)
        return self._convert_to_dto(saved_user)

    def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        user = self.user_repository.find_by_id(user_id)
        return self._convert_to_dto(user) if user else None

    def get_all_users(self) -> List[UserDTO]:
        users = self.user_repository.find_all()
        return [self._convert_to_dto(user) for user in users]

    def delete_user(self, user_id: int) -> None:
        self.user_repository.delete(user_id)

    @staticmethod
    def _hash_password(password: str) -> str:
        # В реальном приложении используйте bcrypt или аналоги
        return f"hashed_{password}"

    @staticmethod
    def _convert_to_dto(user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )