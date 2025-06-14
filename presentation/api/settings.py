from fastapi import APIRouter, Depends, HTTPException
from presentation.factory import ServiceFactory
from application.dto.user_dto import UserUpdateDTO, UserDTO
from core.security import get_current_user


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=UserDTO)
def get_user_settings(
    current_user=Depends(get_current_user),
    service=Depends(ServiceFactory.create_user_service)
):
    return service.get_user_by_id(current_user.id)


@router.put("/", response_model=UserDTO)
def update_user_settings(
    user_data: UserUpdateDTO,
    current_user=Depends(get_current_user),
    service=Depends(ServiceFactory.create_user_service)
):
    return service.update_user(current_user.id, user_data)


@router.delete("/")
def delete_account(
    current_user=Depends(get_current_user),
    service=Depends(ServiceFactory.create_user_service)
):
    service.delete_user(current_user.id)
    return {"message": "Account deleted successfully"}