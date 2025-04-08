import os
from dotenv import load_dotenv
import pathlib

# 環境変数を読み込む (.envファイルがカレントディレクトリまたは親ディレクトリにある場合)
env_path = pathlib.Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    parent_env_path = pathlib.Path('..') / '.env'
    if parent_env_path.exists():
        load_dotenv(dotenv_path=parent_env_path)
    else:
        load_dotenv()  # システム環境変数から読み込み

# Cosmos DB設定
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "ragdatabase")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "documents")

# GPT-4o設定
GPT_API_KEY = os.getenv("GPT_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")  # 後方互換性のため
GPT_ENDPOINT = os.getenv("GPT_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")  # 後方互換性のため
GPT_DEPLOYMENT = os.getenv("GPT_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
GPT_API_VERSION = os.getenv("GPT_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

# Embedding設定
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")  # 後方互換性のため
EMBEDDING_ENDPOINT = os.getenv("EMBEDDING_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")  # 後方互換性のため
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT") or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
EMBEDDING_API_VERSION = os.getenv("EMBEDDING_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

# アプリケーション設定
API_PREFIX = "/api/v1"

# 後方互換性のための変数（非推奨）
AZURE_OPENAI_API_KEY = GPT_API_KEY
AZURE_OPENAI_ENDPOINT = GPT_ENDPOINT
AZURE_OPENAI_DEPLOYMENT = GPT_DEPLOYMENT
AZURE_OPENAI_API_VERSION = GPT_API_VERSION
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = EMBEDDING_DEPLOYMENT
