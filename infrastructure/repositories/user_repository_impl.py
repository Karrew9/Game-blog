from typing import List, Optional
from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        user_model = self.session.query(UserModel).filter_by(id=user_id).first()
        return self._convert_to_entity(user_model) if user_model else None

    def find_by_username(self, username: str) -> Optional[User]:
        user_model = self.session.query(UserModel).filter_by(username=username).first()
        return self._convert_to_entity(user_model) if user_model else None

    def find_by_email(self, email: str) -> Optional[User]:
        user_model = self.session.query(UserModel).filter_by(email=email).first()
        return self._convert_to_entity(user_model) if user_model else None

    def save(self, user: User) -> User:
        if user.id is None:
            user_model = UserModel(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                created_at=user.created_at
            )
            self.session.add(user_model)
            self.session.commit()
            self.session.refresh(user_model)
            return self._convert_to_entity(user_model)
        else:
            user_model = self.session.query(UserModel).filter_by(id=user.id).first()
            if user_model:
                user_model.username = user.username
                user_model.email = user.email
                user_model.password_hash = user.password_hash
                self.session.commit()
                return self._convert_to_entity(user_model)
            raise ValueError(f"User with id {user.id} not found")

    def delete(self, user_id: int) -> None:
        user_model = self.session.query(UserModel).filter_by(id=user_id).first()
        if user_model:
            self.session.delete(user_model)
            self.session.commit()

    def find_all(self) -> List[User]:
        user_models = self.session.query(UserModel).all()
        return [self._convert_to_entity(user_model) for user_model in user_models]

    @staticmethod
    def _convert_to_entity(user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            password_hash=user_model.password_hash,
            created_at=user_model.created_at
        )