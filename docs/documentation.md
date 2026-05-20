# Expense Tracker Documentation

## Overview
This project is a Streamlit-based expense tracker that helps users:
- Track daily spending
- Categorize expenses by category
- Analyze monthly budgets and compare to prior months
- Predict next-month expenses using recent trends
- Receive budget alerts using color-coded status indicators
- Authenticate with JWT tokens via a login/register board
- Use SMTP to send welcome emails

## Project Structure
- `app.py` — main Streamlit application
- `auth.py` — registration and login with JWT creation
- `data_manager.py` — expense storage and analytics
- `utils.py` — helper functions for file I/O, JWT, SMTP, and formatting
- `config.py` — environment configuration for JWT and SMTP
- `storage/users.json` — persisted user accounts
- `storage/expenses.json` — persisted expense records
- `README.md` — project overview and installation instructions
- `preview.txt` — quick summary

## Features
### Authentication
- New users can register with name, email, and password
- Returning users can log in and receive a JWT
- Authenticated session is stored in Streamlit session state
- The authentication board also displays raw JWT details after login

### Expense Management
- Add expenses with amount, category, description, date, and monthly budget
- Track multiple categories such as Food, Transport, Entertainment, Bills, Health, and Other
- Store expenses in a local JSON file

### Dashboard and Analysis
- Monthly spending metric and budget comparison
- Trend chart for the last 6 months
- Category breakdown chart
- Comparison with the previous month
- Forecasted next-month expense estimate

### Budget Alerts
- Green status if spending is safely below budget
- Orange status when spending is close to the limit
- Red status when spending exceeds the budget

### SMTP Integration
- Sends a welcome email at registration if SMTP credentials are configured
- SMTP server, port, sender, and password are configured through environment variables

## How it works
1. Install dependencies from `requirements.txt`
2. Set environment variables in a `.env` file or your shell
3. Run `streamlit run app.py`
4. Register a new user and log in
5. Add expenses and view dashboards
6. Budget alerts are generated automatically based on monthly budget input

## Running the App
```bash
streamlit run app.py
```

## Configuration
Create a `.env` file or export the following values:
```env
JWT_SECRET=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER=your-email@example.com
SMTP_PASSWORD=your-email-password
```

## Notes
- Use a secure secret for `JWT_SECRET`
- If SMTP is not configured, the app still works but email sends may fail silently
- Expense data is stored locally in `storage/expenses.json`
