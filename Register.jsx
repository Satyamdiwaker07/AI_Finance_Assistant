import React, { useState } from "react";
import { Link } from "react-router-dom";
import { api, request } from "../api";
import { AuthShell } from "./Login";

export default function Register({ onAuth }) {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault(); setError(""); setBusy(true);
    try { onAuth(await request(api.post("/register", form))); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  return (
    <AuthShell title="Create your account" subtitle="Start tracking your finances in a few seconds.">
      <form onSubmit={submit} className="auth-form">
        {error && <div className="error">{error}</div>}
        <label>Name<input required minLength="2" value={form.name} onChange={e => setForm({...form, name:e.target.value})} /></label>
        <label>Email<input type="email" required value={form.email} onChange={e => setForm({...form, email:e.target.value})} /></label>
        <label>Password<input type="password" required minLength="8" value={form.password} onChange={e => setForm({...form, password:e.target.value})} /></label>
        <button className="primary-btn" disabled={busy}>{busy ? "Creating…" : "Create account"}</button>
        <p>Already have an account? <Link to="/login">Sign in</Link></p>
      </form>
    </AuthShell>
  );
}
