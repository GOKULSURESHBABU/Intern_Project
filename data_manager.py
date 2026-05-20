from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from utils import ensure_storage, load_json_file, save_json_file, parse_date, EXPENSE_STORAGE

ensure_storage()


def add_expense(user_email: str, amount: float, category: str, description: str, date_str: str, budget: float) -> bool:
    expenses = load_json_file(EXPENSE_STORAGE)
    expense = {
        "email": user_email,
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": parse_date(date_str),
        "budget": float(budget)
    }
    expenses.append(expense)
    save_json_file(EXPENSE_STORAGE, expenses)
    return True


def get_user_expenses(email: str) -> list[dict]:
    expenses = load_json_file(EXPENSE_STORAGE)
    return [expense for expense in expenses if expense["email"] == email]


def get_dataframe(expenses: list[dict]) -> pd.DataFrame:
    if not expenses:
        return pd.DataFrame(columns=["date", "amount", "category", "description", "budget"])
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    df["budget"] = df["budget"].astype(float)
    return df


def get_monthly_summary(email: str, year: int, month: int) -> dict:
    df = get_dataframe(get_user_expenses(email))
    if df.empty:
        return {"total": 0.0, "categories": {}, "expense_count": 0, "budget": 0.0}

    month_df = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]
    total = float(month_df["amount"].sum())
    budget = float(month_df["budget"].max() if not month_df.empty else 0.0)
    categories = month_df.groupby("category")["amount"].sum().to_dict()
    return {
        "total": total,
        "categories": categories,
        "expense_count": len(month_df),
        "budget": budget
    }


def get_monthly_history(email: str, months: int = 6) -> pd.DataFrame:
    df = get_dataframe(get_user_expenses(email))
    if df.empty:
        return pd.DataFrame(columns=["month", "total"])
    
    df["month"] = df["date"].dt.to_period("M").astype(str)
    
    # FIX: Explicitly rename 'amount' to 'total' after aggregation
    history = df.groupby("month")["amount"].sum().reset_index(name="total")
    history = history.sort_values("month")
    return history.tail(months)


def compare_previous_month(email: str, year: int, month: int) -> dict:
    current = get_monthly_summary(email, year, month)
    previous_month = (datetime(year, month, 1) - timedelta(days=1)).month
    previous_year = (datetime(year, month, 1) - timedelta(days=1)).year
    previous = get_monthly_summary(email, previous_year, previous_month)
    diff = current["total"] - previous["total"]
    pct = 0.0 if previous["total"] == 0 else diff / previous["total"] * 100
    return {
        "current_total": current["total"],
        "previous_total": previous["total"],
        "difference": diff,
        "percent_change": pct
    }


def predict_next_month(email: str) -> float:
    history = get_monthly_history(email, months=6)
    if history.empty:
        return 0.0
    
    # This now functions properly because the column "total" exists
    amounts = history["total"].astype(float).tolist()
    if len(amounts) == 1:
        return float(amounts[0])

    x = list(range(len(amounts)))
    y = amounts
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    slope = numerator / denominator if denominator != 0 else 0.0
    intercept = y_mean - slope * x_mean
    trend_prediction = intercept + slope * len(amounts)

    recent_average = float(sum(amounts[-3:]) / min(len(amounts[-3:]), 3))
    last_month = amounts[-1]
    predicted = max(0.0, 0.5 * last_month + 0.3 * recent_average + 0.2 * trend_prediction)
    return float(predicted)


def get_category_breakdown(email: str) -> dict:
    df = get_dataframe(get_user_expenses(email))
    if df.empty:
        return {}
    return df.groupby("category")["amount"].sum().sort_values(ascending=False).to_dict()


def get_status_color(total: float, budget: float) -> str:
    if budget <= 0:
        return "orange"
    ratio = total / budget
    if ratio <= 0.9:
        return "green"
    if ratio <= 1.0:
        return "orange"
    return "red"


def get_budget_message(total: float, budget: float) -> str:
    color = get_status_color(total, budget)
    if budget <= 0:
        return "Set a monthly budget to activate alerts."
    if color == "green":
        return "You are safely under budget. Keep saving!"
    if color == "orange":
        return "You are close to your budget. Watch your spending."
    return "Budget exceeded. Take action to reduce costs."