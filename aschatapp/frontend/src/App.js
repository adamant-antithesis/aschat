import React, { useState } from 'react';
import Login from './components/Login';
import ChatList from './components/ChatList';
import ChatRoom from './components/ChatRoom';

function App() {
  const [auth, setAuth] = useState(null);
  const [selectedChat, setSelectedChat] = useState(null);

  const handleLogin = (authData) => {
    setAuth(authData);
  };

  const handleChatSelect = (chatId) => {
    setSelectedChat(chatId);
  };

  const handleLogout = () => {
    setAuth(null);
    setSelectedChat(null);
  };

  return (
    <div className="app">
      {!auth ? (
        <Login onLogin={handleLogin} />
      ) : !selectedChat ? (
        <ChatList
          token={auth.token}
          onChatSelect={handleChatSelect}
          onLogout={handleLogout}
        />
      ) : (
        <ChatRoom
          token={auth.token}
          chatId={selectedChat}
          onBack={() => setSelectedChat(null)}
          username={auth.username}
        />
      )}
    </div>
  );
}

export default App;