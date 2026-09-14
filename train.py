from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parent

# Keep the model labels aligned with the categories available in the app UI.
# The larger downloaded dataset has more detailed labels, so related labels are
# folded into the app's broader categories before training.
CATEGORY_MAP = {
    "food": "Food",
    "grocery": "Food",
    "transport": "Transport",
    "travel": "Transport",
    "online shopping": "Shopping",
    "electronics": "Shopping",
    "clothing": "Shopping",
    "bills": "Bills",
    "entertainment": "Entertainment",
    "healthcare": "Health",
    "health": "Health",
    "education": "Education",
    "other": "Other",
}


def load_examples(path: Path) -> pd.DataFrame:
    """Load either the original CSV or the downloaded finance dataset."""
    source = pd.read_csv(path)
    columns = {column.lower(): column for column in source.columns}
    if "description" not in columns or "category" not in columns:
        raise ValueError(f"{path.name} must contain Description and Category columns")

    examples = source[[columns["description"], columns["category"]]].copy()
    examples.columns = ["description", "category"]
    examples["description"] = (
        examples["description"].fillna("").astype(str).str.lower().str.strip()
        .str.replace(r"^transaction at\\s+", "", regex=True)
    )
    examples["category"] = examples["category"].fillna("Other").astype(str).str.lower().str.strip()
    examples["category"] = examples["category"].map(CATEGORY_MAP).fillna("Other")
    return examples[examples["description"] != ""]


datasets = [ROOT / "transactions.csv"]
downloaded_dataset = ROOT.parent / "personal_finance_dataset_8000_extended.csv"
if downloaded_dataset.exists():
    datasets.append(downloaded_dataset)
    print(f"Using downloaded dataset: {downloaded_dataset.name}")
else:
    print("Downloaded dataset not found; training with the built-in examples only.")

df = pd.concat([load_examples(path) for path in datasets], ignore_index=True)
print("Training examples by category:")
print(df["category"].value_counts().sort_index().to_string())

X_train, X_test, y_train, y_test = train_test_split(
    df["description"], df["category"], test_size=0.2, random_state=42, stratify=df["category"]
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
    ("clf", LogisticRegression(max_iter=2000))
])
model.fit(X_train, y_train)

pred = model.predict(X_test)
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, zero_division=0))

joblib.dump(model, ROOT / "model.joblib")
print("Saved:", ROOT / "model.joblib")
