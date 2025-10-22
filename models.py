import uuid
import random
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
    DateTime,
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


class User(Base, BaseModel):
    __tablename__ = "users"

    username = Column(String)
    phone_number = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    photo = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password = Column(String, nullable=False)

    codes = relationship("VerifyUser")
    posts = relationship("Post")
    comments = relationship("Comment")

    def generate_code(self, db):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(5)])
        verify = VerifyUser(code=code, user_id=self.id)
        db.add(verify)
        db.commit()
        return code


class VerifyUser(Base, BaseModel):
    __tablename__ = "verifies"

    code = Column(String, nullable=False)
    is_verifyied = Column(Boolean, default=False)
    

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="codes")


class Post(Base, BaseModel):
    __tablename__ = "posts"

    caption = Column(TEXT)
    image = Column(String)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")

    likes = relationship("PostLike", back_populates="post")


class Comment(Base, BaseModel):
    __tablename__ = "comments"

    comment = Column(TEXT)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="comments")

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    post = relationship("Post")

    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"))
    comment = relationship("Comment", back_populates="child")
    child = relationship("Comment")


class PostLike(Base, BaseModel):
    __tablename__ = "postlikes"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    post = relationship("Post", back_populates="likes")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User")


class CommentLike(Base, BaseModel):
    __tablename__ = "commentlikes"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User")

    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"))
    comment = relationship("Comment")


class Follow(Base, BaseModel):
    __tablename__ = "follows"

    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    follower = relationship("User")

    # followee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    # followee = relationship("User")
