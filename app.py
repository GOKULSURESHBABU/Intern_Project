import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from datetime import datetime

# Load your custom environment variables file
load_dotenv("exp.env")

# Import layout utilities and core logic safely
from auth import register_user, authenticate_user, render_google_login
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


def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def show_welcome(user_info: dict):
    st.title(f"Welcome, {user_info['name']}!")
    st.markdown("Use the sidebar to manage expenses, review budgets, compare months, and track predictions.")


def authentication_board():
    st.subheader("Expense Tracker Authentication")
    
    # Your Login/Register tabs structural framework
    auth_tab, register_tab = st.tabs(["Login", "Register"])

    with auth_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In"):
            success, result, payload = authenticate_user(email, password)
            if success:
                st.session_state["token"] = result
                st.session_state["user"] = payload
                rerun_app()
            else:
                st.error(result)

        st.write("---")
        # UPDATED BORING CAPTION HERE
        st.write("✨ Speed through securely with single sign-on:")
        
        # YOUR GOOGLE SIGN-IN WIDGET MOVED HERE AS REQUESTED
        try:
            google_user = render_google_login()
            if google_user:
                st.session_state["user"] = google_user
                st.session_state["token"] = "google_oauth_authenticated"
                rerun_app()
        except Exception:
            pass

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

    # --- FEATURE 1: BUDGET PROGRESS BAR AND TRACKER ---
    st.write("---")
    st.subheader("📊 Budget Utilization Tracker")
    
    total_spent = summary["total"]
    monthly_budget = summary["budget"]
    
    if monthly_budget > 0:
        percentage_used = min(total_spent / monthly_budget, 1.0)
        
        col_bar, col_metric = st.columns([3, 1])
        with col_bar:
            if total_spent >= monthly_budget:
                st.error(f"🚨 Budget Exceeded! You are over by {format_currency(total_spent - monthly_budget)}")
                st.progress(percentage_used)
            elif percentage_used >= 0.80:
                st.warning(f"⚠️ High Spending Warning: You've used {int(percentage_used * 100)}% of your allowance.")
                st.progress(percentage_used)
            else:
                st.success(f"✅ Safe Zone: You've used {int(percentage_used * 100)}% of your monthly budget.")
                st.progress(percentage_used)
                
        with col_metric:
            remaining_funds = max(0.0, monthly_budget - total_spent)
            st.metric(
                label="Funds Remaining", 
                value=format_currency(remaining_funds),
                delta=f"{int((1 - percentage_used) * 100)}% Left",
                delta_color="normal" if total_spent < monthly_budget else "inverse"
            )
    else:
        st.info("Set a budget limit while adding expenses to see your utilization bar tracker.")

    st.write("---")
    status_color = get_status_color(summary["total"], summary["budget"])
    message = get_budget_message(summary["total"], summary["budget"])
    st.markdown(f"<div style='padding:12px;background-color:{status_color};color:#ffffff;border-radius:10px'>{message}</div>", unsafe_allow_html=True)

    st.write("---")
    
    # --- INTERACTIVE CHARTS ANALYSIS AREA ---
    history = get_monthly_history(user_info["email"])
    if not history.empty:
        # Spending Trend Line Chart
        fig = px.line(history, x="month", y="total", title="Monthly Spending Trend", markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        st.subheader("📦 Spending Breakdown Analysis")
        
        # Create side-by-side columns for the charts
        chart_col1, chart_col2 = st.columns(2)
        
        categories = list(category_breakdown.keys())
        amounts = list(category_breakdown.values())
        
        with chart_col1:
            # Interactive Bar Chart
            fig_bar = px.bar(
                x=categories, 
                y=amounts, 
                labels={'x': 'Category', 'y': 'Total Spent'},
                title="Expenses by Category (Bar View)",
                template="plotly_dark"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with chart_col2:
            # PIE / DONUT CHART
            fig_pie = px.pie(
                names=categories,
                values=amounts,
                title="Overall Expense Distribution (Pie View)",
                hole=0.4,
                template="plotly_dark"
            )
            fig_pie.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # --- SMART FINANCIAL INSIGHTS ADVISOR ---
        if any(amounts):
            st.write("---")
            st.subheader("💡 Smart Financial Insights")
            
            highest_cat = max(category_breakdown, key=category_breakdown.get)
            highest_amt = category_breakdown[highest_cat]
            
            if total_spent > 0 and (highest_amt / total_spent) > 0.40:
                st.info(
                    f"🧐 **High Concentration Alert:** You spent a massive **{int((highest_amt/total_spent)*100)}%** "
                    f"of your total cash outlays completely on **{highest_cat}** this month. "
                    f"Look into ways to trim back on discretionary elements in this category."
                )
                
            if predicted > monthly_budget and monthly_budget > 0:
                st.warning(
                    f"📉 **Velocity Risk:** The trend prediction system estimates that your upcoming next month's spending "
                    f"(**{format_currency(predicted)}**) might cross your custom baseline safety limit "
                    f"(**{format_currency(monthly_budget)}**). Try throttling early non-essential outlays."
                )
            elif total_spent > 0:
                st.success("🎯 **Excellent Management:** Your current spending velocities put your trajectory well within safe boundaries.")
    else:
        st.info("Add your first expense to activate charts and insights.")


def add_expense_page(user_info: dict):
    st.subheader("Add Expense")
    
    # --- AUTO-CATEGORIZATION ENGINE ---
    description = st.text_input("Description (e.g., 'Swiggy dinner', 'Uber ride', 'Electricity bill')")
    
    category_guess = "Other"
    desc_lower = description.lower()
    
    # Keyword taxonomy patterns
    mapping = {
        "Food": ["swiggy", "zomato", "restaurant", "dinner", "food", "grocery", "cafe", "eat"],
        "Transport": ["uber", "ola", "auto", "petrol", "fuel", "flight", "train", "cab", "bike"],
        "Entertainment": ["netflix", "spotify", "movie", "game", "hotstar", "pub", "concert"],
        "Bills": ["electricity", "rent", "recharge", "wifi", "bill", "eb", "water"],
        "Health": ["pharmacy", "doctor", "hospital", "medicine", "gym", "health"]
    }
    
    for category_key, keywords in mapping.items():
        if any(keyword in desc_lower for keyword in keywords):
            category_guess = category_key
            break

    with st.form(key="expense_form"):
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        
        cat_options = ["Food", "Transport", "Entertainment", "Bills", "Health", "Other"]
        default_index = cat_options.index(category_guess)
        
        category = st.selectbox("Category", cat_options, index=default_index)
        date = st.date_input("Date")
        budget = st.number_input("Monthly budget", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Save Expense")
        if submitted:
            add_expense(user_info["email"], amount, category, description, date.isoformat(), budget)
            st.success("Expense added successfully. Refresh dashboard to view updates.")


def history_page(user_info: dict):
    st.subheader("Expense History")
    raw_data = get_user_expenses(user_info["email"])
    df = pd.DataFrame(raw_data)
    
    if df.empty:
        st.info("No expenses recorded yet.")
        return
        
    df["date"] = pd.to_datetime(df["date"]).dt.date
    
    # --- SMART HISTORY FILTERS ---
    with st.expander("🔍 Filter Transactions", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cat_list = ["All"] + list(df["category"].unique())
            selected_cat = st.selectbox("Filter by Category", cat_list)
        with col2:
            min_date = df["date"].min()
            max_date = df["date"].max()
            if min_date == max_date:
                date_range = [min_date, max_date]
                st.caption(f"Activity recorded on date: {min_date}")
            else:
                date_range = st.date_input("Filter by Date Range", [min_date, max_date])

    # Dynamic Filter Executions
    filtered_df = df.copy()
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]
        
    if isinstance(date_range, list) or isinstance(date_range, tuple):
        if len(date_range) == 2:
            filtered_df = filtered_df[(filtered_df["date"] >= date_range[0]) & (filtered_df["date"] <= date_range[1])]

    # Display dataset
    st.dataframe(filtered_df.sort_values(by="date", ascending=False), use_container_width=True)
    st.metric("Total for Filtered Selection", format_currency(filtered_df["amount"].sum()))


def main():
    st.sidebar.title("Expense Tracker Menu")
    
    # Check current state gatekeeper verification
    is_authenticated = False
    payload = None

    if "token" in st.session_state and st.session_state["token"]:
        if st.session_state["token"] == "google_oauth_authenticated":
            payload = st.session_state.get("user")
            is_authenticated = True if payload else False
        else:
            payload = decode_jwt(st.session_state["token"])
            is_authenticated = True if payload else False

    # Route logic separation gate
    if not is_authenticated:
        authentication_board()
        return

    # --- ANALYSIS DASHBOARD PAGES PANEL AREA ---
    page = st.sidebar.radio("Navigation", ["Dashboard", "Add Expense", "History"])
    
    # --- FEATURE: EXPORT TO CSV SIDEBAR BUTTON ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Data Tools")
    
    try:
        raw_expenses = get_user_expenses(payload["email"])
        if raw_expenses:
            export_df = pd.DataFrame(raw_expenses)
            export_df["date"] = pd.to_datetime(export_df["date"]).dt.date
            csv_data = export_df.to_csv(index=False).encode('utf-8')
            
            st.sidebar.download_button(
                label="Download Report (CSV)",
                data=csv_data,
                file_name=f"expenses_{datetime.now().strftime('%Y_%m_%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.sidebar.caption("No data entries to export yet.")
    except Exception:
        pass

    # Handy Log out Utility Option
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state["token"] = None
        st.session_state["user"] = None
        rerun_app()

    show_welcome(payload)

    if page == "Dashboard":
        dashboard_page(payload)
    elif page == "Add Expense":
        add_expense_page(payload)
    elif page == "History":
        history_page(payload)


if __name__ == "__main__":
    main() 