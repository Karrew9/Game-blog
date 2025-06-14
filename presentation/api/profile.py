from fastapi import APIRouter, Depends, HTTPException
from presentation.factory import ServiceFactory
from application.dto.post_dto import PostDTO
from typing import List
from core.security import get_current_user


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/posts", response_model=List[PostDTO])
def get_user_posts(
    user_id: int,
    service=Depends(ServiceFactory.create_post_service),
    current_user=Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return service.get_posts_by_user(user_id)


@router.put("/posts/{post_id}", response_model=PostDTO)
def update_user_post(
    post_id: int,
    post_data: PostDTO,
    service=Depends(ServiceFactory.create_post_service),
    current_user=Depends(get_current_user)
):
    post = service.get_post_by_id(post_id)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return service.update_post(post_id, post_data)


@router.delete("/posts/{post_id}")
def delete_user_post(
    post_id: int,
    service=Depends(ServiceFactory.create_post_service),
    current_user=Depends(get_current_user)
):
    post = service.get_post_by_id(post_id)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    service.delete_post(post_id)
    return {"message": "Post deleted successfully"}