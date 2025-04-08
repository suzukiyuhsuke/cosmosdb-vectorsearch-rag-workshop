import axios from 'axios';
import { QueryResponse, DocumentResponse } from '../types';

const API_URL = '/api/v1';

// Axiosインスタンスの作成
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// RAG関連のAPI
export const ragApi = {
  // 質問を送信して回答を取得
  async sendQuery(query: string): Promise<QueryResponse> {
    try {
      const response = await apiClient.post<QueryResponse>('/rag/query', { query });
      return response.data;
    } catch (error) {
      console.error('クエリ送信中にエラーが発生しました:', error);
      throw error;
    }
  },

  // 新しいドキュメントを追加
  async addDocument(title: string, content: string): Promise<DocumentResponse> {
    try {
      const response = await apiClient.post<DocumentResponse>('/rag/documents', { title, content });
      return response.data;
    } catch (error) {
      console.error('ドキュメント追加中にエラーが発生しました:', error);
      throw error;
    }
  }
};

export default {
  rag: ragApi
};
