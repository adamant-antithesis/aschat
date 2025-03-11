import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatRoom.css';

function ChatRoom({ token, chatId, onBack }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [ws, setWs] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    console.log('Connecting to WebSocket with token:', token);
    const websocket = new WebSocket(`ws://localhost/ws/chat/${chatId}?token=${token}`);

    websocket.onopen = () => {
      console.log('WebSocket connected successfully');
    };

    websocket.onmessage = (event) => {
      console.log('Message received:', event.data);
      setMessages((prev) => [...prev, event.data]);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = (event) => {
      console.log('WebSocket closed with code:', event.code, 'reason:', event.reason);
    };

    setWs(websocket);

    return () => {
      console.log('Cleaning up WebSocket');
      websocket.close();
    };
  }, [chatId, token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (ws && message.trim()) {
      console.log('Sending message:', message);
      ws.send(message);
      setMessage('');
    } else {
      console.log('Cannot send message: WebSocket not ready or message empty');
    }
  };

  return (
    <div className="chat-room">
      <h2>Chat {chatId}</h2>
      <button onClick={onBack} className="back-button">Back to Chat List</button>
      <div className="messages">
        {messages.map((msg, index) => (
          <p key={index} className="message">{msg}</p>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className="message-input"
          placeholder="Type a message..."
        />
        <button onClick={sendMessage} className="send-button">Send</button>
      </div>
    </div>
  );
}

export default ChatRoom;
