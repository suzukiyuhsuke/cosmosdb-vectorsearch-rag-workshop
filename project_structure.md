# プロジェクト構造

```
cosmosdb-verctersearch-rag-workshop/
├── backend/               # FastAPIバックエンド
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPIのメインアプリケーション
│   │   ├── config.py      # 設定ファイル
│   │   ├── models/        # データモデル
│   │   ├── api/           # APIエンドポイント
│   │   ├── services/      # ビジネスロジック
│   │   └── utils/         # ユーティリティ関数
│   ├── requirements.txt   # Pythonの依存関係
│   └── Dockerfile         # バックエンド用Dockerfile
├── frontend/              # Vite+React+TypeScriptフロントエンド
│   ├── src/
│   │   ├── components/    # Reactコンポーネント（.tsx）
│   │   ├── hooks/         # カスタムフック
│   │   ├── services/      # APIサービス（.ts）
│   │   ├── types/         # TypeScript型定義
│   │   ├── App.tsx        # メインアプリケーション
│   │   ├── main.tsx       # エントリーポイント
│   │   └── styles/        # CSSファイル
│   ├── package.json       # npmの依存関係
│   ├── tsconfig.json      # TypeScript設定
│   ├── vite.config.ts     # Viteの設定
│   └── Dockerfile         # フロントエンド用Dockerfile
├── scripts/               # ユーティリティスクリプト
├── sample_documents/      # サンプルドキュメント
├── .devcontainer/         # 開発コンテナ設定
├── docker-compose.yml     # Dockerコンポーズファイル
└── README.md              # プロジェクトの説明
```
