import React, { useState } from "react";
import axios from "axios";
import { ShieldCheck } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import "./chat.css";

const api = axios.create({ withCredentials: true });

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const signup = mode === "signup";
      const response = await api.post(signup ? "/api/auth/signup" : "/api/auth/login",
        signup
          ? { name: form.name.trim(), email: form.email.trim(), password: form.password }
          : { email: form.email.trim(), password: form.password });
      if (!response.data?.user) throw new Error("Account response was incomplete.");
      navigate("/chat");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : err.message || "Could not complete account request.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat-auth-page">
      <div className="chat-auth-card">
        <div className="chat-auth-brand"><span className="chat-auth-logo">T</span><span>Tamanna AI</span></div>
        <div className="chat-auth-heading">
          <ShieldCheck size={22} />
          <h1>{mode === "signup" ? "Create your account" : "Welcome back"}</h1>
          <p>{mode === "signup" ? "Create an account when you are ready." : "Sign in to your Tamanna AI account."}</p>
        </div>
        <div className="chat-auth-tabs" role="tablist" aria-label="Account access">
          <button type="button" role="tab" aria-selected={mode === "login"} className={mode === "login" ? "active" : ""} onClick={() => { setMode("login"); setError(""); }}>Log in</button>
          <button type="button" role="tab" aria-selected={mode === "signup"} className={mode === "signup" ? "active" : ""} onClick={() => { setMode("signup"); setError(""); }}>Sign up</button>
        </div>
        <form className="chat-auth-form" onSubmit={submit}>
          {mode === "signup" && <label>Full name<input autoComplete="name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} minLength={2} maxLength={80} required placeholder="Your name" /></label>}
          <label>Email address<input type="email" autoComplete="email" autoCapitalize="none" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} maxLength={254} required placeholder="you@example.com" /></label>
          <label>Password<input type="password" autoComplete={mode === "signup" ? "new-password" : "current-password"} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} minLength={mode === "signup" ? 12 : 1} maxLength={128} required placeholder={mode === "signup" ? "At least 12 characters" : "Your password"} /></label>
          {error && <p className="chat-auth-error" role="alert">{error}</p>}
          <button className="chat-auth-submit" type="submit" disabled={busy}>{busy ? "Please wait…" : mode === "signup" ? "Create account" : "Log in"}</button>
        </form>
        <p className="chat-auth-note">Chat is available without signing in. <Link to="/chat">Return to chat</Link>.</p>
      </div>
    </section>
  );
}
