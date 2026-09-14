from collections import defaultdict
from datetime import date
import numpy as np

def monthly_forecast(transactions):
    monthly = defaultdict(float)
    for tx in transactions:
        if tx.type == "expense":
            monthly[tx.date.strftime("%Y-%m")] += tx.amount

    ordered = sorted(monthly.items())
    if len(ordered) < 2:
        return {"available": False, "message": "Not enough historical expense data for a forecast.", "estimate": None}

    values = np.array([v for _, v in ordered], dtype=float)
    x = np.arange(1, len(values) + 1, dtype=float)
    if len(values) == 2:
        estimate = float(values[-1])
    else:
        slope, intercept = np.polyfit(x, values, 1)
        estimate = max(0.0, float(slope * (len(values) + 1) + intercept))

    return {
        "available": True,
        "estimate": round(estimate, 2),
        "based_on_months": len(values),
        "message": "Estimate based on historical monthly expense totals; it is not a guarantee."
    }
