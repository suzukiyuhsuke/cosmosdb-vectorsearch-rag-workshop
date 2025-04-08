# 開発コンテナ環境

このプロジェクトはVS Code Remote Containersを使用して、一貫した開発環境を提供します。

## 前提条件

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code Remote - Containers拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## 環境のセットアップ

1. このリポジトリをクローンします
2. `.devcontainer/.env.example`を`.devcontainer/.env`にコピーし、必要な環境変数を設定します
   ```bash
   cd .devcontainer
   cp .env.example .env
   # .envファイルを編集して必要な情報を入力
   ```
3. VS Codeでプロジェクトフォルダを開きます
4. VSCodeの左下にある「><」アイコンをクリックし、「Reopen in Container」を選択します
5. コンテナのビルドと起動が完了するまで待ちます

## 開発環境の構成

この開発コンテナ環境は以下のサービスを提供します：

- **workspace**: メインの開発環境
  - Python 3.10
  - Node.js 20
  - Azure CLI
  - GitHub CLI

- **backend**: FastAPIバックエンド開発環境
  - ポート: 8000
  - 自動リロード有効

- **frontend**: Vite + React フロントエンド開発環境

  - ポート: 5173
  - ホットリロード有効

## トラブルシューティング

- **環境変数が読み込まれない場合**:
  コンテナ内で`.env`ファイルが正しく読み込まれているか確認します：
  ```bash
  printenv | grep COSMOS_
  printenv | grep AZURE_OPENAI_
  ```

- **ポートにアクセスできない場合**:
  VSCodeのポート転送設定を確認します。自動的に設定されていない場合は手動で追加します。

- **コンテナのリビルドが必要な場合**:
  VSCodeのコマンドパレットから「Remote-Containers: Rebuild Container」を選択します。
