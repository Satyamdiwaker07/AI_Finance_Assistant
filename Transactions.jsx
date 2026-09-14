import React, { useEffect, useState } from "react";
import { Pencil, Plus, Search, Trash2, X } from "lucide-react";
import { api, request } from "../api";

const today = new Date().toISOString().slice(0, 10);
const initial = { date: today, description: "", amount: "", type: "expense", category: "" };
const categories = ["Food","Transport","Shopping","Bills","Entertainment","Health","Education","Other"];

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [form, setForm] = useState(initial);
  const [editing, setEditing] = useState(null);
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [type, setType] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try { setTransactions(await request(api.get("/transactions", { params: { search, type } }))); }
    catch (e) { setError(e.message); }
  }
  useEffect(() => { load(); }, [search, type]);

  function openCreate() { setEditing(null); setForm(initial); setOpen(true); }
  function openEdit(tx) {
    setEditing(tx.id);
    setForm({ date: tx.date, description: tx.description, amount: tx.amount, type: tx.type, category: tx.category });
    setOpen(true);
  }

  async function submit(e) {
    e.preventDefault(); setError("");
    try {
      const payload = {...form, amount: Number(form.amount), category: form.category || null};
      if (editing) await request(api.put(`/transactions/${editing}`, payload));
      else await request(api.post("/transactions", payload));
      setOpen(false); load();
    } catch (e) { setError(e.message); }
  }

  async function remove(id) {
    if (!confirm("Delete this transaction?")) return;
    try { await request(api.delete(`/transactions/${id}`)); load(); } catch (e) { setError(e.message); }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div><span className="eyebrow">MONEY FLOW</span><h1>Transactions</h1><p>Record and review your income and expenses.</p></div>
        <button className="primary-btn" onClick={openCreate}><Plus size={17}/> Add transaction</button>
      </header>

      {error && <div className="error page-error">{error}</div>}

      <div className="toolbar card">
        <div className="search"><Search size={17}/><input placeholder="Search description…" value={search} onChange={e=>setSearch(e.target.value)} /></div>
        <select value={type} onChange={e=>setType(e.target.value)}><option value="">All types</option><option value="income">Income</option><option value="expense">Expense</option></select>
      </div>

      <div className="card table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Description</th><th>Type</th><th>Category</th><th>Amount</th><th></th></tr></thead>
          <tbody>
            {transactions.map(t => (
              <tr key={t.id}>
                <td>{t.date}</td><td><strong>{t.description}</strong></td>
                <td><span className={`badge ${t.type}`}>{t.type}</span></td>
                <td>{t.category}{t.predicted_category && <small className="prediction">ML {Math.round((t.confidence||0)*100)}%</small>}</td>
                <td className={t.type === "expense" ? "expense-text" : "income-text"}>{t.type==="expense"?"−":"+"}₹{t.amount.toLocaleString("en-IN")}</td>
                <td><div className="row-actions"><button onClick={()=>openEdit(t)}><Pencil size={15}/></button><button onClick={()=>remove(t.id)}><Trash2 size={15}/></button></div></td>
              </tr>
            ))}
          </tbody>
        </table>
        {!transactions.length && <div className="empty">No transactions match your filters.</div>}
      </div>

      {open && <div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&setOpen(false)}>
        <form className="modal card" onSubmit={submit}>
          <div className="modal-head"><div><h2>{editing ? "Edit transaction" : "Add transaction"}</h2><p>Expenses can be auto-categorized by the ML model.</p></div><button type="button" onClick={()=>setOpen(false)}><X/></button></div>
          <div className="form-grid">
            <label>Date<input type="date" required value={form.date} onChange={e=>setForm({...form,date:e.target.value})}/></label>
            <label>Type<select value={form.type} onChange={e=>setForm({...form,type:e.target.value})}><option value="expense">Expense</option><option value="income">Income</option></select></label>
            <label className="wide">Description<input required placeholder="e.g. Swiggy dinner 450" value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label>
            <label>Amount (₹)<input type="number" min="0.01" step="0.01" required value={form.amount} onChange={e=>setForm({...form,amount:e.target.value})}/></label>
            <label>Category<select value={form.category} onChange={e=>setForm({...form,category:e.target.value})}><option value="">Auto predict</option>{categories.map(c=><option key={c}>{c}</option>)}</select></label>
          </div>
          <button className="primary-btn full">Save transaction</button>
        </form>
      </div>}
    </div>
  );
}
