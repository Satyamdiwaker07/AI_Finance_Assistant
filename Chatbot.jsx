import React, { useState } from "react";
import { Bot, Send, X } from "lucide-react";
import { api, request } from "../api";

export default function Chatbot() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Ask me about budgets, transactions, categorization or forecasts." }
  ]);
  const [busy, setBusy] = useState(false);

  async function send(e) {
    e?.preventDefault();
    if (!message.trim() || busy) return;
    const text = message.trim();
    setMessage("");
    setMessages((m) => [...m, { role: "user", text }]);
    setBusy(true);
    try {
      const data = await request(api.post("/chat", { message: text }));
      setMessages((m) => [...m, { role: "bot", text: data.answer }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "bot", text: err.message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button className="chat-fab" onClick={() => setOpen(!open)} aria-label="Open chatbot">
        {open ? <X /> : <Bot />}
      </button>
      {open && (
        <section className="chat-window">
          <header><div><strong>FinAI Assistant</strong><span>App help</span></div><Bot size={20} /></header>
          <div className="chat-messages">
            {messages.map((m, i) => <div key={i} className={`bubble ${m.role}`}>{m.text}</div>)}
            {busy && <div className="bubble bot">Thinking…</div>}
          </div>
          <form onSubmit={send} className="chat-input">
            <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask something…" />
            <button type="submit"><Send size={16} /></button>
          </form>
        </section>
      )}
    </>
  );
}
