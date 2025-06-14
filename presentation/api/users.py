from fastapi import APIRouter, HTTPException, Depends
from presentation.factory import ServiceFactory
from application.dto.user_dto import UserCreateDTO, UserDTO
from typing import List


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserDTO)
def create_user(user_dto: UserCreateDTO, service=Depends(ServiceFactory.create_user_service)):
    return service.create_user(user_dto)


@router.get("/{user_id}", response_model=UserDTO)
def get_user(user_id: int, service=Depends(ServiceFactory.create_user_service)):
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserDTO])
def get_all_users(service=Depends(ServiceFactory.create_user_service)):
    return service.get_all_users()


@router.delete("/{user_id}")
def delete_user(user_id: int, service=Depends(ServiceFactory.create_user_service)):
    service.delete_user(user_id)
    return {"message": "User deleted successfully"}