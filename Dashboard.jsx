import React, { useEffect, useState } from "react";
import { IndianRupee, ArrowDownLeft, ArrowUpRight, Wallet } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import { api, request } from "../api";
import StatCard from "../components/StatCard";

const money = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    try { setData(await request(api.get("/dashboard"))); }
    catch (e) { setError(e.message); }
  }
  useEffect(() => { load(); }, []);

  if (error) return <div className="error page-error">{error}</div>;
  if (!data) return <div className="center-screen">Loading dashboard…</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div><span className="eyebrow">OVERVIEW</span><h1>Your financial picture</h1><p>Simple analytics from your recorded transactions.</p></div>
        <div className="date-pill">{new Date().toLocaleDateString("en-IN", { day:"2-digit", month:"short", year:"numeric" })}</div>
      </header>

      <section className="stats-grid">
        <StatCard title="Total balance" value={money(data.balance)} hint="Income minus expenses" icon={<Wallet />} />
        <StatCard title="Total income" value={money(data.total_income)} hint="All recorded income" icon={<ArrowUpRight />} />
        <StatCard title="Total expenses" value={money(data.total_expenses)} hint="All recorded expenses" icon={<ArrowDownLeft />} />
        <StatCard title="Forecast" value={data.forecast.available ? money(data.forecast.estimate) : "—"} hint={data.forecast.message} icon={<IndianRupee />} />
      </section>

      <section className="dashboard-grid">
        <div className="card chart-card">
          <div className="card-heading"><div><h3>Spending trend</h3><p>Monthly income vs expenses</p></div></div>
          <div className="chart"><ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.monthly_trend}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(v) => money(v)} />
              <Bar dataKey="income" name="Income" radius={[5,5,0,0]} />
              <Bar dataKey="expense" name="Expenses" radius={[5,5,0,0]} />
            </BarChart>
          </ResponsiveContainer></div>
        </div>

        <div className="card chart-card">
          <div className="card-heading"><div><h3>Where you spend</h3><p>Expense categories</p></div></div>
          {data.category_spending.length ? <div className="chart"><ResponsiveContainer width="100%" height={300}>
            <PieChart><Pie data={data.category_spending} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={90} label>
              {data.category_spending.map((_, i) => <Cell key={i} />)}
            </Pie><Tooltip formatter={(v) => money(v)} /><Legend /></PieChart>
          </ResponsiveContainer></div> : <Empty text="No expenses recorded yet." />}
        </div>
      </section>

      <section className="card insights-card">
        <div className="card-heading"><div><h3>AI-assisted insights</h3><p>Educational observations based on your data</p></div></div>
        <div className="insight-list">{data.insights.map((x, i) => <div className="insight" key={i}><span>✦</span>{x}</div>)}</div>
      </section>
    </div>
  );
}

function Empty({ text }) { return <div className="empty">{text}</div>; }
