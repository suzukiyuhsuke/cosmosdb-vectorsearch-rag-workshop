@echo off
echo === RAGチャットボット 統合ビルドスクリプト ===

rem フロントエンドのビルド
echo フロントエンドをビルドしています...
cd frontend
call npm install
call npm run build
cd ..

rem バックエンドの静的ディレクトリを作成
echo バックエンドにフロントエンドの静的ファイルをコピーしています...
if not exist backend\static mkdir backend\static
del /q /s backend\static\*
xcopy frontend\dist\* backend\static\ /e /y

echo ビルド完了！
echo バックエンドディレクトリには統合されたアプリケーションが含まれています。
