import React, { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Copy, Download, Trash2 } from "lucide-react";
import axios from "axios";
import "./chat.css";

const api = axios.create({ withCredentials: true });

function errorText(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(", ");
  return "Request failed. Please try again.";
}

const GOOGLE_CLIENT_ID = import.meta.env?.VITE_GOOGLE_CLIENT_ID || "";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [user, setUser] = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });
  const [authBusy, setAuthBusy] = useState(false);
  const [authError, setAuthError] = useState("");
  const messagesEndRef = useRef(null);
  const googleButtonRef = useRef(null);

  useEffect(() => {
    let active = true;
    api.get("/api/auth/me")
      .then((response) => { if (active) setUser(response.data.user); })
      .catch((error) => {
        if (active && error.response?.status !== 401) {
          setAuthError("Account service is temporarily unavailable.");
        }
      })
      .finally(() => { if (active) setAuthReady(true); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!authReady || user || !GOOGLE_CLIENT_ID) return undefined;
    let active = true;
    const renderGoogleButton = () => {
      if (!active || !window.google?.accounts?.id || !googleButtonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: async (credentialResponse) => {
          if (!credentialResponse?.credential) {
            setAuthError("Google did not return a sign-in credential.");
            return;
          }
          setAuthBusy(true);
          setAuthError("");
          try {
            const response = await api.post("/api/auth/google", {
              credential: credentialResponse.credential,
            });
            setUser(response.data.user);
          } catch (error) {
            setAuthError(errorText(error));
          } finally {
            setAuthBusy(false);
          }
        },
      });
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        type: "standard",
        theme: "filled_black",
        size: "large",
        shape: "rectangular",
        text: "continue_with",
        width: 340,
      });
    };
    const existing = document.getElementById("google-identity-services");
    if (window.google?.accounts?.id) {
      renderGoogleButton();
    } else if (existing) {
      existing.addEventListener("load", renderGoogleButton, { once: true });
    } else {
      const script = document.createElement("script");
      script.id = "google-identity-services";
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = renderGoogleButton;
      script.onerror = () => setAuthError("Google sign-in could not load. Use email login instead.");
      document.head.appendChild(script);
    }
    return () => { active = false; };
  }, [authReady, user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const submitAuth = async (event) => {
    event.preventDefault();
    if (authBusy) return;
    setAuthBusy(true);
    setAuthError("");
    try {
      const endpoint = authMode === "signup" ? "/api/auth/signup" : "/api/auth/login";
      const payload = authMode === "signup"
        ? { name: authForm.name.trim(), email: authForm.email.trim(), password: authForm.password }
        : { email: authForm.email.trim(), password: authForm.password };
      const response = await api.post(endpoint, payload);
      setUser(response.data.user);
      setAuthForm({ name: "", email: "", password: "" });
    } catch (error) {
      setAuthError(errorText(error));
    } finally {
      setAuthBusy(false);
    }
  };

  const logout = async () => {
    try {
      await api.post("/api/auth/logout");
    } finally {
      setUser(null);
      setMessages([]);
      setConversationId(null);
    }
  };

  const sendMessage = async () => {
    const messageText = input.trim();
    if (!messageText || isLoading) return;
    const userMessage = {
      id: Date.now(),
      content: messageText,
      role: "user",
      timestamp: new Date(),
    };
    setMessages((previous) => [...previous, userMessage]);
    setInput("");
    setIsLoading(true);
    try {
      const response = await api.post("/api/chat", {
        message: messageText,
        conversation_id: conversationId,
        context: messages.slice(-10),
      });
      setMessages((previous) => [...previous, {
        id: Date.now() + 1,
        content: response.data.response || response.data.reply || "Tamanna AI returned an empty response.",
        role: "assistant",
        timestamp: new Date(),
      }]);
      setConversationId(response.data.conversationId || response.data.conversation_id || conversationId);
    } catch (error) {
      {
        setMessages((previous) => [...previous, {
          id: Date.now() + 1,
          content: errorText(error),
          role: "assistant",
          timestamp: new Date(),
          isError: true,
        }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = (content) => {
    if (navigator.clipboard?.writeText) navigator.clipboard.writeText(content);
  };

  const exportConversation = () => {
    const conversationText = messages
      .map((message) => `${message.role === "user" ? "You" : "Tamanna AI"}: ${message.content}`)
      .join("\n\n");
    const blob = new Blob([conversationText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `tamanna-ai-conversation-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  if (!authReady) {
    return <div className="chat-auth-loading" role="status">Checking your Tamanna AI session…</div>;
  }


  return (
    <div className="chat-page">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-title-group">
            <h1>Chat with Tamanna AI</h1>
            <span className="chat-account"><span className="chat-online-dot" />{user ? user.name + " · " + user.email : "Guest chat · no login required"}</span>
          </div>
          <div className="chat-actions">
            <button onClick={exportConversation} className="btn btn-secondary" disabled={messages.length === 0}><Download size={16} />Export</button>
            <button onClick={clearConversation} className="btn btn-secondary" disabled={messages.length === 0}><Trash2 size={16} />Clear</button>
            {!user && <a className="btn btn-secondary" href="/login">Log in</a>}
          </div>
        </div>
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Bot size={64} className="empty-icon" />
              <h2>How can I help you today?</h2>
              <p>Your Tamanna AI conversation is ready. Ask a question or start with an idea.</p>
            </div>
          ) : messages.map((message) => (
            <div key={message.id} className={`message ${message.role} ${message.isError ? "error" : ""}`}>
              <div className="message-avatar">{message.role === "user" ? <User size={20} /> : <Bot size={20} />}</div>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-sender">{message.role === "user" ? "You" : "Tamanna AI"}</span>
                  <span className="message-time">{message.timestamp.toLocaleTimeString()}</span>
                </div>
                <div className="message-text">{message.content}</div>
                {message.role === "assistant" && <button onClick={() => copyMessage(message.content)} className="copy-btn" title="Copy message" aria-label="Copy message"><Copy size={14} /></button>}
              </div>
            </div>
          ))}
          {isLoading && <div className="message assistant"><div className="message-avatar"><Bot size={20} /></div><div className="message-content"><div className="typing-indicator"><span>Tamanna AI is thinking</span><div className="typing-dots"><div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" /></div></div></div></div>}
          <div ref={messagesEndRef} />
        </div>
        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={handleKeyPress} placeholder="Message Tamanna AI… (Enter to send)" className="chat-input" rows="1" disabled={isLoading} />
            <button onClick={sendMessage} disabled={!input.trim() || isLoading} className="send-btn" aria-label="Send message"><Send size={20} /></button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
