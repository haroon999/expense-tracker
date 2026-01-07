import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import hashlib

# ==============================
# User Authentication Setup
# ==============================
USERS_FILE = "users.csv"

# Initialize users file if not exists
if not os.path.exists(USERS_FILE):
    users_df = pd.DataFrame(columns=["Username", "Password"])
    users_df.to_csv(USERS_FILE, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    users_df = pd.read_csv(USERS_FILE)
    user = users_df[users_df["Username"] == username]
    if not user.empty:
        return user.iloc[0]["Password"] == hash_password(password)
    return False

def register_user(username, password):
    users_df = pd.read_csv(USERS_FILE)
    if username in users_df["Username"].values:
        return False
    new_user = pd.DataFrame({
        "Username": [username],
        "Password": [hash_password(password)]
    })
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv(USERS_FILE, index=False)
    return True

# ==============================
# Session State Initialization
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# ==============================
# Login/Register Page
# ==============================
if not st.session_state.logged_in:
    st.title("Expense Tracker - Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            if verify_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Register New Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
        
        if st.button("Register"):
            if not reg_username or not reg_password:
                st.error("Please fill in all fields")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_password) < 4:
                st.error("Password must be at least 4 characters")
            elif register_user(reg_username, reg_password):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists")
    
    st.stop()

# ==============================
# Main App (After Login)
# ==============================

# User-specific data file
DATA_FILE = f"expenses_{st.session_state.username}.csv"

# Load data or initialize
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

# ==============================
# Logout Button
# ==============================
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"Expense Tracker - {st.session_state.username}")
with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# ==============================
# Sidebar: Add Expense
# ==============================
st.sidebar.header("Add Expense")

date = st.sidebar.date_input("Date", datetime.today())
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0.0, format="%.2f")
category = st.sidebar.selectbox(
    "Category",
    ["Food", "Transport", "Entertainment", "Utilities", "Rent", "Others"]
)

if st.sidebar.button("Add Expense"):
    if description and amount > 0:
        new_entry = pd.DataFrame({
            "Date": [date],
            "Description": [description],
            "Amount": [amount],
            "Category": [category]
        })

        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Expense added successfully!")
        st.rerun()
    else:
        st.sidebar.error("Please fill in all fields")

# ==============================
# Main Dashboard
# ==============================

# Convert Date column to datetime
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

# ==============================
# Budget Section
# ==============================
budget = st.number_input(
    "Set Monthly Budget",
    min_value=0.0,
    value=1000.0,
    format="%.2f"
)

# ==============================
# Filter Current Month
# ==============================
current_month = datetime.now().strftime("%Y-%m")
monthly_df = df[df["Date"].dt.strftime("%Y-%m") == current_month] if not df.empty else pd.DataFrame()

# ==============================
# Total Spend
# ==============================
total_spend = monthly_df["Amount"].sum() if not monthly_df.empty else 0
st.subheader(f"Total Spend this Month: Rs. {total_spend:.2f}")

# ==============================
# Budget Alerts
# ==============================
if total_spend > budget:
    st.error(f"Budget Exceeded by Rs. {total_spend - budget:.2f}")
elif total_spend > budget * 0.8:
    st.warning("Warning: You have used 80% of your budget.")

# ==============================
# Charts
# ==============================
if not monthly_df.empty:

    # Pie Chart
    pie_fig = px.pie(
        monthly_df,
        values="Amount",
        names="Category",
        title="Expense Breakdown (This Month)"
    )
    st.plotly_chart(pie_fig)

    # Line Chart (Cumulative)
    monthly_df = monthly_df.sort_values("Date")
    monthly_df["Cumulative"] = monthly_df["Amount"].cumsum()

    line_fig = px.line(
        monthly_df,
        x="Date",
        y="Cumulative",
        title="Spending Trend This Month"
    )
    st.plotly_chart(line_fig)
else:
    st.info("No expenses recorded for this month yet.")

# ==============================
# View All Expenses
# ==============================
st.subheader("All Expenses")

if not df.empty:
    df_reset = df.reset_index()  # keep index for delete
    st.dataframe(df_reset)
else:
    st.info("No expenses recorded yet. Add your first expense!")

# ==============================
# Delete Expense Section
# ==============================
st.subheader("Delete Expense")

if not df.empty:
    df_reset = df.reset_index()
    delete_index = st.number_input(
        "Enter the index number to delete",
        min_value=0,
        max_value=len(df_reset) - 1,
        step=1
    )

    st.write("Selected Expense:")
    st.write(df_reset.loc[delete_index])

    if st.button("Delete Expense"):
        df = df.drop(df.index[delete_index])
        df.to_csv(DATA_FILE, index=False)
        st.success("Expense deleted successfully!")
        st.rerun()
else:
    st.info("No expenses available to delete.")

# ==============================
# Monthly Trend Analysis
# ==============================
if not df.empty:
    st.subheader("Monthly Spend Trend")

    monthly_summary = (
        df.groupby(df["Date"].dt.strftime("%Y-%m"))["Amount"]
        .sum()
        .reset_index(name="Total")
    )

    bar_fig = px.bar(
        monthly_summary,
        x="Date",
        y="Total",
        title="Monthly Spend Over Time"
    )
    st.plotly_chart(bar_fig)
