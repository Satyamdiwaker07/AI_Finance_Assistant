# Architecture

```text
React UI
   |
   | HTTP + JWT
   v
FastAPI
   |
   +---- SQLAlchemy ---- SQLite
   |
   +---- ML service ---- TF-IDF + Logistic Regression
   |
   +---- Analytics ---- pandas/NumPy-style Python calculations
   |
   +---- Forecasting ---- simple linear regression over monthly expense totals
   |
   +---- Insights ---- rule-based educational explanations
   |
   +---- Chatbot ---- application-help responses
```

The SRS calls for a simple fresher implementation and explicitly allows React.js on the frontend, FastAPI/Flask on the backend, scikit-learn for ML, pandas/NumPy for data processing, a relational database, and Git/GitHub for development. This implementation chooses React + FastAPI + SQLite + scikit-learn to keep local setup straightforward.
