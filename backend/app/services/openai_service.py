from openai import AzureOpenAI
from app.config import (
    GPT_API_KEY,
    GPT_ENDPOINT,
    GPT_DEPLOYMENT,
    GPT_API_VERSION
)

class OpenAIService:
    def __init__(self):
        # Azure OpenAIクライアントの初期化
        self.client = AzureOpenAI(
            api_key=GPT_API_KEY,
            api_version=GPT_API_VERSION,
            azure_endpoint=GPT_ENDPOINT
        )
    
    def generate_response(self, query, context_docs):
        """
        検索結果のコンテキストを利用してGPT-4oでレスポンスを生成
        
        Args:
            query: ユーザーの質問
            context_docs: 検索結果のコンテキストドキュメント
        
        Returns:
            str: 生成された回答
        """
        try:
            # コンテキストを構築
            context = "\n\n".join([f"タイトル: {doc['title']}\n内容: {doc['content']}" for doc in context_docs])
            
            # プロンプトの構築
            messages = [
                {"role": "system", "content": "あなたは親切なアシスタントです。与えられたコンテキストに基づいて質問に回答してください。与えられたコンテキストがない場合でも、できるだけ正確に回答して下さい。"},
                {"role": "user", "content": f"以下のコンテキストを使用して質問に答えてください。\n\nコンテキスト:\n{context}\n\n質問: {query}"}
            ]
            
            # GPT-4oを使用して回答を生成
            response = self.client.chat.completions.create(
                model=GPT_DEPLOYMENT,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAIレスポンス生成中にエラーが発生しました: {str(e)}")
            raise
