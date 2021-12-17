from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostVotes])
def get_posts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # Psycog way
    # query = "SELECT * FROM posts"
    # cursor.execute(query)
    # posts = cursor.fetchall()

    # sqlalchemy way
    results = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return results


# id field is a path parameter
@router.get("/{id}", response_model=schemas.PostVotes)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.get_current_user),
):
    # query = """SELECT * FROM posts WHERE id = %s"""
    # cursor.execute(query, (id,))
    # post = cursor.fetchone()
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )
    if post:
        return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No post with id:{} found".format(id),
    )


# extracts all the fields from the request body and stores it in the payload dictionary
# payload: dict = Body(...)

# w/ post class passed in, fastAPI will validate that whatever data we receive matches the Post class
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    post: schemas.Post,
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.get_current_user),
):
    # Format leaves you vulernable to sql injection when u do string interpolation
    # query = """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *"""
    # cursor.execute(query, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # conn.commit()
    # Unpacks all fields for us, convenient because if we add a new field, no need to chagne anything
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int,
    post: schemas.Post,
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.get_current_user),
):
    # query = """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"""
    # cursor.execute(query, (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    current_post = post_query.first()
    if not current_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post with id: {} found".format(id),
        )
    if current_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    post_query.update(post.dict())
    db.commit()
    return post_query.first()


@router.delete("/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.get_current_user),
):
    # query = """DELETE FROM posts WHERE id = %s RETURNING *"""
    # cursor.execute(query, (id,))
    # deleted_post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id)
    current_post = post.first()
    if not current_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post with id: {} found".format(id),
        )
    if current_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    post.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
