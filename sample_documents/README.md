# サンプルドキュメント

このディレクトリには、RAGチャットボットのテスト用サンプルドキュメントが含まれています。これらのドキュメントを使用して、チャットボットの質問応答機能をテストできます。

## 含まれるドキュメント

- `azure_cosmos_db.md` - Azure Cosmos DBの概要と機能
- `azure_openai.md` - Azure OpenAIサービスの説明
- `rag_architecture.md` - RAG（Retrieval Augmented Generation）アーキテクチャの解説
- `fastapi_overview.md` - FastAPIフレームワークの概要
- `react_development.md` - React開発ガイド
- `rag_upload_guide.md` - RAGチャットボットへのドキュメント追加手順

## ドキュメントのアップロード方法

### 手動アップロード

1. アプリケーションの「知識の追加」タブに移動
2. タイトルと内容を入力フォームにコピー＆ペースト
3. 「ドキュメントを追加」ボタンをクリック

### スクリプトによる一括アップロード

このディレクトリには、サンプルドキュメントを一括でアップロードするためのPythonスクリプト `load_documents.py` が含まれています。

#### 使用方法

```bash
# アプリケーションのAPIが実行されていることを確認

# 現在のディレクトリ内のすべてのMarkdownファイルをアップロード
python load_documents.py

# または、特定のAPIエンドポイントを指定
python load_documents.py --url http://localhost:8000/api/v1/rag/documents

# または、異なるディレクトリを指定
python load_documents.py --dir /path/to/documents
```

## テスト方法

ドキュメントをアップロードした後、「チャット」タブで以下のような質問を試してみてください：

- 「Azure Cosmos DBとは何ですか？」
- 「RAGアーキテクチャの仕組みを説明してください」
- 「FastAPIの主な特徴は？」
- 「Reactでコンポーネントを作成する方法は？」
- 「Azure OpenAIのモデルには何がありますか？」
- 「ドキュメントをアップロードする方法は？」

## 独自のドキュメントの追加

このサンプルを参考に、独自のドキュメントを追加することができます。Markdownフォーマットで作成し、明確なタイトルと構造化されたコンテンツを含めることをお勧めします。
