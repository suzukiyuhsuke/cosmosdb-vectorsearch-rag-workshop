#!/usr/bin/env python
"""
サンプルドキュメントをCosmosDBに直接アップロードするスクリプト
"""

import os
import sys
import time
import pathlib
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
from openai import AzureOpenAI

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

def get_embedding(text):
    """
    テキストのベクトル埋め込みを取得する
    
    Args:
        text: 埋め込みするテキスト
    
    Returns:
        list: ベクトル埋め込み
    """
    if not text.strip():
        raise ValueError("テキストが空です")
    
    # Embeddingの設定を取得
    embedding_api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY") 
    embedding_endpoint = os.getenv("EMBEDDING_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
    embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT") or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    embedding_api_version = os.getenv("EMBEDDING_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    
    # 接続情報の確認
    if not embedding_api_key or not embedding_endpoint:
        raise ValueError("EMBEDDING_API_KEY(またはAZURE_OPENAI_API_KEY)とEMBEDDING_ENDPOINT(またはAZURE_OPENAI_ENDPOINT)の環境変数が必要です")
    
    # Azure OpenAIクライアントの初期化
    client = AzureOpenAI(
        api_key=embedding_api_key,
        api_version=embedding_api_version,
        azure_endpoint=embedding_endpoint
    )
    
    # ベクトル埋め込みを取得
    response = client.embeddings.create(
        input=text,
        model=embedding_deployment
    )
    
    return response.data[0].embedding

def load_markdown_files(directory="./sample_documents"):
    """指定ディレクトリ内のMarkdownファイルを読み込む"""
    directory_path = pathlib.Path(directory)
    if not directory_path.exists():
        # サンプルドキュメントディレクトリが現在の場所にない場合、上位ディレクトリを確認
        parent_dir = pathlib.Path("../sample_documents")
        if parent_dir.exists():
            directory_path = parent_dir
        else:
            # プロジェクトルートからの相対パスを試す
            project_dir = pathlib.Path("../../../sample_documents")
            if project_dir.exists():
                directory_path = project_dir
    
    print(f"ドキュメントディレクトリ: {directory_path.absolute()}")
    md_files = list(directory_path.glob("*.md"))
    
    if not md_files:
        print(f"警告: {directory_path}にMarkdownファイルが見つかりません")
        return []
    
    documents = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 最初の行をタイトルとして使用（# で始まる行）
            lines = content.split('\n')
            title = lines[0].lstrip('# ')
            
            documents.append({
                "file_path": str(file_path),
                "title": title,
                "content": content
            })
            
        except Exception as e:
            print(f"ファイル {file_path} の読み込み中にエラーが発生しました: {str(e)}")
    
    return documents

def upload_to_cosmos(documents):
    """ドキュメントをCosmosDBに直接アップロード"""
    # Cosmos DBの設定を取得
    cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    cosmos_database = os.getenv("COSMOS_DATABASE", "ragdatabase")
    cosmos_container = os.getenv("COSMOS_CONTAINER", "documents")
    
    # 接続情報の確認
    if not cosmos_endpoint or not cosmos_key:
        print("エラー: COSMOS_ENDPOINTとCOSMOS_KEYの環境変数が必要です")
        return 0, 0
    
    success_count = 0
    error_count = 0
    
    try:
        # CosmosDBクライアントの初期化
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        
        # データベースとコンテナの取得または作成
        database = client.create_database_if_not_exists(id=cosmos_database)
        container = database.create_container_if_not_exists(
            id=cosmos_container,
            partition_key="/id",
            offer_throughput=400
        )
        
        # ドキュメントのアップロード
        for doc in documents:
            try:
                print(f"処理中: {doc['title']} ({doc['file_path']})")
                
                # コンテンツのベクトル埋め込みを取得
                embedding = get_embedding(doc['content'])
                
                # ドキュメントを作成
                document = {
                    "id": str(hash(doc['title'] + doc['content'])),
                    "title": doc['title'],
                    "content": doc['content'],
                    "embedding": embedding,
                    "source": doc['file_path'],
                    "timestamp": time.time()
                }
                
                # Cosmos DBにドキュメントを保存
                container.create_item(body=document)
                print(f"✅ アップロード成功: {doc['title']}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ アップロード失敗: {doc['title']} - エラー: {str(e)}")
                error_count += 1
                
    except Exception as e:
        print(f"CosmosDBへの接続中にエラーが発生しました: {str(e)}")
        return success_count, error_count
    
    return success_count, error_count

def main():
    """メイン処理"""
    # 環境変数を読み込む
    load_env_vars()
    
    # コマンドライン引数の解析
    import argparse
    parser = argparse.ArgumentParser(description='サンプルドキュメントをCosmosDBにアップロード')
    parser.add_argument('--dir', default='./sample_documents', 
                       help='Markdownファイルのディレクトリ')
    args = parser.parse_args()
    
    # Markdownファイルを読み込む
    print(f"ディレクトリ {args.dir} からマークダウンファイルを読み込みます...")
    documents = load_markdown_files(args.dir)
    
    if not documents:
        print("ドキュメントが見つかりませんでした。終了します。")
        sys.exit(1)
    
    print(f"{len(documents)} 件のドキュメントを読み込みました")
    
    # ドキュメントをCosmosDBにアップロード
    print("\nCosmosDBにドキュメントをアップロードしています...")
    success, error = upload_to_cosmos(documents)
    
    # 結果を表示
    print("\n===== アップロード結果 =====")
    print(f"成功: {success} 件")
    print(f"失敗: {error} 件")
    print("===========================")

if __name__ == "__main__":
    main()
