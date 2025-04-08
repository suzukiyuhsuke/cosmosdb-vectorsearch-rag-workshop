# FastAPI フレームワーク

FastAPIは、Pythonで高性能なWebAPIを構築するための現代的なWebフレームワークです。

## 主な特徴

- **高速**: Starlette（ASGI）とPydanticを活用した高パフォーマンス
- **自動ドキュメント生成**: OpenAPI（Swagger）とReDocによる自動API文書化
- **型ヒントベース**: Pythonの型アノテーションを使用した直感的な開発
- **非同期処理**: async/awaitによる効率的な非同期処理
- **依存性注入**: 再利用可能なコンポーネントの柔軟な構成

## 基本的な使い方

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## Pydanticモデル

FastAPIはPydanticを使用してデータバリデーションを行います：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## 依存性注入

依存性注入を使用して共通の機能を提供できます：

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def read_users(db: DBSession = Depends(get_db)):
    users = db.query(User).all()
    return users
```

## デプロイ

FastAPIアプリケーションは以下のいずれかでデプロイできます：

- Uvicorn（開発用）
- Uvicorn + Gunicorn（本番用）
- Docker
- Azure App Service
- AWS Lambda
- Google Cloud Run
