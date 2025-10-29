from pydantic import BaseModel


class PostCreate(BaseModel):
    caption: str


class CommentCreate(BaseModel):
    comment: str
    post_id: int


class PostLikeCreate(BaseModel):
    post_id: int


class CommentLikeCreate(BaseModel):
    comment_id: int

