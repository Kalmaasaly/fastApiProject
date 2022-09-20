import time

import psycopg2
from fastapi import FastAPI, Response, status, HTTPException, Depends

from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    # id: int
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "title of post 2", "content": "content of post 2", "id": 2}]
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='postgres',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was Successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Hello My World"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status":"success"}



@app.get("/posts")
def get_posts():
    cursor.execute("""select * from fastapi.posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


def find_post(id):
    for p in my_posts:
        if p['id'] == int(id):
            return p


def find_index_post(id):
    print(type(id))
    for i, p in enumerate(my_posts):
        if p['id'] == int(id):
            return i


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(""" select * from fastapi.posts where id = %s """, str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found")
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""insert into fastapi.posts( title, content, published) 
    values (%s,%s,%s) returning *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(""" delete  from fastapi.posts where id=%s returning *""", str(id))
    deleted_post = cursor.fetchone()
    conn.commit();
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" update fastapi.posts set content = %s ,title = %s , published = %s  where id= %s returning *""",
                   (post.content, post.title, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not exist")
    return {"data": updated_post}
    # Response(status_code=status.HTTP_204_NO_CONTENT)
