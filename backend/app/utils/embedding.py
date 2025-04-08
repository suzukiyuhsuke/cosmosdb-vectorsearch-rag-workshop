from openai import AzureOpenAI
from app.config import (
    EMBEDDING_API_KEY,
    EMBEDDING_ENDPOINT,
    EMBEDDING_DEPLOYMENT,
    EMBEDDING_API_VERSION
)


print(f"Embedding API Key: {EMBEDDING_API_KEY}")
print(f"Embedding Endpoint: {EMBEDDING_ENDPOINT}") 
print(f"Embedding Deployment: {EMBEDDING_DEPLOYMENT}")
print(f"Embedding API Version: {EMBEDDING_API_VERSION}")
# Azure OpenAIクライアントの初期化
client = AzureOpenAI(
    api_key=EMBEDDING_API_KEY,
    api_version=EMBEDDING_API_VERSION,
    azure_endpoint=EMBEDDING_ENDPOINT
)

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
        
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_DEPLOYMENT
    )
    
    return response.data[0].embedding
