from fastapi import APIRouter
from routes.post import PostCreate, CommentCreate, PostLikeCreate, CommentLikeCreate
from security import get_current_user
from fastapi import Depends, status, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Post, PostLike, CommentLike, Comment
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

routes = APIRouter(prefix="/post", tags=["Posts"])


@routes.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_post = Post(caption=post_in.caption, user_id=user.id)

    db.add(new_post)
    await db.commit()

    return {"success": True}


@routes.post("/comment", status_code=status.HTTP_201_CREATED)
async def create_comment(comment_in: CommentCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Post).where(Post.id == comment_in.post_id))

    if not result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Post does not exits"
        )

    new_comment = Comment(comment=comment_in.comment, post_id=comment_in.post_id)

    db.add(new_comment)
    await db.commit()

    return {"success": True}


@routes.post("/post/create-delete-like/{id}", status_code=status.HTTP_201_CREATED)
async def post_like(
    like_in: PostLikeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    post_result = await db.execute(select(Post).where(Post.id == like_in.post_id))
    if not post_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Post does not exists"
        )

    result = await db.execute(
        select(PostLike).where(
            PostLike.user_id == user.id, PostLike.post_id == like_in.post_id
        )
    )
    existing_like = result.scalars().first()
    if result.scalars().first():
        await db.delete(existing_like)
        await db.commit()
        return {"msg": "You disliked the post"}
    else:
        new_post_like = PostLike(user_id=user.id, post_id=like_in.post_id)
        db.add(new_post_like)
        await db.commit()
        return {"msg": "You liked the post"}


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
