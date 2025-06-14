from infrastructure.database.session import SessionLocal
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.repositories.post_repository_impl import PostRepositoryImpl
from infrastructure.repositories.comment_repository_impl import CommentRepositoryImpl
from application.services.user_service import UserService
from application.services.post_service import PostService
from application.services.comment_service import CommentService


class ServiceFactory:
    @staticmethod
    def create_user_service():
        session = SessionLocal()
        user_repository = UserRepositoryImpl(session)
        return UserService(user_repository)

    @staticmethod
    def create_post_service():
        session = SessionLocal()
        post_repository = PostRepositoryImpl(session)
        user_repository = UserRepositoryImpl(session)
        return PostService(post_repository, user_repository)

    @staticmethod
    def create_comment_service():
        session = SessionLocal()
        comment_repository = CommentRepositoryImpl(session)
        user_repository = UserRepositoryImpl(session)
        post_repository = PostRepositoryImpl(session)
        return CommentService(comment_repository, user_repository, post_repository)