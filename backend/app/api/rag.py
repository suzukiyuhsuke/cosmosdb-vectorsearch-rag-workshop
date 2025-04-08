from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

# 初期化が必要な場合にサービスを取得する依存関数
def get_initialized_rag_service():
    if not hasattr(get_initialized_rag_service, "initialized"):
        rag_service.initialize()
        get_initialized_rag_service.initialized = True
    return rag_service

# リクエスト/レスポンスモデル
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

class DocumentRequest(BaseModel):
    title: str
    content: str

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_initialized_rag_service)
):
    """
    ユーザーの質問を処理してRAGベースの回答を返す
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="質問が空です")
            
        result = rag_service.process_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"クエリ処理中にエラーが発生しました: {str(e)}")

@router.post("/documents", response_model=DocumentResponse)
async def add_document(
    request: DocumentRequest,
    rag_service: RAGService = Depends(get_initialized_rag_service)
):
    """
    知識ベースに新しいドキュメントを追加する
    """
    try:
        if not request.title.strip() or not request.content.strip():
            raise HTTPException(status_code=400, detail="タイトルまたは内容が空です")
            
        document = rag_service.add_document(request.title, request.content)
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ドキュメント追加中にエラーが発生しました: {str(e)}")
