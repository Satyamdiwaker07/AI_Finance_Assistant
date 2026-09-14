from collections import defaultdict
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import create_access_token, hash_password, verify_password
from .database import Base, engine, get_db
from .dependencies import get_current_user
from .forecasting import monthly_forecast
from .insights import generate_insights
from .ml_service import predict_category
from .models import Budget, Insight, Prediction, Transaction, User
from .schemas import (
    BudgetCreate, BudgetOut, ChatRequest, LoginRequest, Token,
    TransactionCreate, TransactionOut, UserCreate, UserOut
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Finance Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SPAStaticFiles(StaticFiles):
    """Serve React's index page for client-side routes such as /login."""

    async def get_response(self, path, scope):
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as error:
            if error.status_code != 404 or "." in Path(path).name:
                raise
            return await super().get_response("index.html", scope)

        if response.status_code == 404 and "." not in Path(path).name:
            return await super().get_response("index.html", scope)
        return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email is already registered")
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token(user.id), "user": user}

@app.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_access_token(user.id), "user": user}

@app.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

def tx_out(tx):
    return {
        "id": tx.id, "date": tx.date, "description": tx.description,
        "amount": tx.amount, "type": tx.type, "category": tx.category,
        "predicted_category": tx.prediction.predicted_category if tx.prediction else None,
        "confidence": tx.prediction.confidence if tx.prediction else None,
    }

@app.post("/transactions", response_model=TransactionOut)
def add_transaction(payload: TransactionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.type == "expense" and not payload.category:
        category, confidence = predict_category(payload.description)
    else:
        category = payload.category or "Other"
        confidence = None

    tx = Transaction(
        user_id=user.id, date=payload.date, description=payload.description.strip(),
        amount=payload.amount, type=payload.type, category=category
    )
    db.add(tx)
    db.flush()

    if payload.type == "expense":
        predicted, conf = predict_category(payload.description)
        db.add(Prediction(transaction_id=tx.id, predicted_category=predicted, confidence=conf))

    db.commit()
    db.refresh(tx)
    return tx_out(tx)

@app.get("/transactions", response_model=list[TransactionOut])
def get_transactions(
    search: str = Query("", max_length=100),
    tx_type: str = Query("", alias="type"),
    category: str = Query(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Transaction).filter(Transaction.user_id == user.id)
    if search:
        q = q.filter(Transaction.description.ilike(f"%{search}%"))
    if tx_type in ("income", "expense"):
        q = q.filter(Transaction.type == tx_type)
    if category:
        q = q.filter(Transaction.category == category)
    return [tx_out(t) for t in q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()]

@app.put("/transactions/{tx_id}", response_model=TransactionOut)
def update_transaction(tx_id: int, payload: TransactionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")

    tx.date, tx.description, tx.amount, tx.type = payload.date, payload.description.strip(), payload.amount, payload.type
    if payload.type == "expense" and not payload.category:
        tx.category, confidence = predict_category(payload.description)
    else:
        tx.category = payload.category or "Other"

    if tx.prediction:
        db.delete(tx.prediction)
        # A transaction has only one prediction. Flush the deletion before
        # inserting the replacement so SQLite's unique constraint is honored.
        db.flush()
    if payload.type == "expense":
        predicted, conf = predict_category(payload.description)
        db.add(Prediction(transaction_id=tx.id, predicted_category=predicted, confidence=conf))
    db.commit()
    db.refresh(tx)
    return tx_out(tx)

@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    db.delete(tx)
    db.commit()
    return {"message": "Transaction deleted"}

@app.post("/predict-category")
def predict(payload: dict, user: User = Depends(get_current_user)):
    description = str(payload.get("description", "")).strip()
    if not description:
        raise HTTPException(400, "Description is required")
    category, confidence = predict_category(description)
    return {"predicted_category": category, "confidence": confidence}

def budget_out(budget, spent):
    usage = (spent / budget.limit_amount * 100) if budget.limit_amount else 0
    return {
        "id": budget.id, "month": budget.month, "category": budget.category,
        "limit_amount": budget.limit_amount, "spent": round(spent, 2),
        "usage_percent": round(usage, 2)
    }

@app.post("/budgets", response_model=BudgetOut)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(Budget).filter(
        Budget.user_id == user.id, Budget.month == payload.month, Budget.category == payload.category
    ).first()
    if existing:
        existing.limit_amount = payload.limit_amount
        budget = existing
    else:
        budget = Budget(user_id=user.id, month=payload.month, category=payload.category, limit_amount=payload.limit_amount)
        db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget_out(budget, _budget_spent(db, user.id, budget.month, budget.category))

def _budget_spent(db, user_id, month, category):
    q = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense",
        func.strftime("%Y-%m", Transaction.date) == month
    )
    if category != "Overall":
        q = q.filter(Transaction.category == category)
    return float(q.scalar() or 0)

@app.get("/budgets", response_model=list[BudgetOut])
def get_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budgets = db.query(Budget).filter(Budget.user_id == user.id).order_by(Budget.month.desc()).all()
    return [budget_out(b, _budget_spent(db, user.id, b.month, b.category)) for b in budgets]

@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not budget:
        raise HTTPException(404, "Budget not found")
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted"}

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    txs = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    income = sum(t.amount for t in txs if t.type == "income")
    expense = sum(t.amount for t in txs if t.type == "expense")

    categories = defaultdict(float)
    months = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in txs:
        month = t.date.strftime("%Y-%m")
        months[month][t.type] += t.amount
        if t.type == "expense":
            categories[t.category] += t.amount

    trend = [{"month": m, **months[m]} for m in sorted(months)[-6:]]
    category_data = [{"category": k, "amount": round(v, 2)} for k, v in sorted(categories.items(), key=lambda x: -x[1])]
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    insights = generate_insights(txs, budgets)

    return {
        "total_income": round(income, 2),
        "total_expenses": round(expense, 2),
        "balance": round(income - expense, 2),
        "category_spending": category_data,
        "monthly_trend": trend,
        "forecast": monthly_forecast(txs),
        "insights": insights,
    }

@app.get("/insights")
def insights(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    txs = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    return {"insights": generate_insights(txs, budgets)}

@app.post("/chat")
def chat(payload: ChatRequest, user: User = Depends(get_current_user)):
    # This is an in-app help assistant, so give direct task instructions instead
    # of trying to answer general finance questions.
    msg = payload.message.lower().strip()
    if any(word in msg for word in ("income", "salary", "earnings", "earn", "paycheck")):
        answer = (
            "To add income, open Transactions and select Add transaction. "
            "Choose Income in the Type field, enter the date, description (for example, Salary), "
            "amount and an optional category, then select Save transaction. Income increases your total balance."
        )
    elif any(word in msg for word in ("add expense", "record expense", "new expense", "expense")):
        answer = (
            "To add an expense, open Transactions and select Add transaction. Keep Type as Expense, "
            "enter its date, description and amount. Leave Category as Auto predict to let the ML model choose one, "
            "or select a category yourself, then save."
        )
    elif any(word in msg for word in ("categor", "auto predict", "ml", "prediction")):
        answer = (
            "Automatic categorization is available for expenses. Add a clear description such as 'Swiggy dinner' "
            "and leave Category as Auto predict. The ML model suggests a category; you can select a different one "
            "before saving or edit the transaction later."
        )
    elif any(word in msg for word in ("edit", "update", "change transaction")):
        answer = "Open Transactions, find the record, and select the pencil icon. Change its details and select Save transaction."
    elif any(word in msg for word in ("delete", "remove")):
        answer = "Open Transactions, find the record, and select the trash icon. Confirm the prompt to permanently delete it."
    elif any(word in msg for word in ("search", "filter", "find transaction")):
        answer = "On Transactions, use the search box to find a description or use the type menu to show only income or expenses."
    elif "budget" in msg or "limit" in msg:
        answer = (
            "Open Budgets and choose a month, Overall or a category, and a spending limit. "
            "Saving the same month and category updates that budget. The page shows your spending, percentage used and warnings."
        )
    elif any(word in msg for word in ("dashboard", "balance", "chart", "analytics")):
        answer = "The Dashboard shows total income, total expenses and balance, plus monthly trends, category spending, forecasts and insights from your transactions."
    elif any(word in msg for word in ("forecast", "future spending")):
        answer = "The Forecast card estimates a future monthly expense total from your recorded monthly expenses. It needs enough history and is only an estimate."
    elif any(word in msg for word in ("insight", "highest spending", "spending habit")):
        answer = "The Dashboard insights highlight patterns such as your highest-spending category, budget usage and changes in monthly expenses. Add transactions for more useful results."
    elif any(word in msg for word in ("login", "log in", "register", "sign up", "account")):
        answer = "Use the login screen to create an account or sign in. Your transactions and budgets are private to your account."
    elif any(word in msg for word in ("advice", "invest", "stock", "tax")):
        answer = "This app helps you track your own finances, but it does not provide professional investment, tax or financial advice."
    elif any(word in msg for word in ("hello", "hi", "help", "what can you do")):
        answer = (
            f"Hi {user.name}! I can explain how to add income or expenses, use ML categories, edit or filter transactions, "
            "set budgets, and understand the dashboard, forecast and insights."
        )
    else:
        answer = (
            "I can help with this finance app. Try asking: 'How do I add income?', 'How do I add an expense?', "
            "'Will ML choose a category?', 'How do I set a budget?', or 'What does the dashboard show?'"
        )
    return {"answer": answer}


# After `npm run build` in frontend/, one Uvicorn server can serve both the API
# and the React application.  API routes above take precedence over this mount.
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", SPAStaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def frontend_not_built():
        return {
            "message": "Frontend is not built. Run `npm run dev` in frontend/ and open http://localhost:5173."
        }
