import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==============================
# File to store expenses
# ==============================
DATA_FILE = "expenses.csv"

# ==============================
# Load data or initialize
# ==============================
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

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

# ==============================
# Main Dashboard
# ==============================
st.title("Expense Tracker Dashboard")

# Convert Date column to datetime
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
monthly_df = df[df["Date"].dt.strftime("%Y-%m") == current_month]

# ==============================
# Total Spend
# ==============================
total_spend = monthly_df["Amount"].sum()
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

# ==============================
# View All Expenses
# ==============================
st.subheader("All Expenses")

df_reset = df.reset_index()  # keep index for delete
st.dataframe(df_reset)

# ==============================
# Delete Expense Section
# ==============================
st.subheader("Delete Expense")

if not df_reset.empty:
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
