from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "ml" / "model.joblib"

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]

# A short, explicit rule set handles clear transaction descriptions more
# reliably than a statistical model trained on generic data.  The ML model is
# still used for descriptions that do not match one of these terms.
CATEGORY_KEYWORDS = {
    "Food": ("swiggy", "zomato", "restaurant", "cafe", "coffee", "pizza", "biryani", "lunch", "dinner", "breakfast", "grocery", "bigbasket", "blinkit", "zepto"),
    "Transport": ("uber", "ola", "rapido", "metro", "bus", "cab", "taxi", "irctc", "train", "flight", "fuel", "petrol", "diesel", "parking"),
    "Shopping": ("amazon", "flipkart", "myntra", "meesho", "clothes", "clothing", "shoes", "electronics", "store"),
    "Bills": ("electricity", "water bill", "internet", "wifi", "broadband", "mobile recharge", "airtel", "jio", "rent", "property tax", "insurance"),
    "Entertainment": ("movie", "cinema", "ticket", "netflix", "prime video", "hotstar", "spotify", "concert", "game", "gaming"),
    "Health": ("doctor", "medicine", "pharmacy", "hospital", "clinic", "apollo", "healthcare"),
    "Education": ("college", "school", "course", "tuition", "exam", "book", "udemy", "coursera"),
}

FALLBACK_DATA = [
    ("swiggy dinner pizza food restaurant", "Food"),
    ("zomato lunch cafe coffee", "Food"),
    ("uber ola cab metro bus ride", "Transport"),
    ("amazon clothes shoes shopping", "Shopping"),
    ("electricity water internet bill", "Bills"),
    ("netflix movie concert game", "Entertainment"),
    ("doctor medicine pharmacy hospital", "Health"),
    ("college course book tuition", "Education"),
    ("miscellaneous payment", "Other"),
]

_model = None

def _load():
    global _model
    if _model is not None:
        return _model
    if MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
        return _model
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    texts, labels = zip(*FALLBACK_DATA)
    _model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    _model.fit(texts, labels)
    return _model

def predict_category(description: str):
    normalized_description = description.lower().strip()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_description for keyword in keywords):
            return category, 0.99

    model = _load()
    category = str(model.predict([normalized_description])[0])
    confidence = 0.75
    if hasattr(model, "predict_proba"):
        confidence = float(max(model.predict_proba([description])[0]))
    return category, round(confidence, 4)
