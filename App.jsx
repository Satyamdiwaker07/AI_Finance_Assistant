import React, { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { request, api } from "./api";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Budgets from "./pages/Budgets";

function PrivateRoute({ user, children }) {
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("finance_token")) {
      setLoading(false);
      return;
    }
    request(api.get("/me"))
      .then(setUser)
      .catch(() => localStorage.removeItem("finance_token"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="center-screen">Loading Finance Assistant…</div>;

  const onAuth = (data) => {
    localStorage.setItem("finance_token", data.access_token);
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem("finance_token");
    setUser(null);
  };

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login onAuth={onAuth} />} />
      <Route path="/register" element={user ? <Navigate to="/" replace /> : <Register onAuth={onAuth} />} />
      <Route
        path="/*"
        element={
          <PrivateRoute user={user}>
            <Layout user={user} onLogout={logout}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/transactions" element={<Transactions />} />
                <Route path="/budgets" element={<Budgets />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
