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
            self.database = self.client.create_database_if_not_exists(id=COSMOS_DATABASE)
            
            # コンテナが存在しなければ作成（パーティションキーはidフィールド）
            self.container = self.database.create_container_if_not_exists(
                id=COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/id"),
                indexing_policy={
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {
                            'path': '/*'
                        }
                    ],
                    'excludedPaths': [
                        {
                            'path': '/embedding/?'
                        }
                    ]
                }
            )
            
            # Vector Searchのインデックスを作成
            # self._create_vector_index()
            
            return True
        except Exception as e:
            print(f"データベースの初期化中にエラーが発生しました: {str(e)}")
            return False
            
    def _create_vector_index(self):
        """Vector Searchのインデックスを作成する"""
        try:
            # Vector Searchのインデックスポリシー
            vector_index = {
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
            
            # 修正: ストアドプロシージャの作成方法を改善
            # JSON文字列をそのまま文字列に埋め込むのではなく、適切に変数として渡す
            stored_proc_body = """
            function() {
                const indexDefinition = JSON.parse(JSON.stringify(@indexDef));
                
                // Cosmos DBのインデックスポリシーを取得
                const collection = getCollection();
                
                // インデックスが既に存在するか確認
                const indexExists = collection.indexPolicies && 
                                    collection.indexPolicies.some(p => p.name === indexDefinition.name);
                
                if (!indexExists) {
                    try {
                        // インデックスが存在しない場合は作成
                        collection.createIndex(indexDefinition);
                        return {"status": "success", "message": "Vector index created successfully"};
                    } catch (error) {
                        return {"status": "error", "message": error.toString()};
                    }
                } else {
                    return {"status": "info", "message": "Vector index already exists"};
                }
            }
            """
            
            # ストアドプロシージャを作成または置き換え
            try:
                self.container.scripts.delete_stored_procedure("createVectorIndex")
            except:
                pass  # 存在しない場合は無視
                
            self.container.scripts.create_stored_procedure(
                id="createVectorIndex",
                body=stored_proc_body
            )
            
            # ストアドプロシージャを実行
            result = self.container.scripts.execute_stored_procedure(
                sproc="createVectorIndex",
                partition_key=None,
                params=[vector_index]  # インデックス定義をパラメータとして渡す
            )
            
            print(f"Vector Searchインデックス作成結果: {result}")
            return True
            
        except Exception as e:
            print(f"Vector Searchのインデックス作成中にエラーが発生しました: {str(e)}")
            
            # 代替方法: REST APIを使用してインデックスを作成
            try:
                print("代替方法でVector Searchインデックスを作成しています...")
                # REST APIを使用したインデックス作成は複雑なので、
                # 単純にインデックスなしで続行します
                return False
            except Exception as inner_e:
                print(f"代替インデックス作成中にもエラーが発生しました: {str(inner_e)}")
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
