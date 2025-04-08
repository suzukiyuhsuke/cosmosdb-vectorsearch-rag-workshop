# ユーティリティスクリプト

このディレクトリには、RAGチャットボットの開発とデバッグに役立つユーティリティスクリプトが含まれています。

## 利用可能なスクリプト

### test_cosmos_connection.py

CosmosDBへの接続をテストするスクリプトです。環境変数からCosmosDBの接続情報を読み取り、データベースとコンテナに接続できるかを確認します。

#### 使用方法

```bash
# スクリプトを実行
python test_cosmos_connection.py

# または、実行権限を付与して直接実行
chmod +x test_cosmos_connection.py
./test_cosmos_connection.py
```

#### 機能

このスクリプトは以下のテストを実行します：

1. CosmosDBクライアントへの接続
2. データベースへの接続
3. コンテナへの接続
4. 基本的なクエリの実行
5. テストドキュメントの作成
6. テストドキュメントの読み取り
7. テストドキュメントの削除

接続に失敗した場合、考えられる原因と解決策が表示されます。リソース（データベースやコンテナ）が存在しない場合は、それらを作成するオプションが提供されます。

#### 前提条件

- Python 3.8以上
- 必要なパッケージ：azure-cosmos, python-dotenv
- 環境変数：COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_CONTAINER

#### インストール

```bash
pip install azure-cosmos python-dotenv
```

### upload_sample_data.py

サンプルドキュメントをCosmosDBに直接アップロードするスクリプトです。このスクリプトは単にAPIを通さずに、直接Cosmos DBにドキュメントを追加します。

#### 使用方法

```bash
# スクリプトを実行（デフォルトでは ./sample_documents ディレクトリを使用）
python upload_sample_data.py

# または、別のディレクトリを指定
python upload_sample_data.py --dir ../sample_documents

# または、実行権限を付与して直接実行
chmod +x upload_sample_data.py
./upload_sample_data.py
```

#### 機能

このスクリプトは以下の処理を行います：

1. 指定されたディレクトリからMarkdownファイルを読み込む
2. 各ドキュメントに対して、Azure OpenAIを使用してテキスト埋め込みベクトルを生成
3. 埋め込みベクトルを含むドキュメントをCosmos DBに保存

#### 前提条件

- Python 3.8以上
- 必要なパッケージ：azure-cosmos, python-dotenv, openai
- 環境変数：
  - Cosmos DB: COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_CONTAINER
  - Azure OpenAI: EMBEDDING_API_KEY (または AZURE_OPENAI_API_KEY), EMBEDDING_ENDPOINT (または AZURE_OPENAI_ENDPOINT)

#### インストール

```bash
pip install azure-cosmos python-dotenv openai
```
