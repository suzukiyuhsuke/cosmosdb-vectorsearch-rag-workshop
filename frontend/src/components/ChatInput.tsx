import React, { useState, FormEvent } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="質問を入力してください..."
        className="chat-input"
        disabled={isLoading}
      />
      <button 
        type="submit" 
        className="send-button"
        disabled={!message.trim() || isLoading}
      >
        {isLoading ? <span className="loading-indicator"></span> : '送信'}
      </button>
    </form>
  );
};

export default ChatInput;
