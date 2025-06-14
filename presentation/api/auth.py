from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from core.logger import logger
from infrastructure.database.models import UserModel
from infrastructure.database.session import get_db
from core.security import (
    hash_password,
    create_access_token,
    authenticate_user
)
from core.config import settings
from datetime import timedelta, datetime

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")


@router.post("/auth/login")
async def login(
        request: Request,
        db: Session = Depends(get_db)
):
    form_data = await request.form()
    user = authenticate_user(
        db,
        username=form_data.get("username"),
        password=form_data.get("password")
    )

    if not user:
        # Возвращаем обратно в форму с ошибкой
        return templates.TemplateResponse(
            "login.html",  # Создайте отдельный шаблон для страницы входа
            {
                "request": request,
                "error": "Неверное имя пользователя или пароль"
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,  # Для HTTPS
        samesite="lax"
    )

    return response


@router.post("/auth/register", response_class=HTMLResponse)
async def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        db: Session = Depends(get_db)
):
    # Проверка совпадения паролей
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Пароли не совпадают"},
            status_code=400
        )

    try:
        # Создаем нового пользователя
        new_user = UserModel(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()

        # Создаем токен
        access_token = create_access_token(
            data={"sub": new_user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Устанавливаем куки и перенаправляем
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # True для HTTPS
            samesite="lax"
        )

        return response

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка регистрации: {str(e)}")
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Ошибка регистрации"},
            status_code=400
        )

@router.post("/auth/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response