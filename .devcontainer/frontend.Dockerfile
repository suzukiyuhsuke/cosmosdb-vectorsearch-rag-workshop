FROM node:20-alpine

WORKDIR /workspace/frontend

# 必要なパッケージをインストール
RUN apk add --no-cache \
    git \
    curl \
    bash

# グローバルパッケージのインストール
RUN npm install -g npm@latest vite

# ポートの公開
EXPOSE 5173

# コマンド
CMD ["npm", "run", "dev"]
