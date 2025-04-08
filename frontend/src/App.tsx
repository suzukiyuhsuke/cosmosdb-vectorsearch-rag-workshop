import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import DocumentForm from './components/DocumentForm';
import './styles/App.css';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">RAGチャットボット</h1>
      </header>

      <div className="nav-tabs">
        <div 
          className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          チャット
        </div>
        <div 
          className={`nav-tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          知識の追加
        </div>
      </div>

      {activeTab === 'chat' ? (
        <ChatInterface />
      ) : (
        <DocumentForm />
      )}
    </div>
  );
};

export default App;
