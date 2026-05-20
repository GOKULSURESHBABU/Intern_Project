import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from auth import register_user, authenticate_user
from utils import decode_jwt, format_currency
from data_manager import (
    add_expense,
    get_user_expenses,
    get_monthly_summary,
    get_monthly_history,
    compare_previous_month,
    predict_next_month,
    get_category_breakdown,
    get_status_color,
    get_budget_message,
)


st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")


@st.cache_data
def load_expenses_for_user(user_email: str) -> pd.DataFrame:
    return pd.DataFrame(get_user_expenses(user_email))


def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def show_welcome(user_info: dict):
    st.title(f"Welcome, {user_info['name']}!")
    st.markdown(
        "Use the sidebar to manage expenses, review budgets, compare months, and track predictions."
    )


def authentication_board():
    st.subheader("Expense Tracker Authentication")
    if "token" in st.session_state and st.session_state["token"]:
        payload = decode_jwt(st.session_state["token"])
        if payload:
            st.success("You are already signed in.")
            st.code(st.session_state["token"], language="text")
            if st.button("Log out"):
                st.session_state.clear()
                rerun_app()
            return

    auth_tab, register_tab = st.tabs(["Login", "Register"])

    with auth_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In"):
            success, result, payload = authenticate_user(email, password)
            if success:
                st.session_state["token"] = result
                st.session_state["user"] = payload
                st.success("Login successful.")
                rerun_app()
            else:
                st.error(result)

    with register_tab:
        name = st.text_input("Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm = st.text_input("Confirm Password", type="password", key="register_confirm")
        if st.button("Create Account"):
            if password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = register_user(name, email, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)


def dashboard_page(user_info: dict):
    st.subheader("Dashboard")
    year = datetime.now().year
    month = datetime.now().month
    summary = get_monthly_summary(user_info["email"], year, month)
    comparison = compare_previous_month(user_info["email"], year, month)
    predicted = predict_next_month(user_info["email"])
    category_breakdown = get_category_breakdown(user_info["email"])

    col1, col2, col3 = st.columns(3)
    col1.metric("This month total", format_currency(summary["total"]))
    col2.metric("Monthly budget", format_currency(summary["budget"]))
    col3.metric("Predicted next month", format_currency(predicted))

    status_color = get_status_color(summary["total"], summary["budget"])
    message = get_budget_message(summary["total"], summary["budget"])
    st.markdown(f"<div style='padding:12px;background-color:{status_color};color:#ffffff;border-radius:10px'>{message}</div>", unsafe_allow_html=True)

    history = get_monthly_history(user_info["email"])
    if not history.empty:
        fig = px.line(history, x="month", y="total", title="Monthly Spending Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(x=list(category_breakdown.keys()), y=list(category_breakdown.values()), title="Category Breakdown")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Add your first expense to activate charts and insights.")

    st.markdown("### Month Comparison")
    st.write(
        f"Current month: {format_currency(comparison['current_total'])} | Last month: {format_currency(comparison['previous_total'])} | Change: {comparison['percent_change']:.1f}%"
    )


def add_expense_page(user_info: dict):
    st.subheader("Add Expense")
    with st.form(key="expense_form"):
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Health", "Other"])
        description = st.text_input("Description")
        date = st.date_input("Date")
        budget = st.number_input("Monthly budget", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Save Expense")
        if submitted:
            add_expense(
                user_info["email"],
                amount,
                category,
                description,
                date.isoformat(),
                budget,
            )
            st.success("Expense added successfully. Refresh dashboard to view updates.")


def history_page(user_info: dict):
    st.subheader("Expense History")
    df = pd.DataFrame(get_user_expenses(user_info["email"]))
    if df.empty:
        st.info("No expenses recorded yet.")
        return
    df["date"] = pd.to_datetime(df["date"]).dt.date
    st.dataframe(df.sort_values(by="date", ascending=False))
    st.markdown("### Expense Table")
    st.write(df)


def settings_page(user_info: dict):
    st.subheader("Account and Security")
    st.write(f"**Name:** {user_info['name']}")
    st.write(f"**Email:** {user_info['email']}")
    if st.button("Show JWT Token"):
        st.code(st.session_state.get("token", ""), language="text")
    if st.button("Log out"):
        st.session_state.clear()
        rerun_app()


def main():
    st.sidebar.title("Expense Tracker Menu")
    if "token" not in st.session_state or not st.session_state.get("token"):
        authentication_board()
        return

    payload = decode_jwt(st.session_state["token"])
    if not payload:
        st.warning("Session expired or invalid. Please sign in again.")
        st.session_state.clear()
        return

    page = st.sidebar.radio("Navigation", ["Dashboard", "Add Expense", "History", "Settings", "Help"])
    show_welcome(payload)

    if page == "Dashboard":
        dashboard_page(payload)
    elif page == "Add Expense":
        add_expense_page(payload)
    elif page == "History":
        history_page(payload)
    elif page == "Settings":
        settings_page(payload)
    else:
        st.subheader("Help & Documentation")
        st.markdown(
            "Use the sidebar to navigate through your dashboard, add expenses, view historical spending, and manage your account. "
            "Enter a monthly budget in the Add Expense page to activate budget alerts and color-coded status."
        )


if __name__ == "__main__":
    main()
