import React, { useState } from "react";
import { Link } from "react-router-dom";
import { api, request } from "../api";

export default function Login({ onAuth }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault(); setError(""); setBusy(true);
    try { onAuth(await request(api.post("/login", form))); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to your personal finance workspace.">
      <form onSubmit={submit} className="auth-form">
        {error && <div className="error">{error}</div>}
        <label>Email<input type="email" required value={form.email} onChange={e => setForm({...form, email:e.target.value})} /></label>
        <label>Password<input type="password" required value={form.password} onChange={e => setForm({...form, password:e.target.value})} /></label>
        <button className="primary-btn" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
        <p>New here? <Link to="/register">Create an account</Link></p>
      </form>
    </AuthShell>
  );
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <div className="brand"><div className="brand-mark">₹</div><strong>FinAI</strong></div>
        <h1>Understand your money.<br /><em>Build better habits.</em></h1>
        <p>Track expenses, monitor budgets and get simple AI-assisted insights from your own data.</p>
      </div>
      <div className="auth-panel"><div className="auth-card"><h1>{title}</h1><p>{subtitle}</p>{children}</div></div>
    </div>
  );
}
