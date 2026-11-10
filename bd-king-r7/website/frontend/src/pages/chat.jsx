import React, { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Copy, Download, Trash2, LogOut, ShieldCheck } from "lucide-react";
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
    if (!messageText || isLoading || !user) return;
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
        conversationId,
        context: messages.slice(-10),
      });
      setMessages((previous) => [...previous, {
        id: Date.now() + 1,
        content: response.data.response,
        role: "assistant",
        timestamp: new Date(),
      }]);
      setConversationId(response.data.conversationId);
    } catch (error) {
      if (error.response?.status === 401) {
        setUser(null);
        setAuthError("Your session expired. Please sign in again.");
      } else {
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

  if (!user) {
    return (
      <section className="chat-auth-page">
        <div className="chat-auth-card">
          <div className="chat-auth-brand"><span className="chat-auth-logo">T</span><span>Tamanna AI</span></div>
          <div className="chat-auth-heading">
            <ShieldCheck size={22} />
            <h1>{authMode === "signup" ? "Create your account" : "Welcome back"}</h1>
            <p>{authMode === "signup" ? "Sign up to start a private conversation." : "Sign in to continue to your private chat."}</p>
          </div>
          <div className="chat-auth-tabs" role="tablist" aria-label="Account access">
            <button type="button" role="tab" aria-selected={authMode === "login"} className={authMode === "login" ? "active" : ""} onClick={() => { setAuthMode("login"); setAuthError(""); }}>Log in</button>
            <button type="button" role="tab" aria-selected={authMode === "signup"} className={authMode === "signup" ? "active" : ""} onClick={() => { setAuthMode("signup"); setAuthError(""); }}>Sign up</button>
          </div>
          {GOOGLE_CLIENT_ID ? (
            <div className="chat-google-wrap">
              <div className="chat-auth-divider"><span>or continue with Google</span></div>
              <div ref={googleButtonRef} className="chat-google-button" />
            </div>
          ) : (
            <p className="chat-google-setup">Google sign-in needs the same OAuth Client ID in VITE_GOOGLE_CLIENT_ID (frontend) and GOOGLE_CLIENT_ID (server). Email login is ready now.</p>
          )}
          <form className="chat-auth-form" onSubmit={submitAuth}>
            {authMode === "signup" && (
              <label>
                Full name
                <input autoComplete="name" value={authForm.name} onChange={(event) => setAuthForm({ ...authForm, name: event.target.value })} minLength={2} maxLength={80} required placeholder="Your name" />
              </label>
            )}
            <label>
              Gmail or email address
              <input type="email" inputMode="email" autoCapitalize="none" autoCorrect="off" autoComplete="email" value={authForm.email} onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })} maxLength={254} required placeholder="you@gmail.com" />
            </label>
            <label>
              Password
              <input type="password" autoComplete={authMode === "signup" ? "new-password" : "current-password"} value={authForm.password} onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })} minLength={authMode === "signup" ? 12 : 1} maxLength={128} required placeholder={authMode === "signup" ? "At least 12 characters" : "Your password"} />
            </label>
            {authError && <p className="chat-auth-error" role="alert">{authError}</p>}
            <button className="chat-auth-submit" type="submit" disabled={authBusy}>
              {authBusy ? "Please wait…" : authMode === "signup" ? "Create account" : "Log in to Tamanna AI"}
            </button>
          </form>
          <p className="chat-auth-note">Use your Gmail address or any valid email. New accounts are signed in automatically after signup.</p>
        </div>
      </section>
    );
  }

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-title-group">
            <h1>Chat with Tamanna AI</h1>
            <span className="chat-account"><span className="chat-online-dot" />{user.name} · {user.email}</span>
          </div>
          <div className="chat-actions">
            <button onClick={exportConversation} className="btn btn-secondary" disabled={messages.length === 0}><Download size={16} />Export</button>
            <button onClick={clearConversation} className="btn btn-secondary" disabled={messages.length === 0}><Trash2 size={16} />Clear</button>
            <button onClick={logout} className="btn btn-secondary"><LogOut size={16} />Log out</button>
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
