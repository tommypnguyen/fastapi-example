from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
import psycopg2
import time
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Title: str, content: str
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="w1l4a7d8k9b10c11r12",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successfull")
        break
    except Exception as e:
        print("Connecting to database failed with error: {}".format(e))
        time.sleep(2)

# looks at request, then looks for matching url path
@app.get("/")
async def root():
    return {"message": "welcome to my api"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}


@app.get("/posts")
def get_posts():
    query = "SELECT * FROM posts"
    cursor.execute(query)
    posts = cursor.fetchall()
    return {"data": posts}


# id field is a path parameter
@app.get("/posts/{id}")
def get_post(id: int):
    query = """SELECT * FROM posts WHERE id = %s"""
    cursor.execute(query, (id,))
    post = cursor.fetchone()
    if post:
        return {"data": post}
    # response.status_code = status.HTTP_404_NOT_FOUND
    # return {"message": "No post with id:{} found".format(id)}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No post with id:{} found".format(id),
    )


# extracts all the fields from the request body and stores it in the payload dictionary
# payload: dict = Body(...)

# w/ post class passed in, fastAPI will validate that whatever data we receive matches the Post class
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # Format leaves you vulernable to sql injection when u do string interpolation
    query = """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *"""
    cursor.execute(query, (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    conn.commit()

    return {"data": new_post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    query = """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"""
    cursor.execute(query, (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post with id: {} found".format(id),
        )
    conn.commit()
    return {"data": updated_post}


@app.delete("/posts/{id}")
def delete_post(id: int):
    query = """DELETE FROM posts WHERE id = %s RETURNING *"""
    cursor.execute(query, (id,))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post with id: {} found".format(id),
        )
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
