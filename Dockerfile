# ビルドステージ: フロントエンド
FROM node:20-alpine as frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ビルドステージ: 最終イメージ
FROM python:3.10-slim

WORKDIR /app

# 依存パッケージのインストール
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# バックエンドコードのコピー
COPY backend/ .

# フロントエンドのビルド成果物をバックエンドの静的ディレクトリにコピー
COPY --from=frontend-build /app/frontend/dist /app/static

# ポート8000を公開
EXPOSE 8000

# アプリケーションの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
