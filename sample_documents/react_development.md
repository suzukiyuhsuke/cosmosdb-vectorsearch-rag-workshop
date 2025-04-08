# React 開発ガイド

Reactは、Facebookが開発したユーザーインターフェイスを構築するためのJavaScriptライブラリです。

## Reactの主な特徴

- **コンポーネントベース**: UIを再利用可能なコンポーネントに分割
- **仮想DOM**: 効率的なDOM更新のための仮想DOMを使用
- **一方向データフロー**: 予測可能なデータの流れ
- **JSX**: JavaScriptの拡張構文でUIを宣言的に記述
- **大規模なエコシステム**: 豊富なライブラリとツール

## コンポーネントの作成

### 関数コンポーネント

```jsx
import React from 'react';

function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}

export default Welcome;
```

### Hooksを使用した状態管理

```jsx
import React, { useState, useEffect } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    document.title = `You clicked ${count} times`;
  }, [count]);
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## React Router

React Routerを使用してSPA（シングルページアプリケーション）でのルーティングを実装できます：

```jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## APIとの通信

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get('https://api.example.com/users');
        setUsers(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching users:', error);
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, []);
  
  if (loading) return <p>Loading...</p>;
  
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

## Viteを使用したReactプロジェクトの作成

Viteは高速な開発サーバーとビルドツールを提供します：

```bash
# プロジェクト作成
npm create vite@latest my-react-app -- --template react

# 依存関係のインストール
cd my-react-app
npm install

# 開発サーバー起動
npm run dev
```
