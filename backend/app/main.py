from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api import rag
from app.config import API_PREFIX

# FastAPIアプリケーションの作成
app = FastAPI(
    title="RAG AIチャットボット API",
    description="Cosmos DB Vector SearchとAzure OpenAIを使用したRAGチャットボットのAPI",
    version="1.0.0"
)

# CORSミドルウェアを追加（フロントエンドからのリクエストを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンのみを許可するべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(rag.router, prefix=f"{API_PREFIX}/rag", tags=["RAG"])

# 静的ファイル用のディレクトリパス
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

# 静的ファイルディレクトリが存在する場合のみマウント
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # APIリクエストはAPI用のルーターで処理
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        
        # その他のルートはindex.htmlを返す（SPA対応）
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend files not found"}

@app.get("/")
async def root():
    # 静的ファイルが存在する場合はそちらを優先
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "RAG AIチャットボット APIへようこそ"}

@app.get(f"{API_PREFIX}/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
