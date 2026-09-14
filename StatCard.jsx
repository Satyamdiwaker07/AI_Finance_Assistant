import React from "react";

export default function StatCard({ title, value, hint, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div>
        <span className="muted">{title}</span>
        <h2>{value}</h2>
        <small>{hint}</small>
      </div>
    </div>
  );
}
