import React, { useState, useEffect } from 'react';

function ChatList({ token, onChatSelect, onLogout }) {
  const [chats, setChats] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await fetch('http://localhost/api/chats/', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch chats');
        }

        const data = await response.json();
        setChats(data);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchChats();
  }, [token]);

  return (
    <div className="chat-list">
      <h2>Available Chats</h2>
      <button onClick={onLogout}>Logout</button>
      {error && <p className="error">{error}</p>}
      <ul>
        {chats.map((chat) => (
          <li key={chat.id} onClick={() => onChatSelect(chat.id)}>
            {chat.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ChatList;