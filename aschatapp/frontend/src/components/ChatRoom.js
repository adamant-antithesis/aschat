import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatRoom.css';

function ChatRoom({ token, chatId, onBack, username }) {
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
      try {
        const data = JSON.parse(event.data);
        const { username: msgUsername, content } = data;
        const timeStart = content.indexOf('[');
        const timeEnd = content.indexOf('] ', timeStart);
        const msgTime = timeStart !== -1 && timeEnd !== -1 ? content.slice(timeStart + 1, timeEnd) : '';
        const msgContent = timeStart !== -1 && timeEnd !== -1 ? content.slice(timeEnd + 2) : content;

        setMessages((prev) => [
          ...prev,
          { username: msgUsername, time: msgTime, content: msgContent },
        ]);
      } catch (error) {
        console.error('Failed to parse message:', error);
        setMessages((prev) => [...prev, { username: 'Unknown', content: event.data, time: '' }]);
      }
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
          <div
            key={index}
            className={`message ${
              msg.username === username ? 'my-message' : 'other-message'
            }`}
          >
            {msg.username === username ? (
              <div className="my-message-content">
                <span className="content">{msg.content}</span>
                <span className="time">{msg.time}</span>
              </div>
            ) : (
              <div className="other-message-content">
                <span className="username">{msg.username}</span>
                <div className="content-wrapper">
                  <span className="content">{msg.content}</span>
                  <span className="time">{msg.time}</span>
                </div>
              </div>
            )}
          </div>
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