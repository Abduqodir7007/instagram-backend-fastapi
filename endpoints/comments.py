from fastapi import APIRouter
from routes.post import CommentCreate, CommentLikeCreate
from security import get_current_user
from fastapi import Depends, status, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Post, CommentLike, Comment
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

routes = APIRouter(prefix="/comment", tags=["Comments"])


@routes.post("/comment/create-delete-like/{id}", status_code=status.HTTP_201_CREATED)
async def comment_like(
    like_in: CommentLikeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    comment_result = await db.execute(
        select(Comment).where(Comment.id == like_in.comment_id)
    )

    if not comment_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment does not exists"
        )

    result = await db.execute(
        select(CommentLike).where(
            CommentLike.user_id == user.id, CommentLike.comment_id == like_in.comment_id
        )
    )
    existing_comment = result.scalars().first()

    if result.scalars().first():
        await db.delete(existing_comment)
        await db.commit()
        return {"msg": "You disliked the comment"}
    else:
        new_comment_like = CommentLike(user_id=user.id, comment_id=like_in.comment_id)
        db.add(new_comment_like)
        await db.commit()
        return {"msg": "You liked the comment"}


@routes.get("/create", status_code=status.HTTP_200_OK)
async def comment_create_for_comment(
    comment_in: CommentCreate, db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Comment).where(Comment.id == comment_in.comment_id)
    )
    comment = result.scalars().first()

    result_post = await db.execute(select(Post).where(Post.id == comment_in.post_id))
    post = result_post.scalars().first()

    if not comment or not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment or Post does not exist",
        )

    new_comment = Comment(
        post_id=post.id, comment_id=comment.id, comment=comment_in.comment
    )

    db.add(new_comment)
    await db.commit()

    return {"message": "Comment created successfully"}
