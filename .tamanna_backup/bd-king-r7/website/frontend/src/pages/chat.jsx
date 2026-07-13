import React, { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Copy, Download, Trash2 } from "lucide-react";
import axios from "axios";
import "./Chat.css";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post("/api/chat", {
        message: input,
        conversationId,
        context: messages.slice(-10), // Send last 10 messages for context
      });

      const aiMessage = {
        id: Date.now() + 1,
        content: response.data.response,
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setConversationId(response.data.conversationId);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: Date.now() + 1,
        content: "Sorry, I encountered an error. Please try again.",
        role: "assistant",
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content);
  };

  const exportConversation = () => {
    const conversationText = messages
      .map(
        (msg) =>
          `${msg.role === "user" ? "You" : "BD-King-R7"}: ${msg.content}`,
      )
      .join("\n\n");

    const blob = new Blob([conversationText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bd-king-r7-conversation-${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div className="chat-header">
          <h1>Chat with BD-King-R7</h1>
          <div className="chat-actions">
            <button
              onClick={exportConversation}
              className="btn btn-secondary"
              disabled={messages.length === 0}
            >
              <Download size={16} />
              Export
            </button>
            <button
              onClick={clearConversation}
              className="btn btn-secondary"
              disabled={messages.length === 0}
            >
              <Trash2 size={16} />
              Clear
            </button>
          </div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Bot size={64} className="empty-icon" />
              <h2>Start a Conversation</h2>
              <p>
                Ask me anything - I'm here to help with questions, creative
                tasks, or just chat!
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role} ${message.isError ? "error" : ""}`}
              >
                <div className="message-avatar">
                  {message.role === "user" ? (
                    <User size={20} />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-sender">
                      {message.role === "user" ? "You" : "BD-King-R7"}
                    </span>
                    <span className="message-time">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-text">{message.content}</div>
                  {message.role === "assistant" && (
                    <button
                      onClick={() => copyMessage(message.content)}
                      className="copy-btn"
                      title="Copy message"
                    >
                      <Copy size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span>BD-King-R7 is thinking</span>
                  <div className="typing-dots">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Press Enter to send)"
              className="chat-input"
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="send-btn"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
