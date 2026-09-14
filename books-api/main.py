from fastapi import FastAPI, HTTPException
from pydantic import BaseModel   # ← 追加

app = FastAPI(title="Books API", description="本を管理するシンプルなREST API")


# リクエストで受け取る本の情報の「形」を決める
class BookIn(BaseModel):
    title: str
    author: str


books = [
    {"id": 1, "title": "はじめてのWeb API", "author": "山田太郎"},
    {"id": 2, "title": "RESTがわかる本", "author": "鈴木花子"},
]
next_id = 3   # 次に追加する本のID


@app.get("/books")
def get_books():
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="本が見つかりません")


# 新しい本を追加する（POST /books）
@app.post("/books", status_code=201)
def create_book(book: BookIn):
    global next_id
    new_book = {"id": next_id, "title": book.title, "author": book.author}
    books.append(new_book)
    next_id += 1
    return new_book

