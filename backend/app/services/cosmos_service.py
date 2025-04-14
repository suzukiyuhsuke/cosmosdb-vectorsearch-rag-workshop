import json
from azure.cosmos import CosmosClient, PartitionKey
from app.config import COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_CONTAINER
from app.utils.embedding import get_embedding


class CosmosService:
    def __init__(self):
        # Cosmos DBクライアントの初期化
        self.client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        print(f"Cosmos DBクライアントを初期化しました{COSMOS_ENDPOINT},{COSMOS_KEY}")
        self.database = self.client.get_database_client(COSMOS_DATABASE)
        self.container = self.database.get_container_client(COSMOS_CONTAINER)

    def initialize_database(self):
        """データベースとコンテナが存在しない場合は作成する"""
        try:
            # データベースが存在しなければ作成
            self.database = self.client.create_database_if_not_exists(
                id=COSMOS_DATABASE)

            # READMEのガイダンスに従ってインデックスポリシーを設定
            indexing_policy = {
                "indexingMode": "consistent",
                "automatic": True,
                "includedPaths": [
                    {
                        "path": "/*"
                    }
                ],
                "excludedPaths": [
                    {
                        "path": "/\"_etag\"/?"
                    }
                ]
            }

            # Vector Indexesポリシーを設定
            vector_indexes = [
                {
                    "path": "/embedding",
                    "type": "vector",
                    "dataType": "float32",
                    "dimensions": 1536,
                    "algorithm": "hnsw",
                    "distanceFunction": "cosine"
                }
            ]

            # コンテナが存在しなければ作成（パーティションキーはidフィールド）
            self.container = self.database.create_container_if_not_exists(
                id=COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy
            )

            print("コンテナが作成されました。Vector Indexは手動でAzure Portalから設定するか、APIを使用して追加する必要があります。")
            print("以下のJSONをAzure Portalのコンテナ設定 > インデックスポリシーに追加してください:")
            print(json.dumps({"vectorIndexes": vector_indexes}, indent=2))

            return True
        except Exception as e:
            print(f"データベースの初期化中にエラーが発生しました: {str(e)}")
            return False

    def add_document(self, title, content):
        """
        ドキュメントをCosmosDBに追加する

        Args:
            title: ドキュメントのタイトル
            content: ドキュメントの内容

        Returns:
            dict: 作成されたドキュメント
        """
        try:
            # コンテンツのベクトル埋め込みを取得
            embedding = get_embedding(content)

            # ドキュメントを作成
            document = {
                "id": str(hash(title + content)),
                "title": title,
                "content": content,
                "embedding": embedding
            }

            # Cosmos DBにドキュメントを保存
            return self.container.create_item(body=document)
        except Exception as e:
            print(f"ドキュメント追加中にエラーが発生しました: {str(e)}")
            raise

    def search_documents(self, query, limit=3):
        """
        クエリのベクトル埋め込みを使用して類似ドキュメントを検索する

        Args:
            query: 検索クエリ
            limit: 結果の最大数

        Returns:
            list: 類似ドキュメントのリスト
        """
        try:
            # クエリのベクトル埋め込みを取得
            query_embedding = get_embedding(query)

            # Vector Searchを使用して類似ドキュメントを検索
            # READMEと一致するVectorDistanceクエリを使用
            query = {
                "query": "SELECT TOP @limit * FROM c ORDER BY VectorDistance(c.embedding, @queryEmbedding)",
                "parameters": [
                    {"name": "@queryEmbedding", "value": query_embedding},
                    {"name": "@limit", "value": limit}
                ]
            }

            results = list(self.container.query_items(
                query=query["query"],
                parameters=query["parameters"],
                enable_cross_partition_query=True
            ))

            return results
        except Exception as e:
            print(f"ドキュメント検索中にエラーが発生しました: {str(e)}")
            raise
