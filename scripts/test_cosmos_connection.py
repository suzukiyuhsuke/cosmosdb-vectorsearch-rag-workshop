#!/usr/bin/env python
"""
CosmosDBへの接続をテストするスクリプト
"""

import os
import sys
import time
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
import pathlib

def load_env_vars():
    """環境変数を読み込む"""
    # .envファイルが様々な場所にあるかもしれないので、複数のパスをチェック
    env_paths = [
        pathlib.Path('.env'),
        pathlib.Path('../.env'),
        pathlib.Path('../../.env'),
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            print(f".envファイルを読み込みました: {env_path.absolute()}")
            load_dotenv(dotenv_path=env_path)
            return True
    
    # システム環境変数からの読み込みを試みる
    print(".envファイルが見つからなかったため、システム環境変数を使用します")
    load_dotenv()
    return True

def test_cosmos_connection():
    """CosmosDBへの接続をテスト"""
    # 必要な環境変数を取得
    cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    cosmos_database = os.getenv("COSMOS_DATABASE", "ragdatabase")
    cosmos_container = os.getenv("COSMOS_CONTAINER", "documents")
    
    # 接続情報の確認
    if not cosmos_endpoint or not cosmos_key:
        print("エラー: COSMOS_ENDPOINTとCOSMOS_KEYの環境変数が必要です")
        print(f"COSMOS_ENDPOINT: {'設定されています' if cosmos_endpoint else '設定されていません'}")
        print(f"COSMOS_KEY: {'設定されています' if cosmos_key else '設定されていません'}")
        return False
    
    print("\n===== CosmosDB接続テスト =====")
    print(f"エンドポイント: {cosmos_endpoint}")
    print(f"データベース: {cosmos_database}")
    print(f"コンテナ: {cosmos_container}")
    
    try:
        # CosmosDBクライアントの初期化
        print("\n1. CosmosDBクライアントに接続しています...")
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        print("   ✓ クライアント接続成功")
        
        # データベースへの接続
        print("\n2. データベースに接続しています...")
        database = client.get_database_client(cosmos_database)
        database_properties = database.read()
        print(f"   ✓ データベース '{database_properties['id']}' に接続成功")
        
        # コンテナへの接続
        print("\n3. コンテナに接続しています...")
        container = database.get_container_client(cosmos_container)
        container_properties = container.read()
        print(f"   ✓ コンテナ '{container_properties['id']}' に接続成功")
        
        # 基本的なクエリを実行（ドキュメント数の取得）
        print("\n4. クエリを実行しています...")
        items = list(container.query_items(
            query="SELECT VALUE COUNT(1) FROM c",
            enable_cross_partition_query=True
        ))
        doc_count = items[0] if items else 0
        print(f"   ✓ クエリ成功: コンテナ内のドキュメント数: {doc_count}")
        
        # テストドキュメントの作成
        print("\n5. テストドキュメントを作成しています...")
        test_doc_id = f"test-doc-{int(time.time())}"
        test_doc = {
            "id": test_doc_id,
            "title": "接続テストドキュメント",
            "content": "これはCosmosDB接続テスト用のドキュメントです。",
            "test": True,
            "timestamp": time.time()
        }
        
        container.create_item(body=test_doc)
        print(f"   ✓ テストドキュメント '{test_doc_id}' の作成に成功")
        
        # テストドキュメントの読み取り
        print("\n6. テストドキュメントを読み取っています...")
        read_doc = container.read_item(item=test_doc_id, partition_key=test_doc_id)
        print(f"   ✓ テストドキュメントの読み取りに成功: {read_doc['title']}")
        
        # テストドキュメントの削除
        print("\n7. テストドキュメントを削除しています...")
        container.delete_item(item=test_doc_id, partition_key=test_doc_id)
        print(f"   ✓ テストドキュメントの削除に成功")
        
        print("\n===== テスト結果 =====")
        print("すべてのテストが成功しました！CosmosDBに正常に接続できています。")
        return True
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"\nエラー: CosmosDB HTTPエラー: {e.status_code} - {e.message}")
        if e.status_code == 403:
            print("認証エラーの可能性があります。Cosmos DBのキーを確認してください。")
        elif e.status_code == 404:
            print("リソースが見つかりません。データベースまたはコンテナ名を確認してください。")
        return False
        
    except exceptions.CosmosResourceNotFoundError as e:
        print(f"\nエラー: リソースが見つかりません: {str(e)}")
        print("データベースまたはコンテナが存在しない可能性があります。")
        
        # データベースとコンテナの作成を提案
        create_resources = input("\nデータベースとコンテナを作成しますか？ (y/n): ")
        if create_resources.lower() == 'y':
            try:
                print(f"データベース '{cosmos_database}' を作成しています...")
                database = client.create_database_if_not_exists(id=cosmos_database)
                
                print(f"コンテナ '{cosmos_container}' を作成しています...")
                container = database.create_container_if_not_exists(
                    id=cosmos_container,
                    partition_key="/id",
                    offer_throughput=400
                )
                print("データベースとコンテナの作成に成功しました。")
                return True
            except Exception as create_error:
                print(f"リソース作成中にエラーが発生しました: {str(create_error)}")
                return False
        return False
        
    except Exception as e:
        print(f"\nエラー: 予期しないエラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    # 環境変数を読み込む
    load_env_vars()
    
    # CosmosDBへの接続テスト
    success = test_cosmos_connection()
    
    # 終了コードを設定
    sys.exit(0 if success else 1)
