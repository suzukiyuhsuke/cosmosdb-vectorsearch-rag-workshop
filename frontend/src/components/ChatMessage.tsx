import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      <div className="message-content">
        {isUser ? (
          <p>{message.text}</p>
        ) : (
          <>
            <ReactMarkdown>{message.text}</ReactMarkdown>
            
            {message.sources && message.sources.length > 0 && (
              <div className="sources-container">
                <h4>参照情報:</h4>
                {message.sources.map((source, index) => (
                  <div key={index} className="source-item">
                    <div className="source-title">{source.title}</div>
                    <div className="source-preview">{source.content_preview}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
