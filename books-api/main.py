from fastapi import FastAPI

app = FastAPI(title="Books API", description="本を管理するシンプルなREST API")


# 疎通確認用のエンドポイント（GET /）
@app.get("/")
def hello():
    return {"message": "hello"}
