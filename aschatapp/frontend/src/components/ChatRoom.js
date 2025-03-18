import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatRoom.css';

function ChatRoom({ token, chatId, onBack, username }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [displayedMessages, setDisplayedMessages] = useState([]);
  const [visibleDate, setVisibleDate] = useState('');
  const [popupVisible, setPopupVisible] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [showImageModal, setShowImageModal] = useState(false);
  const [modalImage, setModalImage] = useState('');
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const previousScrollHeightRef = useRef(0);
  const previousScrollTopRef = useRef(0);
  const lastVisibleDateRef = useRef('');

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost/ws/chat/${chatId}?token=${token}`);

    websocket.onopen = () => {
      console.log('WebSocket connected successfully');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { username: msgUsername, content, image } = data;
        const timeStart = content.indexOf('[');
        const timeEnd = content.indexOf('] ', timeStart);
        const msgTime = timeStart !== -1 && timeEnd !== -1 ? content.slice(timeStart + 1, timeEnd) : '';
        const msgContent = timeStart !== -1 && timeEnd !== -1 ? content.slice(timeEnd + 2) : content;

        setMessages((prev) => [
          ...prev,
          { 
            username: msgUsername, 
            time: msgTime, 
            content: msgContent,
            image: image 
          },
        ]);
      } catch (error) {
        console.error('Failed to parse message:', error);
        setMessages((prev) => [...prev, { username: 'Unknown', content: event.data, time: '', image: null }]);
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
      websocket.close();
    };
  }, [chatId, token]);

  useEffect(() => {
    if (messages.length > 30) {
      setDisplayedMessages(messages.slice(-30));
    } else {
      setDisplayedMessages(messages);
    }
  }, [messages]);

  useEffect(() => {
    if (previousScrollHeightRef.current !== 0) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight - previousScrollHeightRef.current + previousScrollTopRef.current;
    } else {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    previousScrollHeightRef.current = 0;
    previousScrollTopRef.current = 0;
  }, [displayedMessages]);

  const handleScroll = () => {
    if (messagesContainerRef.current.scrollTop === 0 && displayedMessages.length < messages.length) {
      previousScrollHeightRef.current = messagesContainerRef.current.scrollHeight;
      previousScrollTopRef.current = messagesContainerRef.current.scrollTop;

      const remainingMessages = messages.length - displayedMessages.length;
      const newDisplayedMessagesCount = remainingMessages > 30 ? 30 : remainingMessages;
      setDisplayedMessages(messages.slice(-displayedMessages.length - newDisplayedMessagesCount));
    }

    const messageElements = Array.from(messagesContainerRef.current.getElementsByClassName('message'));
    let firstVisibleElement = null;

    for (const element of messageElements) {
      if (element.getBoundingClientRect().top >= messagesContainerRef.current.getBoundingClientRect().top) {
        firstVisibleElement = element;
        break;
      }
    }

    if (firstVisibleElement) {
      const newVisibleDate = new Date(firstVisibleElement.getAttribute('data-time')).toLocaleDateString();

      if (newVisibleDate !== lastVisibleDateRef.current) {
        setVisibleDate(newVisibleDate);
        setPopupVisible(true);
        lastVisibleDateRef.current = newVisibleDate;

        setTimeout(() => {
          setPopupVisible(false);
        }, 3000);
      }
    }
  };

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB
        alert('Файл слишком большой. Максимальный размер: 5MB');
        return;
      }
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(file);
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeSelectedImage = () => {
    setSelectedImage(null);
    setImagePreview('');
    fileInputRef.current.value = '';
  };

  const sendMessage = () => {
    if (ws && (message.trim() || selectedImage)) {
      const messageData = {
        image: imagePreview,
        message: message.trim(),
      };
      console.log('Отправка сообщения:', messageData);
      ws.send(JSON.stringify(messageData));
      setMessage('');
      removeSelectedImage();
    }
  };

  const openImageModal = (imageUrl) => {
    setModalImage(imageUrl);
    setShowImageModal(true);
  };

  return (
    <div className="chat-room">
      <div className="chat-header">
        <h2 className="chat-title">Chat {chatId}</h2>
        <button onClick={onBack} className="back-button">Back to Chat List</button>
      </div>
      <div className="messages" onScroll={handleScroll} ref={messagesContainerRef}>
        {popupVisible && visibleDate && <div className="date-popup">{visibleDate}</div>}

        {displayedMessages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.username === username ? 'my-message' : 'other-message'}`}
            data-time={msg.time}
          >
            {msg.username === username ? (
              <div className="my-message-content">
                {msg.image && (
                  <img
                    src={msg.image}
                    alt="Прикрепленное изображение"
                    className="message-image"
                    onClick={() => openImageModal(msg.image)}
                  />
                )}
                <span className="content">{msg.content}</span>
                <span className="time" data-time={msg.time}>{msg.time.split(' ')[1]}</span>
              </div>
            ) : (
              <div className="other-message-content">
                <span className="username">{msg.username}</span>
                <div className="content-wrapper">
                  {msg.image && (
                    <img
                      src={msg.image}
                      alt="Прикрепленное изображение"
                      className="message-image"
                      onClick={() => openImageModal(msg.image)}
                    />
                  )}
                  <span className="content">{msg.content}</span>
                  <span className="time" data-time={msg.time}>{msg.time.split(' ')[1]}</span>
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {imagePreview && (
        <div className="attachment-preview">
          <img src={imagePreview} alt="Предпросмотр" />
          <button onClick={removeSelectedImage}>×</button>
        </div>
      )}

      <div className="input-area">
        <button
          className="attachment-button"
          onClick={() => fileInputRef.current.click()}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
          </svg>
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageSelect}
          accept="image/*"
          style={{ display: 'none' }}
        />
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className="message-input"
          placeholder="Введите сообщение..."
        />
        <button onClick={sendMessage} className="send-button">Отправить</button>
      </div>

      {showImageModal && (
        <div className="image-modal" onClick={() => setShowImageModal(false)}>
          <img src={modalImage} alt="Увеличенное изображение" />
        </div>
      )}
    </div>
  );
}

export default ChatRoom;