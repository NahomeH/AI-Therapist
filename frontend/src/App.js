/**
 * @fileoverview Main React component for the Talk2Me therapy chatbot application.
 * This component implements a chat interface using the chatscope UI kit,
 * providing real-time interaction with the therapy chatbot.
 */

import React, { useState, useEffect, useCallback } from "react";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  ConversationHeader,
  Avatar,
} from "@chatscope/chat-ui-kit-react";
import "./App.css";

/**
 * Main application component that renders the chat interface
 * and handles message exchange with the backend server.
 * 
 * @component
 * @returns {JSX.Element} The rendered chat interface
 */
function App() {
  const [messages, setMessages] = useState([
    { message: "Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?", sender: "bot" },
  ]);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [hasSelectedMode, setHasSelectedMode] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  // Add recognition state
  const [recognition, setRecognition] = useState(null);

  /**
   * Handles sending messages to the backend server and updating the chat UI.
   * 
   * @param {string} text - The message text to send
   * @returns {Promise<void>}
   */
  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;

    const newMessage = { message: text, sender: "user", timestamp: new Date() };
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);
    setIsTyping(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          sessionId: 'default',
          isVoiceMode: isVoiceMode
        })
      });

      const data = await response.json();
      const botMessage = {
        message: data.message,
        sender: "bot",
        timestamp: new Date()
      };
      setMessages([...newMessages, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        message: "Sorry, I'm having trouble connecting to the server.",
        sender: "bot",
        timestamp: new Date()
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [messages, isVoiceMode]); // Add messages as a dependency

  // Update the useEffect for speech recognition to include handleSend
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          handleSend(transcript);
          setIsRecording(false);
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsRecording(false);
        };

        recognition.onend = () => {
          setIsRecording(false);
        };

        setRecognition(recognition);
      }
    }
  }, [handleSend]); // Add handleSend as a dependency

  // Add toggle recording function
  const toggleRecording = useCallback(() => {
    if (!recognition) return;

    if (isRecording) {
      recognition.stop();
    } else {
      recognition.start();
      setIsRecording(true);
    }
  }, [recognition, isRecording]); // Add recognition and isRecording as dependencies

  // Update keyboard event handling to include toggleRecording
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (isVoiceMode && event.code === 'Space') {
        event.preventDefault();
        toggleRecording();
      }
    };

    if (isVoiceMode) {
      window.addEventListener('keydown', handleKeyPress);
      return () => window.removeEventListener('keydown', handleKeyPress);
    }
  }, [isVoiceMode, toggleRecording]); // Add toggleRecording as a dependency

  // Initialize chat after mode selection
  const initializeChat = (mode) => {
    setIsVoiceMode(mode);
    setHasSelectedMode(true);
    setMessages([{ 
        message: `Hi, I'm Jennifer! ${mode ? 'Press space to start speaking.' : 'What\'s on your mind?'}`, 
        sender: "bot" 
    }]);
  };



  return (
    <div className="app-container">
      {!hasSelectedMode ? (
        <div className="mode-selection">
          <h1>Welcome to Talk2Me</h1>
          <p>Choose how you'd like to interact:</p>
          <div className="mode-buttons">
          <button onClick={() => initializeChat(false)} className="mode-button text-mode">
            <span className="mode-icon">
                <span role="img" aria-label="keyboard">⌨️</span>
            </span>
            <span className="mode-label">Text Chat</span>
            <span className="mode-description">Type to communicate</span>
            </button>
          <button onClick={() => initializeChat(true)} className="mode-button voice-mode">
            <span className="mode-icon">
                <span role="img" aria-label="microphone">🎤</span>
            </span>
            <span className="mode-label">Voice Chat</span>
            <span className="mode-description">Speak to communicate</span>
          </button>
          </div>
        </div>
      ) : (
        <div className="chat-window">
            <MainContainer>
            <ChatContainer>
                <ConversationHeader>
                <ConversationHeader.Content 
                    userName="Jennifer"
                />
                </ConversationHeader>
                <MessageList 
                typingIndicator={isTyping ? <TypingIndicator content="Jennifer is thinking..." /> : null}
                className="message-list"
                >
                {messages.map((msg, i) => (
                    <Message 
                    key={i} 
                    model={{
                        message: msg.message,
                        sender: msg.sender,
                        direction: msg.sender === "user" ? "outgoing" : "incoming",
                        position: "single"
                    }}
                      avatarPosition={msg.sender === "bot" ? "tl" : undefined}
                      avatarSpacer={msg.sender === "user"}
                    >
                      {msg.sender === "bot" && (
                        <Avatar src="/robot-icon.png" name="Jennifer" />
                      )}
                    <Message.Header sender={msg.sender === "bot" ? "Jennifer" : "You"} />
                    </Message>
                ))}
                </MessageList>
                {isVoiceMode ? (
                    <div className="voice-controls">
                    <button 
                        onClick={toggleRecording}
                        className={`voice-button ${isRecording ? 'recording' : ''}`}
                    >
                        {isRecording ? 'Stop Recording' : 'Start Recording'}
                    </button>
                    </div>
                ) : (
                    <MessageInput 
                    placeholder="Type your message here..."
                    onSend={handleSend}
                    attachButton={false}
                    className="message-input"
                    />
                )}
            </ChatContainer>
            </MainContainer>
        </div>
      )}
    </div>
  );
}

export default App;
