# RAGチャットボット - Cosmos DB Vector Searchワークショップ

このプロジェクトは、Cosmos DB Vector SearchとAzure OpenAIを使用したRAG（Retrieval Augmented Generation）チャットボットのサンプル実装です。

## 目次

- [機能](#機能)
- [プロジェクト構成](#プロジェクト構成)
- [前提条件](#前提条件)
- [セットアップ手順](#セットアップ手順)
  - [1. Azure Cosmos DBの構築](#1-azure-cosmos-dbの構築)
  - [2. Azure OpenAIリソースの作成とモデルのデプロイ](#2-azure-openaiリソースの作成とモデルのデプロイ)
  - [3. 環境変数の設定](#3-環境変数の設定)
  - [4. Docker Composeで起動](#4-docker-composeで起動)
  - [5. アプリケーションへのアクセス](#5-アプリケーションへのアクセス)
- [ローカル開発](#ローカル開発)
  - [1. 環境変数の設定](#1-環境変数の設定)
  - [2. バックエンド開発](#2-バックエンド開発)
  - [3. フロントエンド開発](#3-フロントエンド開発)
  - [4. アプリケーションへのアクセス](#4-アプリケーションへのアクセス)
- [Docker Compose による実行 (オプション)](#docker-compose-による実行-オプション)
- [使い方](#使い方)
  - [サンプルデータのロード](#サンプルデータのロード)
  - [テスト用質問例](#テスト用質問例)
- [プロジェクト構造の詳細](#プロジェクト構造の詳細)
- [ライセンス](#ライセンス)
- [Azure App Serviceへのデプロイ](#azure-app-serviceへのデプロイ)
  - [前提条件](#前提条件)
  - [1. リソースグループの作成](#1-リソースグループの作成)
  - [2. バックエンドのデプロイ](#2-バックエンドのデプロイ)
  - [3. フロントエンドのデプロイ](#3-フロントエンドのデプロイ)
  - [4. CORSの設定](#4-corsの設定)
  - [5. アプリケーションへのアクセス](#5-アプリケーションへのアクセス)
  - [6. （オプション）カスタムドメインとSSLの設定](#6-オプションカスタムドメインとsslの設定)
  - [7. 継続的デプロイの設定（オプション）](#7-継続的デプロイの設定オプション)
  - [統合アプリケーションのビルド](#統合アプリケーションのビルド)
  - [デプロイのトラブルシューティング](#デプロイのトラブルシューティング)

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

### プロジェクト構造の詳細

詳細は`project_structure.md`を参照してください。



## 前提条件

- Azure Cosmos DB for NoSQLアカウント
- Azure OpenAIサービス（GPT-4oとEmbedding）
- Docker と Docker Compose（ローカル開発でコンテナを使用する場合）
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
6. **Vector Searchの有効化** デプロイが完了した後、作成したCosmos DBリソースのブレードに移動し、「機能」から「Vector Search for NoSQL API」を選択、ダイアログで「有効」をクリックしてVector Search機能を有効化する

**Azure CLIを使用する場合：**

```bash
# リソースグループの作成（既存のものを使用する場合は不要）
az group create --name cosmos-rag-rg --location japaneast

# Cosmos DBアカウントの作成
az cosmosdb create \
  --name rag-cosmos-account \
  --resource-group cosmos-rag-rg \
  --default-consistency-level Session \
  --locations regionName=japaneast failoverPriority=0 \
  --capabilities EnableVectorSearch
```

#### b. データベースとコンテナの作成

Cosmos DBアカウントが作成されたら、データベースとコンテナを作成します。

**Azure Portal を使用する場合：**

1. 作成した Cosmos DB アカウントに移動  
2. 左側のメニューから「**データエクスプローラー**」を選択  
3. 「**新しいコンテナー**」をクリック  
4. 以下の情報を入力：
   - **データベース ID**: `ragdatabase`（「新規作成」にチェックを入れる）
   - **コンテナ ID**: `documents`
   - **パーティションキー**: `/id`
   - **スループット**: 「自動スケーリング」または「プロビジョニング済み」（開発用途であれば **400 RU/s** で十分）
5. 「**Container Vector Policy**」の項目を展開し、「**Add vector embedding**」をクリックする
6. 以下の情報を入力：
   - **Path**: /embedding
   - **DataType: float32
   - **Distance function**: cosine
   - **Dimensions**: 1536
   > *OpenAI の Embeddingモデルを使用する場合、Dimentionsには1536を指定します。*
   - **Index Type**: none

5. 「**OK**」をクリックしてコンテナを作成  


**Azure CLI を使用する場合：**

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
  --idx @indexies.json
```

#### c. 接続情報の取得

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
   - **サブスクリプション**: 利用するサブスクリプションを選択
   - **リソースグループ**: 既存のグループを選択または新規作成
   - **リージョン**: 利用可能なリージョンを選択（East USやWest US、South Central USなど）
   - **名前**: リソース名（例: `rag-openai-resource`）
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
2. 「**概要**」から「**Explore Azure AI Foundry Portal**」をクリックし、**AI Foundry**を開く
3. 左側のメニューから、「**デプロイ**」を選択して「**モデルのデプロイ**」をクリックし、「基本のモデルをデプロイする**」を選択する
4. GPT-4oモデルのデプロイ：
   - モデル: 「gpt-4o」を選択（または利用可能なGPT-4モデル）
   - デプロイ名: `gpt-4o`（この名前は環境変数で使用）
   - デプロイの種類: 「Standard」を選択
   - その他の項目は設定を変更しない
   - 「デプロイ」をクリックしてデプロイを開始
5. 同様の手順で埋め込みモデルをデプロイ：
   - モデル: 「text-embedding-ada-002」を選択
   - デプロイ名: `text-embedding-ada-002`（この名前は環境変数で使用）
   - デプロイの種類: 「Standard」を選択
   - その他の項目は設定を変更しない
   - 「デプロイ」をクリックしてデプロイを開始

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
3. これらの値を`.env`ファイルの`GPT_API_KEY`、`GPT_ENDPOINT`、`EMBEDDING_API_KEY`と`EMBEDDING_ENDPOINT`に設定

`.env`ファイル内の設定例：

```
# GPT-4o設定
GPT_API_KEY=your-gpt-openai-api-key
GPT_ENDPOINT=https://your-gpt-resource.openai.azure.com/
GPT_DEPLOYMENT=gpt-4o
GPT_API_VERSION=2025-01-01-preview

# Embedding設定
EMBEDDING_API_KEY=your-embedding-openai-api-key
EMBEDDING_ENDPOINT=https://your-embedding-resource.openai.azure.com/
EMBEDDING_DEPLOYMENT=text-embedding-ada-002
EMBEDDING_API_VERSION=2023-05-15
```

> **注意**: GPT-4oが利用できない場合は、利用可能な最新のGPTモデル（GPT-4, GPT-3.5-turboなど）を使用し、`GPT_DEPLOYMENT`の値を適宜変更してください。

### 3. Docker Composeで起動

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

** Azure CLIを使用する場合:**
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
  GPT_API_VERSION="2025-01-01-preview" \
  EMBEDDING_API_KEY="<your-embedding-api-key>" \
  EMBEDDING_ENDPOINT="<your-embedding-endpoint>" \
  EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
  EMBEDDING_API_VERSION="2023-05-15" \
  SCM_DO_BUILD_DURING_DEPLOYMENT=1

# スタートアップコマンドの設定
az webapp config set --resource-group rag-chatbot-rg --name rag-chatbot-app --startup-file "./startup.txt"
```

### 4. アプリケーションのデプロイ

#### 方法1: ZIP デプロイを使用した簡単なデプロイ

統合ビルドしたアプリケーションをZIPファイルに圧縮し、直接デプロイする最も簡単な方法です。

```bash
# バックエンドディレクトリに移動
cd backend

# requirements.txtにgunicornを追加（存在しない場合）
if ! grep -q "gunicorn" requirements.txt; then
  echo "gunicorn" >> requirements.txt
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


#### 方法2: Dockerコンテナを使用したデプロイ

##### a. Azure Container Registry (ACR) の作成

Azure Container Registryを作成して、コンテナイメージを保存します。

```bash
# ACRの作成
az acr create --resource-group rag-chatbot-rg --name ragchatbotacr --sku Basic --admin-enabled true

# ACRのログイン情報を取得
ACR_USERNAME=$(az acr credential show --name ragchatbotacr --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name ragchatbotacr --query "passwords[0].value" -o tsv)
```

##### b. ACR上でのDocker ビルド実行

```bash
# ACRのAzure Buildサービスを使用してDockerイメージをビルド
az acr build --registry ragchatbotacr --image rag-chatbot-app:latest .
```

このコマンドは、ローカルマシンではなくAzureクラウド上でビルドプロセスを実行します。これにより、以下のメリットがあります：

- ローカルマシンのリソースを消費しない
- ビルド環境が常に一貫している
- 大規模なイメージのビルドが高速に完了する
- Dockerがローカルにインストールされていなくても利用可能

##### c. App ServiceのDocker構成

```bash
# App ServiceをDocker構成に設定
az webapp config container set --name rag-chatbot-app --resource-group rag-chatbot-rg \
  --docker-custom-image-name ragchatbotacr.azurecr.io/rag-chatbot-app:latest \
  --docker-registry-server-url https://ragchatbotacr.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD
```

##### d. マネージドIDを使用したアクセス権限の設定（推奨）

セキュリティを向上させるため、パスワードではなくマネージドIDを使用してACRにアクセスするように設定できます。

```bash
# システム割り当てマネージドIDをApp Serviceに設定
az webapp identity assign --name rag-chatbot-app --resource-group rag-chatbot-rg

# App ServiceのプリンシパルIDを取得
PRINCIPAL_ID=$(az webapp identity show --name rag-chatbot-app --resource-group rag-chatbot-rg --query principalId --output tsv)

# ACRプルロールをApp Serviceに割り当て
ACR_ID=$(az acr show --name ragchatbotacr --resource-group rag-chatbot-rg --query id --output tsv)
az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role "AcrPull"

# App ServiceのDocker構成を更新（マネージドIDを使用）
az webapp config container set --name rag-chatbot-app --resource-group rag-chatbot-rg \
  --docker-custom-image-name ragchatbotacr.azurecr.io/rag-chatbot-app:latest \
  --docker-registry-server-url https://ragchatbotacr.azurecr.io \
  --docker-registry-server-user "" \
  --docker-registry-server-password "" \
  --docker-registry-server-identity
```

これにより、機密性の高いACRの認証情報を環境変数として保存する必要がなくなります。

##### e. 新しいDockerイメージのデプロイ

アプリケーションを更新した後に新しいイメージをビルドしてデプロイするには：

```bash
# 新しいイメージをビルド
az acr build --registry ragchatbotacr --image rag-chatbot-app:latest .

# App Serviceを再起動して新しいイメージを取得
az webapp restart --name rag-chatbot-app --resource-group rag-chatbot-rg
```

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
