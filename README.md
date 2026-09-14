# AI Finance Assistant

A fresher-friendly personal finance web application based on the supplied SRS. It provides authentication, transaction CRUD, ML-based expense categorization, budgets, analytics, spending forecasting, financial insights, and a finance-app chatbot.

> Educational/portfolio project only. It does not provide professional investment, tax, or financial advice.

## Tech stack

- Frontend: React + Vite + JavaScript + Recharts
- Backend: Python + FastAPI + SQLAlchemy
- Database: SQLite by default (easy local setup; can be changed later)
- Authentication: JWT + bcrypt password hashing
- ML: scikit-learn + TF-IDF + Logistic Regression
- Data: pandas + NumPy
- Charts: Recharts
- API docs: FastAPI Swagger UI

## Project structure

```text
ai-finance-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   ├── insights.py
│   │   ├── forecasting.py
│   │   └── ml_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   └── .env.example
├── ml/
│   ├── train.py
│   └── transactions.csv
├── scripts/
│   └── git_commit_each_file.py
└── README.md
```

## 1. Backend setup

Python 3.10+ is recommended.

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
copy .env.example .env
```

or on macOS/Linux:

```bash
cp .env.example .env
```

Start API:

```bash
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

Swagger docs: `http://localhost:8000/docs`

## 2. Train/retrain the classifier

The repository includes a small educational dataset. From the project root:

```bash
cd ml
python train.py
```

This creates `ml/model.joblib`.

The backend automatically loads that model when available. If it is absent, the backend falls back to a small built-in classifier so the application can still start.

## 3. Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend normally runs at `http://localhost:5173`.

Open **http://localhost:5173**, not the backend API URL (`http://localhost:8000`), while developing. The frontend and API run as separate servers in development.

If your API is elsewhere, create `.env`:

```env
VITE_API_URL=http://localhost:8000
```

### Run with one server (optional)

Build the frontend, then start the backend. The backend will serve the built application at `http://localhost:8000`:

```bash
cd frontend
npm run build
cd ../backend
.venv\Scripts\python -m uvicorn app.main:app --reload
```

## 4. Demo account

You can register from the UI. For a quick demo, use:

- Email: `demo@example.com`
- Password: `Demo@12345`

The app does not ship with a seeded password; register the account yourself.

## 5. Git history script

The requested script initializes Git and creates one commit per project file.

From the project root:

```bash
python scripts/git_commit_each_file.py
```

It will:

1. run `git init` if needed,
2. configure no identity automatically,
3. add files one at a time,
4. create a separate commit for each file,
5. skip `.git` and common generated directories/files.

Before running it, set your Git identity if Git asks:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

To connect GitHub later:

```bash
git remote add origin YOUR_REPOSITORY_URL
git branch -M main
git push -u origin main
```

## Features implemented

- Registration/login/logout
- JWT authentication
- Protected user-specific data
- Add/edit/delete transactions
- Automatic expense category prediction
- User correction of predicted category
- Monthly dashboard
- Category spending chart
- Monthly spending trend
- Budget creation and tracking
- Budget warning when usage is high
- Basic spending forecast using historical monthly totals
- Rule-based educational financial insights
- Search/filter transactions
- Finance application chatbot
- Responsive dashboard UI
- API validation and error handling

## SRS alignment

The implementation follows the supplied SRS modules: authentication, transactions, ML classification, budgets, analytics, prediction, insights, chatbot, and the optional admin area is intentionally not implemented in this first portfolio version.

The SRS specifies an API flow of UI → backend → validation/database → ML/analytics → insights → dashboard, and this project follows that architecture.

## Important security note

This is a portfolio/demo implementation. For production, use HTTPS, stronger secret management, secure cookie/token strategies, rate limiting, database migrations, monitoring, and a production database.
