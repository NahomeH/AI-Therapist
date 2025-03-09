/**
 * @fileoverview Main React component for the Talk2Me therapy chatbot application.
 * This component implements a chat interface using the chatscope UI kit,
 * providing real-time interaction with the therapy chatbot.
 */

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../Authentication/AuthContext";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  ConversationHeader,
  Avatar
} from "@chatscope/chat-ui-kit-react";
import { ArrowLeft, Mic, Keyboard, Save } from "lucide-react";
import "./ChatInterface.css";

function ChatInterface() {
  const { user, signOut } = useAuth();
  console.log("Current user:", {user});
  const [messages, setMessages] = useState([]);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [hasSelectedMode, setHasSelectedMode] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  // Add recognition state
  const [recognition, setRecognition] = useState(null);
  // Add state for mode change warning modal
  const [showWarningModal, setShowWarningModal] = useState(false);
  // Add state for save chat modal
  const [showSaveChatModal, setShowSaveChatModal] = useState(false);
  const [saveChatStatus, setSaveChatStatus] = useState('initial'); // 'initial', 'saving', 'saved'

  const playAudio = async (audioData) => {
    try {
      // Convert base64 to ArrayBuffer
      const binaryString = window.atob(audioData);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Create and play audio
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await audioContext.decodeAudioData(bytes.buffer);
      const source = audioContext.createBufferSource();

      setIsPlaying(true);
      source.onended = () => {
        setIsPlaying(false);
      }
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      source.start(0);
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
    }
  };

  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;

    const newMessage = { message: text, sender: "user", timestamp: new Date() };
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);
    setIsTyping(true);

    try {
      // Get bot response
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          sessionId: user?.id || 'default',
          userId: user?.id || 'anonymous',
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

      if (isVoiceMode && data.audioData) {
        playAudio(data.audioData);
      }

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
  }, [messages, isVoiceMode]);

  // Update the useEffect for speech recognition to include handleSend
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let transcript = '';

        recognition.onresult = (event) => {
          const newText = event.results[event.resultIndex][0].transcript;
          transcript += newText;
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsRecording(false);
        };

        recognition.onend = () => {
          if (transcript.trim()) {
            handleSend(transcript);
            transcript = '';
          }
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
  const initializeChat = async (mode) => {
    setIsVoiceMode(mode);
    setHasSelectedMode(true);
    setIsTyping(true);
    try {
      // Call the firstChat API to get the initial message
      const response = await fetch('http://127.0.0.1:5000/api/firstChat', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId: user?.id || 'default',
          userId: user?.id || 'anonymous',
          userName: user?.user_metadata?.preferred_name || 'there'
        })
      });

      console.log('First chat response:', response);
      const data = await response.json();
      
      if (data.success) {
        let welcomeMessage = data.message;
        // Add mode-specific instructions
        if (mode) {
          welcomeMessage += ' Press space to start speaking.';
        }
        
        setMessages([{ 
          message: welcomeMessage, 
          sender: "bot" 
        }]);
      } else {
        // Fallback message if API call fails
        setMessages([{ 
          message: `Hi, I'm Jennifer! ${mode ? 'Press space to start speaking.' : 'What\'s on your mind?'}`, 
          sender: "bot" 
        }]);
      }
    } catch (error) {
      console.error('Error initializing chat:', error);
      // Fallback message if API call fails
      setMessages([{ 
        message: `Hi, I'm Jennifer! ${mode ? 'Press space to start speaking.' : 'What\'s on your mind?'}`, 
        sender: "bot" 
      }]);
    } finally {
      setIsTyping(false);
    }
  };
  
  // Show warning modal when back button is clicked
  const handleBackButtonClick = () => {
    setShowWarningModal(true);
  };
  
  // Confirm going back to mode selection
  const confirmModeChange = () => {
    // Reset any ongoing recordings if in voice mode
    if (isVoiceMode && isRecording && recognition) {
      recognition.stop();
      setIsRecording(false);
    }
    setHasSelectedMode(false);
    setShowWarningModal(false);
  };
  
  // Cancel mode change
  const cancelModeChange = () => {
    setShowWarningModal(false);
  };

  // Handle save chat button click
  const handleSaveChatClick = () => {
    setShowSaveChatModal(true);
    setSaveChatStatus('initial');
  };

  // Saving chat
  const saveChat = async () => {
    setSaveChatStatus('saving');
    const response = await fetch('http://127.0.0.1:5000/api/save', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sessionId: user?.id || 'default'
      })
    });
    const data = await response.json();
    console.log('Save chat response:', data);
    setSaveChatStatus('saved');
  };

  // Handle end session
  const handleEndSession = () => {
    signOut();
    setShowSaveChatModal(false);
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
        <div className="chat-layout">
            <div className="chat-window">
            <button onClick={handleBackButtonClick} className="back-button" title="Go back to chat mode selection">
                <ArrowLeft size={20} />
                <span>Change Chat Mode</span>
                {isVoiceMode ? <Mic size={16} /> : <Keyboard size={16} />}
            </button>
            <MainContainer>
                <ChatContainer>
                <ConversationHeader>
                    <ConversationHeader.Content userName="Jennifer" />
                    <ConversationHeader.Actions>
                      <button onClick={handleSaveChatClick} className="save-chat-button">
                        <Save size={16} />
                        Save Chat
                      </button>
                    </ConversationHeader.Actions>
                </ConversationHeader>
                <MessageList 
                typingIndicator={
                    isTyping ? (
                      <TypingIndicator content="Jennifer is thinking..." /> 
                    ) : (
                      isVoiceMode && !isPlaying && !isRecording ? (
                        <div className="voice-space-hint">Press space to start speaking</div>
                      ) : isVoiceMode && isRecording ? (
                        <div className="voice-space-hint">Recording... Press space when done</div>
                      ) : null
                    )
                }
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
                        sendButton={false}
                        className="message-input"
                    />
                )}
                </ChatContainer>
            </MainContainer>
            </div>
        </div>
      )}
      
      {/* Warning Modal */}
      {showWarningModal && (
        <div className="modal-overlay">
          <div className="warning-modal">
            <div className="warning-icon">⚠️</div>
            <h3>Change Chat Mode?</h3>
            <p>Your current conversation will be reset if you return to mode selection.</p>
            <div className="modal-buttons">
              <button className="modal-button cancel" onClick={cancelModeChange}>
                Cancel
              </button>
              <button className="modal-button confirm" onClick={confirmModeChange}>
                Change Mode
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Save Chat Modal */}
      {showSaveChatModal && (
        <div className="modal-overlay">
          <div className="warning-modal save-chat-modal">
            {saveChatStatus === 'initial' && (
              <>
                <div className="warning-icon">💾</div>
                <h3>Save Chat</h3>
                <p>Would you like to save this chat to memory?</p>
                <div className="modal-buttons">
                  <button className="modal-button cancel" onClick={() => setShowSaveChatModal(false)}>
                    Cancel
                  </button>
                  <button className="modal-button confirm" onClick={saveChat}>
                    Save Chat
                  </button>
                </div>
              </>
            )}
            
            {saveChatStatus === 'saving' && (
              <>
                <div className="saving-spinner"></div>
                <h3>Saving chat to memory...</h3>
              </>
            )}
            
            {saveChatStatus === 'saved' && (
              <>
                <div className="success-icon">✅</div>
                <h3>Chat saved successfully!</h3>
                <div className="modal-buttons single-button">
                  <button className="modal-button end-session" onClick={handleEndSession}>
                    End Session
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );  
}
export default ChatInterface;