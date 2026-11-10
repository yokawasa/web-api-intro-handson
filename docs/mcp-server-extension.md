# ハンズオン付録: MCPサーバー機能追加

この付録では、[【実習】ハンズオン手順書](hands-on-manual.md)で作成した本（book）を管理するREST APIに、MCPサーバー機能を追加します。

既存のFastAPIエンドポイントをMCPツールとして公開し、MCPクライアントから利用できるようにします。

---

## この付録のゴール

- FastAPI-MCPをインストールします
- 既存の `main.py` にMCPサーバー機能を追加します
- MCPサーバーを `/mcp` で利用できるようにします

> この付録は、先に[【実習】ハンズオン手順書](hands-on-manual.md)を最後まで実施し、Books APIが動作していることを前提としています。

---

## 1. 作業フォルダーに移動する

Codespacesのターミナルで、次のコマンドを実行します。

```bash
cd books-api
```

すでに `books-api` フォルダーにいる場合は、この操作は不要です。現在のフォルダーは次のコマンドで確認できます。

```bash
pwd
```

---

## 2. FastAPI-MCPをインストールする

FastAPI-MCPと、互換性を確認済みのMCP Python SDK・Pydanticをインストールします。

```bash
python -m pip install \
  "fastapi-mcp==0.4.0" \
  "mcp==1.12.1" \
  "pydantic==2.10.6"
```

`mcp` と `pydantic` のバージョンも固定するのは、FastAPI-MCP 0.4.0と新しいバージョンのMCP Python SDK・Pydanticとの間で、内部APIの互換性が保たれていないためです。

インストールされたバージョンを確認します。

```bash
python -m pip show fastapi-mcp mcp pydantic
```

次のバージョンが表示されることを確認してください。

```text
Name: fastapi-mcp
Version: 0.4.0
...
Name: mcp
Version: 1.12.1
...
Name: pydantic
Version: 2.10.6
```

最後に、インストールしたパッケージ間の依存関係に問題がないことを確認します。

```bash
python -m pip check
```

`No broken requirements found.` と表示されたら、実際にモジュールを読み込めることも確認します。

```bash
python -c "from fastapi_mcp import FastApiMCP; print('import OK')"
```

`import OK` と表示されれば、インストールは完了です。

> 📝 `pip check` だけでは検出できない互換性問題
>
> `pip check` は、各パッケージが宣言しているバージョン条件を確認します。今回のように、宣言上は条件を満たしていても内部APIに互換性がない問題は検出できません。そのため、上記のimport確認も行います。

> 📝 パッケージ名とimport名の違い
>
> インストール時のパッケージ名は `fastapi-mcp` ですが、Pythonコードから読み込むときは `fastapi_mcp` と記述します。

---

## 3. `main.py` にMCPサーバー機能を追加する

`main.py` の末尾に、次の3行を追加します。

```python
from fastapi_mcp import FastApiMCP

mcp = FastApiMCP(app)

# Streamable HTTP
mcp.mount_http()
# SSE
# mcp.mount()
```

追加する場所は、`get_books`、`get_book`、`create_book` など、すべてのエンドポイントを定義した後です。完成後の末尾は次のようになります。

```python
@app.post("/books", status_code=201)
def create_book(book: BookIn):
    global next_id
    new_book = {"id": next_id, "title": book.title, "author": book.author}
    books.append(new_book)
    next_id += 1
    return new_book


from fastapi_mcp import FastApiMCP

mcp = FastApiMCP(app)
mcp.mount_http()
```

`FastApiMCP(app)` は、その時点で定義済みのFastAPIエンドポイントを読み取り、MCPツールへ変換します。そのため、この処理はすべてのエンドポイント定義より後に記述します。

---

## 4. サーバーを起動する

すでにUvicornを起動している場合は、起動中のターミナルで `Ctrl + C` を押して一度停止します。その後、`books-api` フォルダーで次のコマンドを実行します。

```bash
python -m uvicorn main:app --reload
```

起動に成功すると、次のようなメッセージが表示されます。

```text
Uvicorn running on http://127.0.0.1:8000
```

既存のBooks APIも引き続き利用できます。別のターミナルを開き、次のコマンドで確認します。

```bash
curl http://127.0.0.1:8000/books
```

---

## 5. `/mcp` エンドポイントを確認する

Uvicornを起動したまま、別のターミナルで次のコマンドを実行します。

```bash
curl -N \
  -H "Accept: text/event-stream" \
  http://127.0.0.1:8000/mcp
```

接続に成功すると、`event: endpoint` から始まる情報が表示され、MCPクライアントからの接続を待つ状態になります。確認後は `Ctrl + C` でcurlを終了します。

> 📝 `/mcp` は通常のWebページではありません
>
> `/mcp` はMCPクライアントが接続するためのエンドポイントです。ブラウザで開いたときに一般的なWebページが表示されなくても、異常ではありません。また、FastAPIの `/docs` に `/mcp` が表示されないことも正常です。

Codespacesの外部にあるMCPクライアントから接続する場合は、ポート8000の公開URLを使用します。

```text
https://＜ランダムな文字列＞-8000.app.github.dev/mcp
```

この場合は、Codespacesの「ポート」タブでポート8000の公開範囲を、接続方法に合わせて設定してください。

---

## よくあるエラー

### `ModuleNotFoundError: No module named 'fastapi_mcp'`

Uvicornが使用しているPython環境にFastAPI-MCPがインストールされていません。次のコマンドを実行してから、Uvicornを再起動します。

```bash
python -m pip install \
  "fastapi-mcp==0.4.0" \
  "mcp==1.12.1" \
  "pydantic==2.10.6"
```

### `TypeError: Server.__init__() takes 2 positional arguments but 3 were given`

FastAPI-MCP 0.4.0と互換性のない新しいバージョンのMCP Python SDKがインストールされています。現在のバージョンを確認します。

```bash
python -m pip show fastapi-mcp mcp
```

`mcp` が `2.x` になっている場合は、互換性を確認済みの組み合わせへ変更します。

```bash
python -m pip install \
  "fastapi-mcp==0.4.0" \
  "mcp==1.12.1" \
  "pydantic==2.10.6"
```

変更後、依存関係を確認してからUvicornを再起動します。

```bash
python -m pip check
python -c "from fastapi_mcp import FastApiMCP; print('import OK')"
python -m uvicorn main:app --reload
```

### `ImportError: cannot import name 'eval_type_backport'`

MCP Python SDK 1.12.1と互換性のない新しいバージョンのPydanticがインストールされています。現在のバージョンを確認します。

```bash
python -m pip show pydantic
```

Pydanticが `2.10.6` 以外になっている場合は、互換性を確認済みの組み合わせへ変更します。

```bash
python -m pip install \
  "fastapi-mcp==0.4.0" \
  "mcp==1.12.1" \
  "pydantic==2.10.6"
```

変更後、import確認を行ってからUvicornを再起動します。

```bash
python -c "from fastapi_mcp import FastApiMCP; print('import OK')"
python -m uvicorn main:app --reload
```

### `Error loading ASGI app. Could not import module "main"`

`main.py` があるフォルダーとは別の場所でUvicornを起動している可能性があります。

```bash
cd books-api
python -m uvicorn main:app --reload
```

### MCPツールにBooks APIのエンドポイントが含まれない

`mcp = FastApiMCP(app)` をエンドポイント定義より前に記述している可能性があります。MCP関連の3行を `main.py` の末尾へ移動し、Uvicornを再起動します。

---

## 追加後の構成

```text
Books API
├── GET  /books
├── GET  /books/{book_id}
├── POST /books
└── MCP  /mcp
```

これで、通常のREST APIとして利用できるBooks APIに、MCPサーバー機能が追加されました。
