from fastapi import APIRouter, HTTPException, Depends
from typing import List
from presentation.factory import ServiceFactory
from application.dto.comment_dto import CommentCreateDTO, CommentDTO


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentDTO)
def create_comment(comment_dto: CommentCreateDTO, service=Depends(ServiceFactory.create_comment_service)):
    try:
        return service.create_comment(comment_dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{comment_id}", response_model=CommentDTO)
def get_comment(comment_id: int, service=Depends(ServiceFactory.create_comment_service)):
    comment = service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("/", response_model=List[CommentDTO])
def get_all_comments(service=Depends(ServiceFactory.create_comment_service)):
    return service.get_all_comments()


@router.get("/post/{post_id}", response_model=List[CommentDTO])
def get_comments_by_post(post_id: int, service=Depends(ServiceFactory.create_comment_service)):
    return service.get_comments_by_post(post_id)


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, service=Depends(ServiceFactory.create_comment_service)):
    service.delete_comment(comment_id)
    return {"message": "Comment deleted successfully"}