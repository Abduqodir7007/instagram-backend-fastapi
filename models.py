import uuid
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from config import settings
from sqlalchemy import (
    Column,
    INTEGER,
    String,
    ForeignKey,
    Boolean,
    DATETIME,
    TEXT,
)


class BaseModel:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class User(BaseModel, Base):
    __tablename__ = "users"

    username = Column(String())
    phone_number = Column(String(), nullable=True)
    email = Column(String(), unique=True, nullable=False)
    photo = Column(String(), nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)

    codes = relationship("VerifyUser")
    posts = relationship("Post")
    comments = relationship("Comment")


class VerifyUser(BaseModel, Base):
    __tablename__ = "verifies"

    code = Column(INTEGER, nullable=False)
    is_verifyied = Column(Boolean, default=False)
    expiration_time = Column(DATETIME, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="codes")


class Post(BaseModel, Base):
    __tablename__ = "posts"

    caption = Column(TEXT)
    image = Column(String)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")

    likes = relationship("PostLike", back_populates="post")


class Comment(BaseModel, Base):
    __tablename__ = "comments"

    comment = Column(TEXT)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="comments")

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    post = relationship("Post")

    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"))
    comment = relationship("Comment", back_populates="child")
    child = relationship("Comment")


class PostLike(BaseModel, Base):
    __tablename__ = "postlikes"

    post_id = Column(INTEGER, ForeignKey("posts.id"))
    post = relationship("Post", back_populates="likes")

    user_id = Column(INTEGER, ForeignKey("users.id"))
    user = relationship("User")


class CommentLike(BaseModel, Base):
    __tablename__ = "commentlikes"

    user_id = Column(INTEGER, ForeignKey("users.id"))
    user = relationship("User")

    comment_id = Column(INTEGER, ForeignKey("comments.id"))
    comment = relationship("Comment")


class Follow(BaseModel, Base):
    __tablename__ = "follows"

    follower_id = Column(INTEGER, ForeignKey("users.id"))
    follower = relationship("User")

    followee_id = Column(INTEGER, ForeignKey("users.id"))
    followee = relationship("User")
