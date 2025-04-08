#!/bin/bash
set -e

echo "=== RAGチャットボット 統合ビルドスクリプト ==="

# フロントエンドのビルド
echo "フロントエンドをビルドしています..."
cd frontend
npm install
npm run build
cd ..

# backendの静的ディレクトリを作成
echo "バックエンドにフロントエンドの静的ファイルをコピーしています..."
mkdir -p backend/static
rm -rf backend/static/*
cp -r frontend/dist/* backend/static/

echo "ビルド完了！"
echo "バックエンドディレクトリには統合されたアプリケーションが含まれています。"
