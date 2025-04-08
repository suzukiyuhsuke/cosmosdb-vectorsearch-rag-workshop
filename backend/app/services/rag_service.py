from app.services.cosmos_service import CosmosService
from app.services.openai_service import OpenAIService

class RAGService:
    def __init__(self):
        self.cosmos_service = CosmosService()
        self.openai_service = OpenAIService()
    
    def initialize(self):
        """RAGサービスの初期化"""
        return self.cosmos_service.initialize_database()
    
    def add_document(self, title, content):
        """
        知識ベースにドキュメントを追加
        
        Args:
            title: ドキュメントのタイトル
            content: ドキュメントの内容
        
        Returns:
            dict: 追加されたドキュメント
        """
        return self.cosmos_service.add_document(title, content)
    
    def process_query(self, query):
        """
        RAGを使用してクエリを処理
        
        Args:
            query: ユーザーの質問
        
        Returns:
            dict: 回答と使用されたコンテキスト
        """
        try:
            # 関連ドキュメントを検索
            docs = self.cosmos_service.search_documents(query)
            
            # ドキュメントが見つからない場合
            if not docs:
                return {
                    "answer": "申し訳ありませんが、関連する情報が見つかりませんでした。",
                    "sources": []
                }
            
            # 検索結果を使用して回答を生成
            answer = self.openai_service.generate_response(query, docs)
            
            # ソース情報を整形
            sources = [{"title": doc["title"], "content_preview": doc["content"][:200] + "..."} for doc in docs]
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            print(f"クエリ処理中にエラーが発生しました: {str(e)}")
            raise
