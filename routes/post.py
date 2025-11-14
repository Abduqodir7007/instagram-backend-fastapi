from pydantic import BaseModel
from uuid import UUID

class PostCreate(BaseModel):
    caption: str


class PostCommentCreate(BaseModel):
    comment: str
    post_id: UUID
    
class PostLikeCreate(BaseModel):
    post_id: UUID

class PostResponse(BaseModel):
    id: UUID
    caption: str
    user_id: UUID
    likes_count: int | None = 0
    
    
    class Config:
        orm_mode = True
class CommentCreate(BaseModel):
    comment: str
    comment_id: UUID
    post_id: UUID

class CommentLikeCreate(BaseModel):
    comment_id: UUID




