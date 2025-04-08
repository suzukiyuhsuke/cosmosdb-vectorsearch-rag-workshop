FROM python:3.10-slim

WORKDIR /workspace/backend

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 依存関係をインストール
COPY ./backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install python-dotenv

# 開発ツールのインストール
RUN pip install black pylint pytest pytest-cov

# ポートの公開
EXPOSE 8000

# コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
