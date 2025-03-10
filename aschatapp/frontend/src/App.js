import React, { useState } from 'react';
import Login from './components/Login';
import ChatList from './components/ChatList';
import ChatRoom from './components/ChatRoom';

function App() {
  const [token, setToken] = useState(null);
  const [selectedChat, setSelectedChat] = useState(null);

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleChatSelect = (chatId) => {
    setSelectedChat(chatId);
  };

  const handleLogout = () => {
    setToken(null);
    setSelectedChat(null);
  };

  return (
    <div className="app">
      {!token ? (
        <Login onLogin={handleLogin} />
      ) : !selectedChat ? (
        <ChatList token={token} onChatSelect={handleChatSelect} onLogout={handleLogout} />
      ) : (
        <ChatRoom token={token} chatId={selectedChat} onBack={() => setSelectedChat(null)} />
      )}
    </div>
  );
}

export default App;