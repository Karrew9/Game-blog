from fastapi import APIRouter, HTTPException, Depends
from typing import List
from presentation.factory import ServiceFactory
from application.dto.post_dto import PostCreateDTO, PostDTO


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostDTO)
def create_post(post_dto: PostCreateDTO, service=Depends(ServiceFactory.create_post_service)):
    try:
        return service.create_post(post_dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{post_id}", response_model=PostDTO)
def get_post(post_id: int, service=Depends(ServiceFactory.create_post_service)):
    post = service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/", response_model=List[PostDTO])
def get_all_posts(service=Depends(ServiceFactory.create_post_service)):
    return service.get_all_posts()


@router.get("/author/{author_id}", response_model=List[PostDTO])
def get_posts_by_author(author_id: int, service=Depends(ServiceFactory.create_post_service)):
    return service.get_posts_by_author(author_id)


@router.delete("/{post_id}")
def delete_post(post_id: int, service=Depends(ServiceFactory.create_post_service)):
    service.delete_post(post_id)
    return {"message": "Post deleted successfully"}