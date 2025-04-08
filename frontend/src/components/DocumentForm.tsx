import React, { useState, FormEvent } from 'react';
import { ragApi } from '../services/api';

interface StatusState {
  message: string;
  isError: boolean;
}

const DocumentForm: React.FC = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState<StatusState>({ message: '', isError: false });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !content.trim()) {
      setStatus({
        message: 'タイトルと内容は必須です',
        isError: true
      });
      return;
    }
    
    try {
      setIsSubmitting(true);
      const result = await ragApi.addDocument(title, content);
      
      setStatus({
        message: `ドキュメント「${result.title}」が正常に追加されました`,
        isError: false
      });
      
      // フォームをクリア
      setTitle('');
      setContent('');
    } catch (error: any) {
      setStatus({
        message: `エラーが発生しました: ${error.response?.data?.detail || error.message}`,
        isError: true
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="document-form">
      <h2 className="form-title">新しい知識を追加</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title" className="form-label">タイトル</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="form-input"
            placeholder="ドキュメントのタイトル"
            disabled={isSubmitting}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="content" className="form-label">内容</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="form-textarea"
            placeholder="ドキュメントの内容"
            disabled={isSubmitting}
          />
        </div>
        
        <button 
          type="submit" 
          className="form-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? '追加中...' : 'ドキュメントを追加'}
        </button>
        
        {status.message && (
          <div className={status.isError ? "error-message" : "success-message"}>
            {status.message}
          </div>
        )}
      </form>
    </div>
  );
};

export default DocumentForm;
