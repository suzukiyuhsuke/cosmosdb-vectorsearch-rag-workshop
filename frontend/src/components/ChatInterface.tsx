import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { ragApi } from '../services/api';
import { Message } from '../types';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // チャットが更新されたら自動的に一番下にスクロール
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    // ユーザーメッセージをチャットに追加
    const userMessage: Message = { text, isUser: true };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // 読み込み中の状態にする
    setIsLoading(true);
    
    try {
      // APIにクエリを送信
      const response = await ragApi.sendQuery(text);
      
      // ボットの回答をチャットに追加
      const botMessage: Message = { 
        text: response.answer, 
        isUser: false,
        sources: response.sources 
      };
      
      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('エラーが発生しました:', error);
      
      // エラーメッセージをチャットに追加
      const errorMessage: Message = { 
        text: '申し訳ありません、エラーが発生しました。もう一度お試しください。', 
        isUser: false 
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>RAGチャットボットへようこそ！</h3>
            <p>質問を入力すると、関連する知識を検索して回答します。</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage key={index} message={message} isUser={message.isUser} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatInterface;
