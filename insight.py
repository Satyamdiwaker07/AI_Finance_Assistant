from collections import defaultdict
from datetime import date

def generate_insights(transactions, budgets):
    expenses = [t for t in transactions if t.type == "expense"]
    if not expenses:
        return ["Add some expense transactions to receive personalized spending insights."]

    by_category = defaultdict(float)
    by_month = defaultdict(float)
    for tx in expenses:
        by_category[tx.category] += tx.amount
        by_month[tx.date.strftime("%Y-%m")] += tx.amount

    insights = []
    top_category, top_amount = max(by_category.items(), key=lambda x: x[1])
    total = sum(by_category.values())
    share = top_amount / total * 100 if total else 0
    insights.append(f"{top_category} is your highest-spending category at ₹{top_amount:,.0f}, about {share:.0f}% of recorded expenses.")

    current_month = date.today().strftime("%Y-%m")
    current_spend = by_month.get(current_month, 0)
    for budget in budgets:
        if budget.month == current_month and budget.category == "Overall":
            usage = current_spend / budget.limit_amount * 100
            if usage >= 100:
                insights.append(f"Your overall budget is exceeded by ₹{current_spend - budget.limit_amount:,.0f}.")
            elif usage >= 80:
                insights.append(f"You have used {usage:.0f}% of your overall monthly budget. Consider reviewing discretionary spending.")

    # Category budgets are evaluated independently, so users are warned before
    # either a category limit or the overall limit is exceeded.
    for budget in budgets:
        if budget.month != current_month or budget.category == "Overall":
            continue
        spent = by_category.get(budget.category, 0)
        usage = spent / budget.limit_amount * 100 if budget.limit_amount else 0
        if usage >= 100:
            insights.append(f"Your {budget.category} budget is exceeded by {spent - budget.limit_amount:,.0f}.")
        elif usage >= 80:
            insights.append(f"You have used {usage:.0f}% of your {budget.category} budget. Consider reviewing this spending.")

    if len(by_month) >= 2:
        months = sorted(by_month)
        if by_month[months[-1]] > by_month[months[-2]] * 1.15:
            insights.append("Your latest recorded month's expenses increased noticeably compared with the previous month.")

    insights.append("These insights are educational observations from your recorded data, not professional financial advice.")
    return insights[:5]
