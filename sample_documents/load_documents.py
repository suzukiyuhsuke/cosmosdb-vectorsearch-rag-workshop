#!/usr/bin/env python
"""
サンプルドキュメントをRAGチャットボットのナレッジベースに一括でアップロードするスクリプト
"""

import os
import requests
import argparse
from pathlib import Path

def load_markdown_files(directory):
    """指定ディレクトリ内のMarkdownファイルを読み込む"""
    md_files = list(Path(directory).glob("*.md"))
    documents = []
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 最初の行をタイトルとして使用（# で始まる行）
        lines = content.split('\n')
        title = lines[0].lstrip('# ')
        
        documents.append({
            "title": title,
            "content": content
        })
    
    return documents

def upload_documents(api_url, documents):
    """ドキュメントをAPIにアップロード"""
    success_count = 0
    error_count = 0
    
    for doc in documents:
        try:
            response = requests.post(
                api_url, 
                json=doc
            )
            response.raise_for_status()
            
            print(f"アップロード成功: {doc['title']}")
            success_count += 1
            
        except Exception as e:
            print(f"アップロード失敗: {doc['title']} - エラー: {str(e)}")
            error_count += 1
    
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description='サンプルドキュメントをRAGチャットボットにアップロード')
    parser.add_argument('--url', default='http://localhost:8000/api/v1/rag/documents', 
                      help='ドキュメントアップロードAPIのURL')
    parser.add_argument('--dir', default='.', 
                      help='Markdownファイルのディレクトリ')
    args = parser.parse_args()
    
    print(f"ディレクトリ {args.dir} からマークダウンファイルを読み込みます...")
    documents = load_markdown_files(args.dir)
    print(f"{len(documents)} 件のドキュメントを読み込みました")
    
    print(f"APIエンドポイント {args.url} にアップロードを開始します...")
    success, error = upload_documents(args.url, documents)
    
    print("\n===== アップロード結果 =====")
    print(f"成功: {success} 件")
    print(f"失敗: {error} 件")
    print("===========================")

if __name__ == "__main__":
    main()
