# Expense Tracker

A full Streamlit expense tracker with login, JWT authentication, budget alerts, expense categorization, month comparisons, and predictive analytics.

## Features
- Track expenses by category and date
- Categorize spending automatically
- Analyze monthly budgets and compare against previous months
- Predict future expenses with simple trend forecasting
- Color-coded savings view: green for under budget, orange for near limit, red for over limit
- SMTP alerts for budget threshold warnings
- JSON Web Token (JWT) authentication board
- Interactive dashboard with charts and reports

## Installation
1. Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your SMTP and JWT secrets:

```env
JWT_SECRET=replace-with-a-strong-secret
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER=your-email@example.com
SMTP_PASSWORD=your-email-password
```

## Run the app

```bash
streamlit run app.py
```

## Default files
- `storage/users.json` — user accounts storage
- `storage/expenses.json` — saved expense records
- `docs/documentation.md` — project documentation
- `preview.txt` — quick project preview

## Notes
- Register a new user using the sign-up form or log in with the demo account below.
- After login, use the dashboard to add expenses, view charts, and compare past months.
- Budget alerts are triggered when spending reaches 90% of your monthly budget.

## Demo Account
- Email: `demo@example.com`
- Password: `Password123`
