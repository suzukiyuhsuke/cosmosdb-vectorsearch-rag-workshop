FROM python:3.10-slim

WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# デフォルトでは静的ディレクトリが存在しない可能性があるので作成
RUN mkdir -p /app/static

# ポート8000を公開
EXPOSE 8000

# アプリケーションの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
