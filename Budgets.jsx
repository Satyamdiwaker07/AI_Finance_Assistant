import React, { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { api, request } from "../api";

const categories = ["Overall","Food","Transport","Shopping","Bills","Entertainment","Health","Education","Other"];

export default function Budgets() {
  const monthNow = new Date().toISOString().slice(0,7);
  const [budgets, setBudgets] = useState([]);
  const [form, setForm] = useState({month:monthNow,category:"Overall",limit_amount:""});
  const [error, setError] = useState("");

  async function load() {
    try { setBudgets(await request(api.get("/budgets"))); } catch(e) { setError(e.message); }
  }
  useEffect(()=>{load()},[]);

  async function submit(e) {
    e.preventDefault();
    try { await request(api.post("/budgets",{...form,limit_amount:Number(form.limit_amount)})); setForm({...form,limit_amount:""}); load(); }
    catch(e){setError(e.message)}
  }

  async function remove(id) {
    try { await request(api.delete(`/budgets/${id}`)); load(); } catch(e){setError(e.message)}
  }

  return (
    <div className="page">
      <header className="page-header"><div><span className="eyebrow">CONTROL YOUR SPEND</span><h1>Budgets</h1><p>Set monthly or category-wise limits and monitor usage.</p></div></header>
      {error && <div className="error page-error">{error}</div>}

      <section className="card budget-form">
        <div><h3>Create / update a budget</h3><p>Saving the same month + category updates the existing budget.</p></div>
        <form onSubmit={submit} className="budget-inline">
          <label>Month<input type="month" required value={form.month} onChange={e=>setForm({...form,month:e.target.value})}/></label>
          <label>Category<select value={form.category} onChange={e=>setForm({...form,category:e.target.value})}>{categories.map(c=><option key={c}>{c}</option>)}</select></label>
          <label>Limit (₹)<input type="number" min="1" step="0.01" required value={form.limit_amount} onChange={e=>setForm({...form,limit_amount:e.target.value})}/></label>
          <button className="primary-btn"><Plus size={17}/> Save budget</button>
        </form>
      </section>

      <div className="budget-grid">
        {budgets.map(b => {
          const over = b.usage_percent >= 100;
          const approaching = b.usage_percent >= 80 && !over;
          return <div className="card budget-card" key={b.id}>
            <div className="budget-top"><div><span className="muted">{b.month}</span><h3>{b.category}</h3></div><button className="icon-btn" onClick={()=>remove(b.id)}><Trash2 size={16}/></button></div>
            <div className="budget-numbers"><strong>₹{b.spent.toLocaleString("en-IN")}</strong><span>of ₹{b.limit_amount.toLocaleString("en-IN")}</span></div>
            <div className="progress"><div style={{width:`${Math.min(b.usage_percent,100)}%`}} /></div>
            {approaching && <div className="warning-text">Approaching limit: {b.usage_percent.toFixed(0)}% used.</div>}
            <div className={over ? "warning-text" : "muted"}>{over ? `Over budget by ₹${(b.spent-b.limit_amount).toLocaleString("en-IN")}` : `${b.usage_percent.toFixed(0)}% used`}</div>
          </div>
        })}
      </div>
      {!budgets.length && <div className="empty card">No budgets yet. Create your first monthly limit above.</div>}
    </div>
  );
}
