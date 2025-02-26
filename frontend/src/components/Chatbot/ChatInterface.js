/**
 * @fileoverview Main React component for the Talk2Me therapy chatbot application.
 * This component implements a chat interface using the chatscope UI kit,
 * providing real-time interaction with the therapy chatbot.
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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
import { LogOut } from 'lucide-react';
import "./ChatInterface.css";

function ChatInterface() {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  console.log("Current user:", {user});
  const [messages, setMessages] = useState([
    { message: "Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?", sender: "bot" },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/auth');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleSend = async (text) => {
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
          sessionId: 'default'
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
  };

  return (
    <div className="app-container">
      <div className="chat-layout">
        <div className="chat-window">
          <MainContainer>
            <ChatContainer>
              <ConversationHeader>
                <ConversationHeader.Content userName="Jennifer" />
                <ConversationHeader.Actions>
                  <button 
                    onClick={handleLogout}
                    className="logout-button"
                  >
                    <LogOut size={20} />
                    <span>Logout</span>
                  </button>
                </ConversationHeader.Actions>
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
              <MessageInput 
                placeholder="Type your message here..."
                onSend={handleSend}
                attachButton={false}
                className="message-input"
              />
            </ChatContainer>
          </MainContainer>
        </div>
      </div>
    </div>
  );  
}
export default ChatInterface;

