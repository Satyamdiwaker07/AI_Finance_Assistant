import React from "react";
import { NavLink } from "react-router-dom";
import { BarChart3, LogOut, Receipt, Target, WalletCards } from "lucide-react";
import Chatbot from "./Chatbot";

export default function Layout({ user, onLogout, children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">₹</div>
          <div>
            <strong>FinAI</strong>
            <span>Finance Assistant</span>
          </div>
        </div>

        <nav>
          <NavLink to="/" end><BarChart3 size={18} /> Dashboard</NavLink>
          <NavLink to="/transactions"><Receipt size={18} /> Transactions</NavLink>
          <NavLink to="/budgets"><Target size={18} /> Budgets</NavLink>
        </nav>

        <div className="sidebar-bottom">
          <div className="profile-mini">
            <div className="avatar">{user.name[0].toUpperCase()}</div>
            <div><strong>{user.name}</strong><span>{user.email}</span></div>
          </div>
          <button className="ghost-btn full" onClick={onLogout}><LogOut size={16} /> Logout</button>
        </div>
      </aside>

      <main className="main-content">{children}</main>
      <Chatbot />
    </div>
  );
}
