import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi import FastAPI, Request, Depends, HTTPException, Form, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import func, update
from sqlalchemy.orm import Session, joinedload
from starlette.responses import RedirectResponse
from presentation.api.auth import router as auth_router
from core.security import get_current_user, get_current_user_optional, create_access_token, hash_password, generate_csrf_token, validate_csrf_token, authenticate_user, verify_password
from infrastructure.database.session import SessionLocal, engine, Base
from infrastructure.database.models import PostModel, UserModel, CommentModel
from infrastructure.database.seed import seed_database
from core.config import settings
from core.logger import logger

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_app():
    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.error(f"Ошибка при заполнении БД: {e}")
    finally:
        db.close()

    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )

    app.include_router(auth_router, prefix="/auth")

    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    @app.get("/", response_class=HTMLResponse)
    async def read_root(
            request: Request,
            db: Session = Depends(get_db),
            current_user: Optional[UserModel] = Depends(get_current_user_optional)
    ):
        posts = (
            db.query(PostModel)
                .options(joinedload(PostModel.author))
                .order_by(PostModel.created_at.desc())
                .limit(5)
                .all()
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "posts": posts,
                "current_user": current_user,
                "app_title": settings.APP_TITLE,
                "app_description": settings.APP_DESCRIPTION
            }
        )

    @app.get("/posts", response_class=HTMLResponse)
    async def list_posts(
            request: Request,
            page: int = 1,
            per_page: int = 10,
            db: Session = Depends(get_db),
            current_user: Optional[UserModel] = Depends(get_current_user_optional)
    ):
        try:
            offset = (page - 1) * per_page
            posts = db.query(PostModel) \
                .options(joinedload(PostModel.author)) \
                .order_by(PostModel.created_at.desc()) \
                .offset(offset) \
                .limit(per_page) \
                .all()

            total_posts = db.query(func.count(PostModel.id)).scalar()
            total_pages = (total_posts + per_page - 1) // per_page

            return templates.TemplateResponse(
                "posts/list.html",
                {
                    "request": request,
                    "posts": posts,
                    "current_user": current_user,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1
                    },
                    "app_title": settings.APP_TITLE
                }
            )
        except Exception as e:
            logger.error(f"Error listing posts: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.get("/posts/new", response_class=HTMLResponse)
    async def new_post_form(
            request: Request,
            current_user: UserModel = Depends(get_current_user)
    ):
        if not current_user:
            raise HTTPException(status_code=403, detail="Требуется авторизация")

        return templates.TemplateResponse(
            "create_post.html",
            {
                "request": request,
                "app_title": settings.APP_TITLE,
                "csrf_token": generate_csrf_token()
            }
        )

    @app.post("/posts/new", response_class=HTMLResponse)
    async def create_post(
            request: Request,
            title: str = Form(...),
            content: str = Form(...),
            csrf_token: str = Form(...),
            current_user: UserModel = Depends(get_current_user),
            db: Session = Depends(get_db)
    ):
        if not current_user:
            raise HTTPException(status_code=403, detail="Требуется авторизация")

        if not validate_csrf_token(csrf_token):
            raise HTTPException(status_code=400, detail="Неверный CSRF токен")

        new_post = PostModel(
            title=title,
            content=content,
            author_id=current_user.id,
            created_at=datetime.utcnow()
        )

        db.add(new_post)
        db.commit()

        return RedirectResponse(url=f"/posts/{new_post.id}", status_code=303)

    @app.get("/posts/{post_id}", response_class=HTMLResponse)
    async def read_post(
            post_id: int,
            request: Request,
            db: Session = Depends(get_db)
    ):
        try:
            post = db.query(PostModel) \
                .options(
                joinedload(PostModel.author),
                joinedload(PostModel.comments).joinedload(CommentModel.author)
            ) \
                .filter(PostModel.id == post_id) \
                .first()

            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            similar_posts = db.query(PostModel) \
                .filter(PostModel.author_id == post.author_id, PostModel.id != post.id) \
                .order_by(func.random()) \
                .limit(3) \
                .all()

            current_user = await get_current_user_optional(request, db)

            post.created_at_str = post.created_at.strftime('%d.%m.%Y в %H:%M')
            for comment in post.comments:
                comment.created_at_str = comment.created_at.strftime('%d.%m.%Y в %H:%M')

            return templates.TemplateResponse(
                "post_detail.html",
                {
                    "request": request,
                    "post": post,
                    "similar_posts": similar_posts,
                    "current_user": current_user,
                    "app_title": settings.APP_TITLE,
                    "csrf_token": generate_csrf_token()
                }
            )
        except Exception as e:
            logger.error(f"Error in read_post: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
    async def edit_post_form(
            post_id: int,
            request: Request,
            db: Session = Depends(get_db),
            current_user: UserModel = Depends(get_current_user)
    ):
        try:
            post = db.query(PostModel) \
                .filter(
                PostModel.id == post_id,
                PostModel.author_id == current_user.id
            ) \
                .first()

            if not post:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found or you don't have permission to edit it"
                )

            return templates.TemplateResponse(
                "posts/edit.html",
                {
                    "request": request,
                    "post": post,
                    "current_user": current_user,
                    "csrf_token": generate_csrf_token(),
                    "app_title": f"Edit {post.title} | {settings.APP_TITLE}"
                }
            )
        except Exception as e:
            logger.error(f"Error loading edit form: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.post("/posts/{post_id}/edit", response_class=HTMLResponse)
    async def update_post(
            post_id: int,
            request: Request,
            title: str = Form(...),
            content: str = Form(...),
            csrf_token: str = Form(...),
            db: Session = Depends(get_db),
            current_user: UserModel = Depends(get_current_user)
    ):
        try:
            if not validate_csrf_token(csrf_token):
                raise HTTPException(status_code=400, detail="Invalid CSRF token")

            post = db.query(PostModel) \
                .filter(
                PostModel.id == post_id,
                PostModel.author_id == current_user.id
            ) \
                .first()

            if not post:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found or you don't have permission to edit it"
                )

            post.title = title
            post.content = content
            post.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(post)

            return RedirectResponse(
                url=f"/posts/{post.id}",
                status_code=status.HTTP_303_SEE_OTHER
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating post: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.post("/posts/{post_id}/comments", response_class=HTMLResponse)
    async def create_comment(
            post_id: int,
            request: Request,
            content: str = Form(...),
            csrf_token: str = Form(...),
            current_user: UserModel = Depends(get_current_user),
            db: Session = Depends(get_db)
    ):
        if not validate_csrf_token(csrf_token):
            raise HTTPException(status_code=400, detail="Неверный CSRF токен")

        post = db.query(PostModel).filter(PostModel.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        new_comment = CommentModel(
            content=content,
            author_id=current_user.id,
            post_id=post_id,
            created_at=datetime.utcnow()
        )

        db.add(new_comment)
        db.commit()

        return RedirectResponse(f"/posts/{post_id}", status_code=303)

    @app.get("/users/{user_id}", response_class=HTMLResponse)
    async def user_profile(
            user_id: int,
            request: Request,
            page: int = 1,
            per_page: int = 5,
            db: Session = Depends(get_db),
            current_user: Optional[UserModel] = Depends(get_current_user_optional)
    ):
        try:
            user = db.query(UserModel) \
                .filter(UserModel.id == user_id) \
                .first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            avatar_url = user.avatar_url

            offset = (page - 1) * per_page
            posts = db.query(PostModel) \
                .filter(PostModel.author_id == user_id) \
                .order_by(PostModel.created_at.desc()) \
                .offset(offset) \
                .limit(per_page) \
                .all()

            total_posts = db.query(PostModel) \
                .filter(PostModel.author_id == user_id) \
                .count()
            total_pages = (total_posts + per_page - 1) // per_page

            return templates.TemplateResponse(
                "users/profile.html",
                {
                    "request": request,
                    "user": user,
                    "avatar_url": avatar_url,
                    "posts": posts,
                    "current_user": current_user,
                    "total_posts": total_posts,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1
                    },
                    "app_title": f"{user.username} | {settings.APP_TITLE}"
                }
            )
        except Exception as e:
            logger.error(f"Error loading user profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.get("/profile", response_class=HTMLResponse)
    async def my_profile(
            request: Request,
            page: int = 1,
            per_page: int = 5,
            db: Session = Depends(get_db),
            current_user: UserModel = Depends(get_current_user)
    ):
        try:
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")

            offset = (page - 1) * per_page
            posts = db.query(PostModel) \
                .filter(PostModel.author_id == current_user.id) \
                .order_by(PostModel.created_at.desc()) \
                .offset(offset) \
                .limit(per_page) \
                .all()

            total_posts = db.query(PostModel) \
                .filter(PostModel.author_id == current_user.id) \
                .count()
            total_pages = (total_posts + per_page - 1) // per_page

            return templates.TemplateResponse(
                "users/profile.html",
                {
                    "request": request,
                    "user": current_user,
                    "posts": posts,
                    "current_user": current_user,
                    "total_posts": total_posts,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_pages": total_pages,
                        "has_next": page < total_pages,
                        "has_prev": page > 1
                    },
                    "app_title": f"Мой профиль | {settings.APP_TITLE}"
                }
            )
        except Exception as e:
            logger.error(f"Error loading profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.get("/settings", response_class=HTMLResponse)
    async def user_settings(
            request: Request,
            db: Session = Depends(get_db),
            current_user: UserModel = Depends(get_current_user)
    ):
        try:
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")

            return templates.TemplateResponse(
                "users/settings.html",
                {
                    "request": request,
                    "user": current_user,
                    "current_user": current_user,
                    "app_title": f"Настройки | {settings.APP_TITLE}"
                }
            )
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.put("/settings")
    async def update_user_settings(
            username: Optional[str] = Form(None),
            email: Optional[str] = Form(None),
            bio: Optional[str] = Form(None),
            avatar: Optional[UploadFile] = File(None),
            current_password: str = Form(...),
            new_password: Optional[str] = Form(None),
            db: Session = Depends(get_db),
            current_user: UserModel = Depends(get_current_user)
    ):
        try:
            if not current_user.verify_password(current_password):
                raise HTTPException(
                    status_code=400,
                    detail={"field": "current_password", "message": "Неверный текущий пароль"}
                )

            user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            update_data = {}

            if username and username != user.username:
                existing_user = db.query(UserModel).filter(
                    UserModel.username == username,
                    UserModel.id != user.id
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail={"field": "username", "message": "Это имя пользователя уже занято"}
                    )
                update_data["username"] = username

            if email and email != user.email:
                existing_user = db.query(UserModel).filter(
                    UserModel.email == email,
                    UserModel.id != user.id
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail={"field": "email", "message": "Этот email уже используется"}
                    )
                update_data["email"] = email

            if bio is not None:
                update_data["bio"] = bio

            if new_password:
                update_data["password_hash"] = hash_password(new_password)

            if avatar:
                try:
                    upload_dir = "static/uploads/avatars"
                    os.makedirs(upload_dir, exist_ok=True)

                    if user.avatar_path and not user.avatar_path.startswith('/static/images/default-avatar'):
                        old_path = user.avatar_path.lstrip('/')
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    file_ext = os.path.splitext(avatar.filename)[1].lower()
                    filename = f"user_{user.id}{file_ext}"
                    file_path = f"/{upload_dir}/{filename}"

                    counter = 1
                    while os.path.exists(file_path.lstrip('/')):
                        filename = f"user_{user.id}_{counter}{file_ext}"
                        file_path = f"/{upload_dir}/{filename}"
                        counter += 1

                    with open(file_path.lstrip('/'), "wb") as buffer:
                        content = await avatar.read()
                        buffer.write(content)

                    update_data["avatar_path"] = file_path
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail={"field": "avatar", "message": f"Ошибка загрузки аватара: {str(e)}"}
                    )

            if update_data:
                try:
                    db.query(UserModel).filter(UserModel.id == user.id).update(update_data)
                    db.commit()

                    db.refresh(user)

                    return {
                        "message": "Настройки успешно обновлены",
                        "user": {
                            "username": user.username,
                            "email": user.email,
                            "bio": user.bio,
                            "avatar_url": user.avatar_url
                        }
                    }
                except Exception as e:
                    db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail={"message": f"Ошибка при обновлении данных: {str(e)}"}
                    )

            return {"message": "Нет изменений для сохранения"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in update_user_settings: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Internal server error"}
            )

    @app.post("/auth/register")
    async def register_user(
            request: Request,
            username: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            password_confirm: str = Form(...),
            db: Session = Depends(get_db)
    ):
        if password != password_confirm:
            raise HTTPException(
                status_code=400,
                detail="Пароли не совпадают"
            )

        existing_user = db.query(UserModel).filter(
            (UserModel.username == username) | (UserModel.email == email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким именем или email уже существует"
            )

        new_user = UserModel(
            username=username,
            email=email,
            avatar_path="static/images/default-avatar.png",
            password_hash=hash_password(password),
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()

        access_token = create_access_token(
            data={"sub": new_user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        return response

    @app.post("/auth/login")
    async def login_user(
            request: Request,
            username: str = Form(...),
            password: str = Form(...),
            db: Session = Depends(get_db)
    ):
        try:
            user = authenticate_user(db, username=username, password=password)

            if not user:
                logger.warning(f"Failed login attempt for username: {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверное имя пользователя или пароль"
                )

            access_token = create_access_token(
                data={"sub": user.username, "user_id": str(user.id)},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            response = RedirectResponse(
                url="/",
                status_code=status.HTTP_303_SEE_OTHER
            )

            cookie_kwargs = {
                "key": "access_token",
                "value": f"Bearer {access_token}",
                "httponly": True,
                "max_age": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "samesite": "lax"
            }

            if settings.SECURE_COOKIES:
                cookie_kwargs["secure"] = True

            response.set_cookie(**cookie_kwargs)

            logger.info(f"User {user.username} successfully logged in")
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Произошла внутренняя ошибка сервера"
            )

    @app.post("/auth/logout")
    async def logout_user():
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        return response

    logger.info("Application started successfully")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)