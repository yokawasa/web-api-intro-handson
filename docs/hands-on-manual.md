# 【実習】APIを作って動かす（55分）― 講師用詳細資料

**講座名**：AI時代のWeb API入門 ― つくって学ぶ、これからの必須スキル（3時間版）
**対象パート**：第3章 実習（PC実習版）
**実習環境**：GitHub Codespaces（受講者のPCへのインストールは不要）
**使用技術**：Python 3.12 / FastAPI / Uvicorn
**題材**：本（book）を管理するシンプルなREST API

> この資料は講師が実習を進行するための台本兼サンプルコード集です。受講者に配布する場合は「講師メモ」を除いてお使いください。

---

## この実習のゴール

受講者が自分の手で、次の3つのエンドポイントを持つWeb APIを動かせるようになる。

| メソッド | パス | 役割 |
|---|---|---|
| GET | `/books` | 本の一覧を取得する |
| GET | `/books/{book_id}` | 本を1件取得する |
| POST | `/books` | 本を新しく追加する |

さらに、**わざとエラーを起こして4xxを体験する**ことで、第2章で学んだステータスコードが実際にどう返るかを腹落ちさせる。

---

## タイムテーブル（55分）

| 時間 | 節 | 内容 |
|---|---|---|
| 8分 | 3-1 | 環境確認・題材の説明 |
| 12分 | 3-2 | GETエンドポイントを作る |
| 12分 | 3-3 | POSTでデータを追加する |
| 13分 | 3-4 | APIクライアントで動作確認 |
| 10分 | 3-5 | わざとエラーを起こしてみる |

---

## 3-1. 環境確認・題材の説明（8分）

### 実習環境：GitHub Codespaces

本実習は **GitHub Codespaces** で行う。受講者のPCには**何もインストールさせない**。
ブラウザ上でVS Code・ターミナル・Python・FastAPIがすべて揃った状態から始められるため、
「環境構築でつまずいて実習が進まない」という事故を構造的に潰せる。

受講者の事前準備は `docs/participant-prep.md` を配布して案内しておく（GitHubアカウント作成が唯一の必須作業）。

### 環境の起動手順（受講者に画面共有しながら一緒に進める）

1. 講師がリポジトリURL（`https://github.com/yokawasa/web-api-introduction`）を共有する
2. 緑色の **「Code」** ボタン → **「Codespaces」** タブ → **「Create codespace on main」** をクリック
3. ブラウザ上にVS Codeが起動する（初回1〜2分）。この間に題材の説明をしておくとよい
4. 起動が完了すると、FastAPI・uvicornは**インストール済み**の状態になっている

> **講師メモ**：`.devcontainer/devcontainer.json` の `postCreateCommand` で依存関係を自動インストールしている。
> バージョンは `.devcontainer/requirements.txt` で固定済み（fastapi 0.115.6 / uvicorn 0.34.0）なので、
> 「昨日まで動いていたのに今日は動かない」という事故が起きない。

### 環境が起動したことの確認

画面下部のターミナルで、以下を実行して確認する。

```bash
python --version          # Python 3.12.x と表示される
python -m uvicorn --version   # uvicorn のバージョンが表示される
```

> **講師メモ / 重要**：起動コマンドは終始 `python -m uvicorn ...` の形で統一する。
> `uvicorn` 単体でも動くが、`python -m` を付ける形を身体で覚えてもらうと、
> 受講者が後日ローカル環境で再現するときに `uvicorn: command not found` で詰まらない。

### 作業フォルダーに移動する

```bash
cd books-api
```

このフォルダーに `main.py` を作っていく。

> **講師メモ**：リポジトリには完成版の `books-api/main.py` が既に置いてある。
> 実習では**受講者に一から書いてもらう**ため、開始前に中身を空にしておくか、
> 受講者用ブランチ（例：`hands-on-start`）を用意して、そちらからCodespaceを作らせる運用が安全。
> 遅れた受講者には「付録Aをコピペ」で追いつかせる。

### 題材の説明

「本を管理するAPI」を作る。今回はデータベースの代わりに、プログラムの中の**リスト（配列）**にデータを持たせる。こうすることでDBの準備なしに「APIの本質＝リクエストを受けてレスポンスを返す」だけに集中できる。

---

## 3-2. GETエンドポイントを作る（12分）

作業フォルダーに `main.py` を作成し、まずは「一覧取得」と「1件取得」を書く。

```python
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Books API", description="本を管理するシンプルなREST API")

# 本を保存しておく場所（今回はメモリ上のリストで代用）
books = [
    {"id": 1, "title": "はじめてのWeb API", "author": "山田太郎"},
    {"id": 2, "title": "RESTがわかる本", "author": "鈴木花子"},
]


# 一覧を取得する（GET /books）
@app.get("/books")
def get_books():
    return books


# 1件だけ取得する（GET /books/{book_id}）
@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    # 見つからなければ 404 を返す
    raise HTTPException(status_code=404, detail="本が見つかりません")
```

### サーバーを起動する

```bash
python -m uvicorn main:app --reload
```

- `main` … ファイル名（`main.py`）
- `app` … コード内の `app = FastAPI()` の変数名
- `--reload` … コードを保存すると自動で再起動（開発用に便利）

起動に成功すると `Uvicorn running on http://127.0.0.1:8000` と表示される。

### ブラウザで確認（Codespacesのポートフォワード）

Codespacesはクラウド上で動いているため、**自分のPCのブラウザに `127.0.0.1:8000` と入力しても開けない**。
代わりに、Codespacesが自動で発行する**公開URL**を使う。

1. サーバーを起動すると、画面右下に「ポート8000が利用可能になりました」という通知が出る
2. 通知の **「ブラウザーで開く」** をクリックする
3. 新しいタブで `https://＜ランダムな文字列＞-8000.app.github.dev` のようなURLが開く

通知を見逃した場合は、ターミナル横の **「ポート」タブ** から、ポート8000の「ローカルアドレス」にカーソルを合わせて地球儀アイコンをクリックしても開ける。

このURLの末尾にパスを付けて動作を確認する。

- `＜公開URL＞/books` → 本の一覧（JSON）が表示される
- `＜公開URL＞/books/1` → id=1 の本だけが表示される

> **講師メモ / 必ず押さえる**：ここは受講者が最も混乱する箇所。
> 「サーバーはクラウドの中で `127.0.0.1:8000` として動いていて、Codespacesがそれを外から見えるURLに橋渡ししている」
> と図で説明すると腹落ちしやすい。**ターミナルの表示（127.0.0.1）とブラウザのURL（app.github.dev）が違ってよい**ことを明言しておく。
>
> なお初期状態のポートは**Private**（本人だけがアクセス可能）。受講者同士でURLを共有させたい場合は
> 「ポート」タブで右クリック →「ポートの表示範囲」→「Public」に変更する。第4章のデモで使える。

### 自動生成ドキュメントを見せる

> **講師メモ / ここで必ず触れる**：`＜公開URL＞/docs` を開くと、FastAPIが**自動生成したAPIドキュメント（Swagger UI）**が表示される。「コードを書いただけで仕様書が出てくる」ことを見せると盛り上がる。第4章「AIが使いやすいAPI」の伏線になる（この仕様＝OpenAPIをAIが読んでAPIを呼び出す）。

### コード解説のポイント（受講者への問いかけ）

- `@app.get("/books")` の "get" と "/books" は何を表している？ → 第2章のメソッドとパス
- URLの `{book_id}` が関数の引数 `book_id` に渡ってくる（パスパラメータ）
- `book_id: int` と型を書くと、数字以外が来たとき自動でエラーにしてくれる

---

## 3-3. POSTでデータを追加する（12分）

「本を追加する」機能を足す。POSTでは**リクエストボディ（JSON）**でデータを受け取る。受け取るデータの形を `BaseModel` で定義するのがFastAPI流。

`main.py` の先頭付近と末尾に、以下を追記する。

```python
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
```

### コード解説のポイント

- `class BookIn(BaseModel)` … 受け取るJSONは `title` と `author` を持つ、という「約束」
- `status_code=201` … 「新しく作成した」ことを表すステータスコード（第2章の復習）
- `id` はクライアントに指定させず、サーバー側で採番する（設計の勘所）

> **講師メモ**：`--reload` で起動していれば保存だけで反映される。ここで `/docs` を再度開くと、POSTが追加され、ブラウザ上から「Try it out」で実行できることも見せられる。

---

## 3-4. APIクライアントで動作確認（13分）

GETはブラウザで確認できるが、POSTはブラウザのアドレスバーからは送れない。そこで**APIクライアント**を使う。
まず**全員が確実に成功する** `/docs`（Swagger UI）から入り、そのあと同じことを `curl` で再現する、という順で進める。

### ① Swagger UI から実行する（まずはこれ）

1. ブラウザで `＜公開URL＞/docs` を開く
2. **POST /books** の行をクリックして展開する
3. 右上の **「Try it out」** をクリック
4. Request bodyの欄を、以下のように書き換える

   ```json
   {
     "title": "テスト駆動API入門",
     "author": "田中三郎"
   }
   ```

5. **「Execute」** をクリック
6. 下に表示される **Server response** を確認する
   - **Code** が `201` になっている
   - **Response body** に `"id": 3` の本が返っている

7. 続けて **GET /books** を同じ手順で実行し、追加した本が一覧に入っていることを確認する

> **講師メモ**：ここが本実習の山場。**ブラウザだけでPOSTが送れる**ので、
> コマンドの打ち間違い・クォートの種類・PATHといった本質的でないトラブルがゼロになる。
> 全員が `201` を見られたことを確認してから、次のcurlに進むこと。

### ② curl で同じことをする

「GUIがやっているのは、結局この通信である」と示すパート。
Codespacesのターミナルで実行するので、**ここでは `127.0.0.1:8000` を使う**（サーバーと同じマシンの中から呼ぶため）。

サーバーは起動したままにしておきたいので、**ターミナルをもう1枚開く**。

- ターミナル右上の **「+」** をクリックすると、新しいターミナルが開く
- 開いたら `cd books-api` で作業フォルダーに移動しておく

```bash
# 1) 一覧を取得（GET）
curl http://127.0.0.1:8000/books

# 2) 1件取得（GET）
curl http://127.0.0.1:8000/books/1

# 3) 本を追加（POST） ※ヘッダーでJSONだと伝え、-d でボディを送る
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "テスト駆動API入門", "author": "田中三郎"}'

# 4) 追加されたか、もう一度一覧を取得して確認
curl http://127.0.0.1:8000/books
```

期待される結果：3) で新しい本が返り、4) の一覧に追加された本が含まれている。

> **講師メモ**：IDは実習中にPOSTした回数で変わる（初回なら `id: 3`）。
> 「`3` にならない人？」と聞くと混乱するので、**「新しい番号が振られていればOK」**と伝える。

### ③ ステータスコードも見てみる

```bash
# -i を付けるとレスポンスヘッダー（ステータスコード）も表示される
curl -i http://127.0.0.1:8000/books/1
```

先頭に `HTTP/1.1 200 OK` と出る。POSTで追加したときは `201 Created` になることも確認する。

> **講師メモ**：Codespacesのターミナルは**Linuxのbash**なので、シングルクォートがそのまま使える。
> 従来のWindows/PowerShellのクォート問題は、Codespacesを使うことで発生しない。
> ただし受講者が**後日ローカルのPowerShellで再現する**ときには問題になるため、
> 「自分のPCでやるときはクォートの扱いが違う」とだけ触れ、詳細は付録Dに逃がす。
>
> 時間に余裕があれば、GUIクライアント（Postman Web）で同じPOSTを送るところも見せるとよい。
> その場合は**公開URL**（`https://...app.github.dev`）を使い、ポートを**Public**に変更しておく必要がある。

---

## 3-5. わざとエラーを起こしてみる（10分）

「うまくいく」だけでなく「失敗したときにどう返るか」を体験する。エラーは敵ではなく、**クライアントに状況を正しく伝える大事な仕組み**であることを理解してもらう。

以下はcurlの例だが、**`/docs` の「Try it out」でも同じことが再現できる**（②③はブラウザからのほうが分かりやすい）。
curlがうまく打てない受講者には `/docs` 側で試させ、全員がステータスコードを目にできる状態にする。

### ① 存在しない本を取得 → 404

```bash
curl -i http://127.0.0.1:8000/books/999
```

結果：`HTTP/1.1 404 Not Found` と `{"detail":"本が見つかりません"}` が返る。
→ コード中の `raise HTTPException(status_code=404, ...)` が効いている。

### ② 数字でないIDを指定 → 422（自動バリデーション）

```bash
curl -i http://127.0.0.1:8000/books/abc
```

結果：`HTTP/1.1 422 Unprocessable Entity`。
→ `book_id: int` と型を書いたおかげで、FastAPIが自動で弾いてくれる。

### ③ 必須項目が足りないPOST → 422

```bash
# author を送らずに追加しようとする
curl -i -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "著者がない本"}'
```

結果：`422` と「author が必要」という趣旨のエラー。
→ `BaseModel` で `author: str` を必須にしているから。

### まとめの問いかけ

- 200・201・404・422 はそれぞれ「誰の」「どういう状況」を表している？
- エラーメッセージが分かりやすいと、APIを使う相手（人間もAIも）は何が助かる？
  → 第4章「AIにとって使いやすいAPI」へつなぐ

---

## 付録A. 完成版 `main.py`（全文）

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Books API", description="本を管理するシンプルなREST API")


# リクエストで受け取る本の情報の「形」を決める
class BookIn(BaseModel):
    title: str
    author: str


# 本を保存しておく場所（今回はメモリ上のリストで代用）
books = [
    {"id": 1, "title": "はじめてのWeb API", "author": "山田太郎"},
    {"id": 2, "title": "RESTがわかる本", "author": "鈴木花子"},
]
next_id = 3


@app.get("/books")
def get_books():
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="本が見つかりません")


@app.post("/books", status_code=201)
def create_book(book: BookIn):
    global next_id
    new_book = {"id": next_id, "title": book.title, "author": book.author}
    books.append(new_book)
    next_id += 1
    return new_book
```

## 付録B. 実行手順まとめ（1枚チートシート）

```bash
# 1. 環境を開く（ブラウザ）
#    https://github.com/yokawasa/web-api-introduction
#    → Code → Codespaces → Create codespace on main
#    ※ FastAPI / uvicorn はインストール済み

# 2. 作業フォルダーへ移動して main.py を作成（付録A）
cd books-api

# 3. 起動
python -m uvicorn main:app --reload
#    → 右下の通知「ブラウザーで開く」から公開URLを開く
#    → ＜公開URL＞/docs で自動ドキュメントが見られる

# 4. 動作確認（ターミナルをもう1枚開いて実行）
curl http://127.0.0.1:8000/books
curl http://127.0.0.1:8000/books/1
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"テスト駆動API入門","author":"田中三郎"}'

# 5. エラー体験
curl -i http://127.0.0.1:8000/books/999   # 404
curl -i http://127.0.0.1:8000/books/abc   # 422
```

### URLの使い分け（最重要）

| どこから叩くか | 使うURL |
|---|---|
| Codespacesのターミナル（curl） | `http://127.0.0.1:8000` |
| 自分のPCのブラウザ / Postman | `https://＜ランダム文字列＞-8000.app.github.dev` |

## 付録C. よくあるつまずき（講師用トラブルシュート）

### Codespaces環境まわり

| 症状 | 原因 | 対処 |
|---|---|---|
| ブラウザで `127.0.0.1:8000` が開けない | Codespacesはクラウド上で動いているため | 「ポート」タブから**公開URL**を開く。最頻出のつまずき |
| ポート通知を見逃した | 通知が自動で消えた | ターミナル横の「ポート」タブ → ポート8000の地球儀アイコン |
| 公開URLで `502` が出る | サーバーがまだ起動しきっていない | 数秒待ってリロード。ターミナルに `Application startup complete` が出ているか確認 |
| 公開URLを他人と共有できない | ポートが Private のまま | 「ポート」タブで右クリック →「ポートの表示範囲」→ Public |
| Codespaceの作成に失敗する | 無料枠超過 / 組織のポリシー | 個人アカウントで再試行。不可なら付録Dのローカル手順へ |
| しばらく放置したら切断された | 30分無操作で自動停止 | ブラウザをリロードすれば再開できる（**書いたコードは消えない**） |
| ターミナルが見当たらない | パネルが閉じている | 上部メニュー →「Terminal」→「New Terminal」 |

### アプリケーションまわり

| 症状 | 原因 | 対処 |
|---|---|---|
| `uvicorn: command not found` | PATHが通っていない | `python -m uvicorn main:app --reload` で起動（本資料はこの形で統一） |
| `Address already in use` | 前のサーバーが残っている | 元のターミナルで `Ctrl + C`。または `--port 8001` で別ポート指定 |
| `Error loading ASGI app` | `main.py` のある場所にいない | `cd books-api` を実行してから起動する |
| POSTで`422`が出続ける | JSONの形やヘッダー不足 | `Content-Type: application/json` とキー名を確認。`/docs` から送らせるのが確実 |
| コード変更が反映されない | `--reload` を付けていない | 起動コマンドに `--reload` を追加 |
| `IndentationError` が出る | Pythonのインデントずれ | 半角スペース4つで揃っているか確認 |

## 付録D. ローカル環境で実施する場合（代替手順）

Codespacesが使えない受講者向けのフォールバック。講座後に自分のPCで再現したい人にも案内できる。

### 手順

```bash
# 1. リポジトリを取得
git clone https://github.com/yokawasa/web-api-introduction.git
cd web-api-introduction/books-api

# 2. 仮想環境を作って有効化
python -m venv .venv

#   macOS / Linux
source .venv/bin/activate
#   Windows（PowerShell）
.venv\Scripts\Activate.ps1

# 3. ライブラリをインストール
pip install -r ../.devcontainer/requirements.txt

# 4. 起動
python -m uvicorn main:app --reload
#   → ブラウザで http://127.0.0.1:8000/docs
```

ローカルの場合は `127.0.0.1:8000` が**そのままブラウザで開ける**（ポートフォワードの話は不要）。

### Windows（PowerShell）でのcurl注意点

PowerShellの `curl` は `Invoke-WebRequest` の別名なので、本資料のコマンドはそのままでは動かない。
`curl.exe` と明示し、**ダブルクォートをエスケープ**する。

```powershell
curl.exe -X POST http://127.0.0.1:8000/books `
  -H "Content-Type: application/json" `
  -d '{\"title\":\"テスト駆動API入門\",\"author\":\"田中三郎\"}'
```

> **講師メモ**：この面倒さこそが、実習をCodespacesに寄せた理由そのもの。
> 時間が余ったときに「ローカルだとこうなる」と見せると、環境差の実感につながる。

---

*本資料のサンプルコードは動作ロジックを検証済みです（GET一覧=200 / GET1件=200 / 存在しないID=404 / POST追加=201）。*
