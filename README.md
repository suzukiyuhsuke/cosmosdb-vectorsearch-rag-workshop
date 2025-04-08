# RAGチャットボット - Cosmos DB Vector Searchワークショップ

このプロジェクトは、Cosmos DB Vector SearchとAzure OpenAIを使用したRAG（Retrieval Augmented Generation）チャットボットのサンプル実装です。

## 機能

- 自然言語によるユーザーの質問を受け付け、RAGを行い自然言語で回答
- Vite+Reactによるフロントエンド
- FastAPIによるバックエンド
- Cosmos DB for NoSQLをデータベースとして使用
- Cosmos DBのVector Search機能による類似検索
- Azure OpenAI（GPT-4o）によるテキスト生成

## プロジェクト構成

- `frontend`: Vite+Reactフロントエンド
- `backend`: FastAPIバックエンド
- `docker-compose.yml`: Docker Compose設定ファイル

## 前提条件

- Azure Cosmos DB for NoSQLアカウント
- Azure OpenAIサービス（GPT-4oとEmbedding）
- Docker と Docker Compose
- Node.js v18以上（v20推奨）
- npm/yarn（ローカル開発用）
- Python 3.8以上（ローカル開発用）

## セットアップ手順

### 1. Azure Cosmos DBの構築

#### a. Cosmos DBアカウントの作成

Azure PortalまたはAzure CLIを使用してCosmos DBアカウントを作成します。

**Azure Portal使用する場合：**

1. [Azure Portal](https://portal.azure.com)にログインします
2. 「リソースの作成」→「Cosmos DB」を選択
3. APIとして「Core (SQL)」を選択
4. 必要な詳細情報（サブスクリプション、リソースグループ、アカウント名など）を入力
5. 「レビュー + 作成」→「作成」をクリックしてデプロイを開始

**Azure CLIを使用する場合：**

```bash
# リソースグループの作成（既存のものを使用する場合は不要）
az group create --name cosmos-rag-rg --location japaneast

# Cosmos DBアカウントの作成
az cosmosdb create \
  --name rag-cosmos-account \
  --resource-group cosmos-rag-rg \
  --default-consistency-level Session \
  --locations regionName=japaneast failoverPriority=0
```

#### b. データベースとコンテナの作成

Cosmos DBアカウントが作成されたら、データベースとコンテナを作成します。

**Azure Portal使用する場合：**

1. 作成したCosmos DBアカウントに移動
2. 左側のメニューから「データエクスプローラー」を選択
3. 「新しいコンテナー」をクリック
4. 以下の情報を入力：
   - データベースID: `ragdatabase`（新規作成）
   - コンテナID: `documents`
   - パーティションキー: `/id`
   - スループット: 「自動スケーリング」または「プロビジョニング済み」を選択（開発用には400 RU/sで十分）
5. 「OK」をクリックしてコンテナを作成

**Azure CLIを使用する場合：**

```bash
# データベースの作成
az cosmosdb sql database create \
  --account-name rag-cosmos-account \
  --resource-group cosmos-rag-rg \
  --name ragdatabase

# コンテナの作成
az cosmosdb sql container create \
  --account-name rag-cosmos-account \
  --resource-group cosmos-rag-rg \
  --database-name ragdatabase \
  --name documents \
  --partition-key-path "/id" \
  --throughput 400
```

#### c. Vector Search機能の有効化

Cosmos DBでVector Search機能を使用するには、インデックスポリシーを設定する必要があります。

**Azure Portal使用する場合：**

1. 作成したコンテナの「設定」→「Vector Search」に移動
2. 「Vector Searchの使用を開始」をクリック
3. 「+Vector Indexの追加」をクリック
4. 以下の情報を入力：
   - インデックス名: `vector-index`
   - ベクトル化するフィールド: `/embedding`
   - 次元数: `1536`（OpenAI Embeddingモデルの次元数）
   - 距離関数: `Cosine`
   - 追加のメタデータフィールド: `/title`と`/content`を追加
5. 「保存」をクリックして設定を完了

**JSONを使用して手動設定する場合：**

アプリケーションの初回実行時に自動的にVector Searchインデックスが作成されますが、手動で作成する場合は以下のJSONポリシーをAzure Portalのデータエクスプローラーから適用します：

```json
{
  "kind": "VectorSearch",
  "name": "vector-index",
  "vectorSearchConfiguration": {
    "algorithmConfigurations": [
      {
        "name": "vector-config",
        "kind": "approximate",
        "approximateConfiguration": {
          "metric": "cosine"
        }
      }
    ]
  },
  "fields": [
    {
      "path": "/embedding",
      "kind": "vector",
      "vectorDimension": 1536,
      "vectorSearchConfiguration": "vector-config"
    },
    {
      "path": "/title",
      "kind": "string"
    },
    {
      "path": "/content",
      "kind": "string"
    }
  ]
}
```

#### d. 接続情報の取得

アプリケーションのために必要なCosmos DBの接続情報を取得します。

1. Cosmos DBアカウントの「設定」→「キー」に移動
2. 「プライマリキー」と「URI」をコピー
3. これらの値を`.env`ファイルの`COSMOS_ENDPOINT`と`COSMOS_KEY`に設定

```
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-primary-key
```

### 2. Azure OpenAIリソースの作成とモデルのデプロイ

#### a. Azure OpenAIリソースの作成

Azure PortalまたはAzure CLIを使用してAzure OpenAIリソースを作成します。

**Azure Portal使用する場合：**

1. [Azure Portal](https://portal.azure.com)にログインします
2. 「リソースの作成」→「AI + 機械学習」→「Azure OpenAI」を選択
3. 以下の情報を入力：
   - サブスクリプション: 利用するサブスクリプションを選択
   - リソースグループ: 既存のグループを選択または新規作成
   - リージョン: 利用可能なリージョンを選択（East USやWest US、South Central USなど）
   - 名前: リソース名（例: `rag-openai-resource`）
   - 価格レベル: 「Standard S0」
4. 「確認および作成」→「作成」をクリックしてデプロイを開始

**Azure CLIを使用する場合：**

```bash
# リソースグループの作成（既存のものを使用する場合は不要）
az group create --name openai-rag-rg --location eastus

# Azure OpenAIリソースの作成
az cognitiveservices account create \
  --name rag-openai-resource \
  --resource-group openai-rag-rg \
  --location eastus \
  --kind OpenAI \
  --sku S0
```

#### b. Azure OpenAIモデルのデプロイ

Azure OpenAIリソースを作成した後、必要なモデルをデプロイします。このアプリケーションでは以下の2つのモデルが必要です：
1. GPT-4o（または同等のモデル）- メインの対話モデル
2. text-embedding-ada-002 - ベクトル埋め込み用モデル

**Azure Portal使用する場合：**

1. 作成したAzure OpenAIリソースに移動
2. 左側のメニューから「モデルデプロイ」を選択
3. 「作成」ボタンをクリック
4. GPT-4oモデルのデプロイ：
   - モデル: 「gpt-4o」を選択（または利用可能なGPT-4モデル）
   - モデルバージョン: デフォルトを選択
   - デプロイ名: `gpt-4o`（この名前は環境変数で使用）
   - デプロイの種類: 「標準」を選択
   - トークン/分のレート制限: デフォルト値または必要に応じて調整
   - 「作成」をクリックしてデプロイを開始
5. 同様の手順で埋め込みモデルをデプロイ：
   - モデル: 「text-embedding-ada-002」を選択
   - モデルバージョン: デフォルトを選択
   - デプロイ名: `text-embedding-ada-002`（この名前は環境変数で使用）
   - 「作成」をクリックしてデプロイを開始

**Azure CLIを使用する場合：**

```bash
# GPT-4oモデルのデプロイ
az cognitiveservices account deployment create \
  --name rag-openai-resource \
  --resource-group openai-rag-rg \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version 1 \
  --model-format OpenAI \
  --scale-settings-scale-type Standard

# 埋め込みモデルのデプロイ
az cognitiveservices account deployment create \
  --name rag-openai-resource \
  --resource-group openai-rag-rg \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version 2 \
  --model-format OpenAI \
  --scale-settings-scale-type Standard
```

#### c. Azure OpenAIキーとエンドポイントの取得

アプリケーションに必要なAzure OpenAIの接続情報を取得します。

1. Azure OpenAIリソースの「キーとエンドポイント」に移動
2. 「キー1」（またはキー2）と「エンドポイント」をコピー
3. これらの値を`.env`ファイルの`AZURE_OPENAI_API_KEY`と`AZURE_OPENAI_ENDPOINT`に設定

`.env`ファイル内の設定例：

```
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_ENDPOINT=https://rag-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

> **注意**: GPT-4oが利用できない場合は、利用可能な最新のGPTモデル（GPT-4, GPT-3.5-turboなど）を使用し、`AZURE_OPENAI_DEPLOYMENT`の値を適宜変更してください。

### 3. 環境変数の設定

`.env.example`ファイルをコピーして`.env`ファイルを作成し、必要な環境変数を設定します。

```
cp .env.example .env
```

`.env`ファイルを編集して、必要な情報を入力してください：

- Cosmos DBの接続情報
- Azure OpenAIの接続情報

### 4. Docker Composeで起動

```
docker-compose up -d
```

### 5. アプリケーションへのアクセス

フロントエンド: http://localhost

バックエンドAPI: http://localhost:8000

## ローカル開発

Docker Composeを使わずに直接ローカル環境で開発する方法です。

### 1. 環境変数の設定

`.env.example`ファイルをコピーして`.env`ファイルを作成します。

```bash
cp .env.example .env
```

`.env`ファイルを編集して、必要な情報（Cosmos DBの接続情報とAzure OpenAIの接続情報）を入力します。

### 2. バックエンド開発

```bash
# バックエンドディレクトリに移動
cd backend

# Python仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windowsの場合:
venv\Scripts\activate
# macOS/Linuxの場合:
# source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# .envファイルをバックエンドディレクトリにコピー
cp ../.env .

# 開発サーバーを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

バックエンドサーバーは http://localhost:8000 で実行されます。

### 3. フロントエンド開発

別のターミナルウィンドウを開き、以下のコマンドを実行します：

```bash
# フロントエンドディレクトリに移動
cd frontend

# Node.jsの依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

フロントエンド開発サーバーは通常 http://localhost:5173 で実行されます。

### 4. アプリケーションへのアクセス

- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- Swagger UI (API ドキュメント): http://localhost:8000/docs

## Docker Compose による実行 (オプション)

```
docker-compose up -d
```

## 使い方

1. 「知識の追加」タブからナレッジベースにドキュメントを追加
2. 「チャット」タブで質問を入力すると、関連情報を検索して回答を生成

### サンプルデータのロード

テスト用のサンプルデータを簡単にロードするには、以下のいずれかの方法を使用できます：

#### 方法1: スクリプトでCosmosDBに直接アップロード

```bash
# Python環境が必要です
cd scripts
python upload_sample_data.py
```

このスクリプトは `sample_documents` ディレクトリにあるマークダウンファイルを読み込み、ベクトル埋め込みを生成して、Cosmos DBに直接保存します。

#### 方法2: アプリケーションのAPIを使用してアップロード

```bash
# アプリケーションが実行されている必要があります
cd sample_documents
python load_documents.py
```

このスクリプトはアプリケーションのAPIを使用してドキュメントをアップロードします。

#### 方法3: UIから手動でアップロード

1. サンプルドキュメント (`sample_documents` ディレクトリ内) をブラウザで開く
2. アプリケーションの「知識の追加」タブに移動
3. ドキュメントの内容をコピー＆ペースト
4. 「ドキュメントを追加」ボタンをクリック

### テスト用質問例

サンプルデータをロードした後、以下のような質問を試してみてください：

- 「Azure Cosmos DBとは何ですか？」
- 「RAGアーキテクチャの仕組みを説明してください」
- 「FastAPIの主な特徴は？」
- 「Reactでコンポーネントを作成する方法は？」
- 「Azure OpenAIのモデルについて教えてください」

## プロジェクト構造の詳細

詳細は`project_structure.md`を参照してください。

## ライセンス

[MIT](LICENSE)

## Azure App Serviceへのデプロイ

このアプリケーションはAzure App Serviceにデプロイすることができます。バックエンドとフロントエンドを別々のApp Serviceインスタンスにデプロイします。

### 前提条件

- Azure CLI（インストールと認証済み）
- Azure サブスクリプション
- Git
- Node.js v18以上（ローカルビルド用）
- Python 3.8以上（ローカルビルド用）

### 1. リソースグループの作成

```bash
# リソースグループの作成
az group create --name rag-chatbot-rg --location japaneast
```

### 2. バックエンドのデプロイ

#### a. App Serviceプランの作成（Python用）

```bash
# App Serviceプランの作成
az appservice plan create --name rag-backend-plan --resource-group rag-chatbot-rg --sku B1 --is-linux
```

#### b. Pythonランタイムを使用したApp Serviceの作成

```bash
# Python App Serviceの作成
az webapp create --resource-group rag-chatbot-rg --plan rag-backend-plan --name rag-chatbot-backend --runtime "PYTHON|3.10"
```

#### c. アプリケーション設定の構成（環境変数）

```bash
# 環境変数の設定
az webapp config appsettings set --resource-group rag-chatbot-rg --name rag-chatbot-backend --settings \
  COSMOS_ENDPOINT="<your-cosmos-endpoint>" \
  COSMOS_KEY="<your-cosmos-key>" \
  COSMOS_DATABASE="ragdatabase" \
  COSMOS_CONTAINER="documents" \
  AZURE_OPENAI_API_KEY="<your-openai-api-key>" \
  AZURE_OPENAI_ENDPOINT="<your-openai-endpoint>" \
  AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
  AZURE_OPENAI_API_VERSION="2024-02-01" \
  AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002"
```

#### d. バックエンドのデプロイ

```bash
# プロジェクトディレクトリ内で
cd backend

# デプロイのための準備
# requirements.txtは既に存在します

# startup.txtの作成（Azure App Serviceに起動コマンドを伝える）
echo "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" > startup.txt

# requirements.txtにgunicornを追加
echo "gunicorn==21.2.0" >> requirements.txt

# App Serviceにデプロイ
az webapp deployment source config-local-git --resource-group rag-chatbot-rg --name rag-chatbot-backend

# Gitリモートを追加してデプロイ
git init
git add .
git commit -m "Initial backend deployment"
git remote add azure <生成されたGitリモートURL>
git push azure main
```

### 3. フロントエンドのデプロイ

#### a. App Serviceプランの作成（Node.js用）

```bash
# App Serviceプランの作成（既存のプランを共有することもできます）
az appservice plan create --name rag-frontend-plan --resource-group rag-chatbot-rg --sku B1 --is-linux
```

#### b. Node.jsランタイムを使用したApp Serviceの作成

```bash
# Node.js App Serviceの作成
az webapp create --resource-group rag-chatbot-rg --plan rag-frontend-plan --name rag-chatbot-frontend --runtime "NODE|18-lts"
```

#### c. フロントエンドの設定変更

フロントエンドのAPI設定を変更し、バックエンドのURLを指すように修正します。
`frontend/src/services/api.js`にあるAPIのベースURLを更新します：

```javascript
const API_URL = 'https://rag-chatbot-backend.azurewebsites.net/api/v1';
```

または、環境変数を使用して設定することも可能です：

```bash
# フロントエンドの環境変数を設定
az webapp config appsettings set --resource-group rag-chatbot-rg --name rag-chatbot-frontend --settings \
  VITE_API_URL=https://rag-chatbot-backend.azurewebsites.net/api/v1
```

この場合は、`frontend/src/services/api.js`を以下のように変更します：

```javascript
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';
```

#### d. フロントエンドのビルドとデプロイ

```bash
# プロジェクトディレクトリ内で
cd frontend

# 依存関係のインストール
npm install

# プロダクションビルド作成
npm run build

# web.configファイルを作成（SPAルーティング用）
echo '<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="SPA Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/api" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
    <staticContent>
      <mimeMap fileExtension=".json" mimeType="application/json" />
    </staticContent>
  </system.webServer>
</configuration>' > ./dist/web.config

# App Serviceにデプロイ（ZIPデプロイを使用）
az webapp deployment source config-zip --resource-group rag-chatbot-rg --name rag-chatbot-frontend --src ./dist.zip
```

### 4. CORSの設定

バックエンドApp Serviceで、フロントエンドからのリクエストを許可するためにCORSを構成します。

```bash
# CORSの設定
az webapp cors add --resource-group rag-chatbot-rg --name rag-chatbot-backend --allowed-origins "https://rag-chatbot-frontend.azurewebsites.net"
```

### 5. アプリケーションへのアクセス

- フロントエンド: https://rag-chatbot-frontend.azurewebsites.net
- バックエンドAPI: https://rag-chatbot-backend.azurewebsites.net
- Swagger UI (API ドキュメント): https://rag-chatbot-backend.azurewebsites.net/docs

### 6. （オプション）カスタムドメインとSSLの設定

必要に応じて、カスタムドメインとSSL証明書を設定することができます。

```bash
# カスタムドメインの追加
az webapp config hostname add --webapp-name rag-chatbot-frontend --resource-group rag-chatbot-rg --hostname "your-domain.com"

# SSL証明書の追加
az webapp config ssl upload --certificate-file your-cert.pfx --certificate-password your-password --name rag-chatbot-frontend --resource-group rag-chatbot-rg
```

### 7. 継続的デプロイの設定（オプション）

GitHub Actionsなどを使用して継続的デプロイを設定することもできます。詳細については、Azure Docsを参照してください。

## Azure App Serviceへのデプロイ

このアプリケーションはAzure App Serviceにデプロイすることができます。ここでは、フロントエンドとバックエンドを統合した単一のApp Serviceにデプロイする方法を説明します。

### 1. 統合アプリケーションのビルド

フロントエンドをビルドしてバックエンドに統合するには、プロジェクトルートディレクトリでビルドスクリプトを実行します：

**Linux/macOS:**
```bash
# 実行権限を付与
chmod +x build.sh
# ビルドを実行
./build.sh
```

**Windows:**
```bash
build.bat
```

これにより、フロントエンドがビルドされ、生成された静的ファイルがバックエンドの`static`ディレクトリにコピーされます。

### 2. Azure App Serviceの作成

```bash
# リソースグループの作成（既存のものを使用する場合は省略可能）
az group create --name rag-chatbot-rg --location japaneast

# App Serviceプランの作成
az appservice plan create --name rag-app-plan --resource-group rag-chatbot-rg --sku B1 --is-linux

# Pythonランタイムを使用したApp Serviceの作成
az webapp create --resource-group rag-chatbot-rg --plan rag-app-plan --name rag-chatbot-app --runtime "PYTHON|3.10"
```

### 3. アプリケーション設定の構成

```bash
# 環境変数の設定
az webapp config appsettings set --resource-group rag-chatbot-rg --name rag-chatbot-app --settings \
  COSMOS_ENDPOINT="<your-cosmos-endpoint>" \
  COSMOS_KEY="<your-cosmos-key>" \
  COSMOS_DATABASE="ragdatabase" \
  COSMOS_CONTAINER="documents" \
  GPT_API_KEY="<your-gpt-api-key>" \
  GPT_ENDPOINT="<your-gpt-endpoint>" \
  GPT_DEPLOYMENT="gpt-4o" \
  GPT_API_VERSION="2024-02-01" \
  EMBEDDING_API_KEY="<your-embedding-api-key>" \
  EMBEDDING_ENDPOINT="<your-embedding-endpoint>" \
  EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
  EMBEDDING_API_VERSION="2024-02-01"
```

### 4. アプリケーションのデプロイ

#### 方法1: ZIP デプロイを使用した簡単なデプロイ

統合ビルドしたアプリケーションをZIPファイルに圧縮し、直接デプロイする最も簡単な方法です。

```bash
# バックエンドディレクトリに移動
cd backend

# startup.txtの作成（Azure App Serviceに起動コマンドを伝える）
echo "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" > startup.txt

# requirements.txtにgunicornを追加（存在しない場合）
if ! grep -q "gunicorn" requirements.txt; then
  echo "gunicorn==21.2.0" >> requirements.txt
fi

# ディレクトリをZIPファイルに圧縮
zip -r ../app.zip ./*

# Azure App Serviceにデプロイ
cd ..
az webapp deploy --resource-group rag-chatbot-rg --name rag-chatbot-app --src-path app.zip --type zip
```

**Windows PowerShellの場合:**

```powershell
# バックエンドディレクトリに移動
cd backend

# startup.txtの作成
"gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" | Out-File -Encoding utf8 startup.txt

# requirements.txtにgunicornを追加（存在しない場合）
if (-not (Select-String -Path requirements.txt -Pattern "gunicorn" -Quiet)) {
  "gunicorn==21.2.0" | Add-Content -Path requirements.txt
}

# ディレクトリをZIPファイルに圧縮
Compress-Archive -Path * -DestinationPath ..\app.zip -Force

# Azure App Serviceにデプロイ
cd ..
az webapp deploy --resource-group rag-chatbot-rg --name rag-chatbot-app --src-path app.zip --type zip
```

#### 方法2: ローカルGitを使用したデプロイ

```bash
# プロジェクトルートディレクトリで実行

# startup.txtの作成（Azure App Serviceに起動コマンドを伝える）
echo "gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" > startup.txt

# requirements.txtがルートにない場合は作成または移動
cp backend/requirements.txt ./requirements.txt
# gunicornを追加（存在しない場合）
if ! grep -q "gunicorn" requirements.txt; then
  echo "gunicorn==21.2.0" >> requirements.txt
fi

# フロントエンドをビルド
cd frontend
npm install
npm run build
cd ..

# .deployment ファイルの作成（Kuduデプロイエンジンの設定）
echo "[config]" > .deployment
echo "project = ." >> .deployment

# App Serviceにデプロイするための設定
az webapp deployment source config-local-git --resource-group rag-chatbot-rg --name rag-chatbot-app

# Gitリモートを追加してデプロイ
git init
git add .
git commit -m "Initial root directory deployment"
git remote add azure <生成されたGitリモートURL>
git push azure main
```

**Windows PowerShellの場合:**

```powershell
# プロジェクトルートディレクトリで実行

# startup.txtの作成
"gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" | Out-File -Encoding utf8 startup.txt

# requirements.txtがルートにない場合は作成または移動
Copy-Item -Path backend\requirements.txt -Destination .\requirements.txt -Force
# gunicornを追加（存在しない場合）
if (-not (Select-String -Path requirements.txt -Pattern "gunicorn" -Quiet)) {
  "gunicorn==21.2.0" | Add-Content -Path requirements.txt
}

# フロントエンドをビルド
cd frontend
npm install
npm run build
cd ..

# .deployment ファイルの作成（Kuduデプロイエンジンの設定）
"[config]" | Out-File -Encoding utf8 .deployment
"project = ." | Add-Content -Path .deployment

# App Serviceにデプロイするための設定
az webapp deployment source config-local-git --resource-group rag-chatbot-rg --name rag-chatbot-app

# Gitリモートを追加してデプロイ
git init
git add .
git commit -m "Initial root directory deployment"
git remote add azure <生成されたGitリモートURL>
git push azure main
```

#### 方法3: Dockerコンテナを使用したデプロイ

```bash
# Dockerイメージのビルド
docker build -t rag-chatbot-app .

# Azure Container Registryにイメージをプッシュ（ACRが必要）
az acr build --registry <your-acr-name> --image rag-chatbot-app:latest .

# App ServiceをDockerコンテナモードに設定
az webapp config container set --name rag-chatbot-app --resource-group rag-chatbot-rg \
  --docker-custom-image-name <your-acr-name>.azurecr.io/rag-chatbot-app:latest \
  --docker-registry-server-url https://<your-acr-name>.azurecr.io
```

#### 方法4: GitHub Actionsを使用した継続的デプロイ

このプロジェクトには、GitHub Actionsを使用した継続的デプロイのためのワークフロー設定が含まれています。以下の手順で設定します：

1. GitHubリポジトリのSecretsに以下の値を設定します：
   - `AZURE_CREDENTIALS`: Azureサービスプリンシパルの認証情報
   - `COSMOS_ENDPOINT`: Cosmos DBのエンドポイント
   - `COSMOS_KEY`: Cosmos DBのアクセスキー
   - `GPT_API_KEY`: GPTモデル用のAPIキー
   - `GPT_ENDPOINT`: GPTモデル用のエンドポイント
   - `EMBEDDING_API_KEY`: 埋め込みモデル用のAPIキー
   - `EMBEDDING_ENDPOINT`: 埋め込みモデル用のエンドポイント

2. リポジトリにコードをプッシュすると、GitHub Actionsが自動的にビルドとデプロイを行います。

### 5. アプリケーションへのアクセス

デプロイが完了したら、以下のURLでアプリケーションにアクセスできます：

- アプリケーション: https://rag-chatbot-app.azurewebsites.net
- API: https://rag-chatbot-app.azurewebsites.net/api/v1
- Swagger UI: https://rag-chatbot-app.azurewebsites.net/docs

## デプロイのトラブルシューティング

アプリケーションのデプロイ時に問題が発生した場合は、以下を確認してください：

### ログの確認

```bash
# アプリケーションログのストリーミング
az webapp log tail --resource-group rag-chatbot-rg --name rag-chatbot-app

# 詳細なログの有効化
az webapp log config --resource-group rag-chatbot-rg --name rag-chatbot-app --docker-container-logging filesystem
```

### 一般的な問題

1. **起動コマンドの問題**: `startup.txt` ファイルが正しく作成されているか確認してください。
2. **依存関係の問題**: `requirements.txt` に必要なすべての依存関係（特に `gunicorn`）が含まれているか確認してください。
3. **環境変数の問題**: すべての環境変数が正しく設定されているか確認してください。
4. **静的ファイルの問題**: `static` ディレクトリにフロントエンドのビルドファイルが正しくコピーされているか確認してください。
