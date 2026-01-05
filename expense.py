import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
# File to store expenses
DATA_FILE = "expenses.csv"
# Load data or initialize
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
# Sidebar for inputs
st.sidebar.header("Add Expense")
date = st.sidebar.date_input("Date", datetime.today())
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0.0, format="%.2f")
category = st.sidebar.selectbox("Category", ["Food", "Transport", "Entertainment", "Others", "Utilities", "Rent"])
if st.sidebar.button("Add Expense"):
    new_entry = pd.DataFrame({"Date": [date], "Description": [description], "Amount": [amount], "Category": [category]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.sidebar.success("Expense added!")
# Main Dashboard
st.title("Expense Tracker Dashboard")
# Set budget
budget = st.number_input("Set Monthly Budget", min_value=0.0, value=1000.0, format="%.2f")
# Filter by month
df['Date'] = pd.to_datetime(df['Date'])
current_month = datetime.now().strftime("%Y-%m")
monthly_df = df[df['Date'].dt.strftime("%Y-%m") == current_month]
# Total Spend
total_spend = monthly_df['Amount'].sum()
st.subheader(f"Total Spend this Month: ${total_spend:.2f}")
# Budget Alert
if total_spend > budget:
    st.error(f"Alert: You've exceeded your budget by ${total_spend - budget:.2f}!")
elif total_spend > budget * 0.8:
    st.warning(f"Warning: You're at 80% of your budget.")
# Summary Charts
if not monthly_df.empty:
    # Pie Chart: Category Breakdown
    pie_fig = px.pie(monthly_df, values='Amount', names='Category', title="Expense Breakdown")
    st.plotly_chart(pie_fig)
    # Line Chart: Trend Over Time (cumulative spend)
    monthly_df = monthly_df.sort_values('Date')
    monthly_df['Cumulative'] = monthly_df['Amount'].cumsum()
    line_fig = px.line(monthly_df, x='Date', y='Cumulative', title="Spend Trend This Month")
    st.plotly_chart(line_fig)
# View All Expenses
st.subheader("All Expenses")
st.dataframe(df)
# Trend Analysis: Monthly Summaries
st.subheader("Trend Analysis")
monthly_summary = df.groupby(df['Date'].dt.strftime("%Y-%m"))['Amount'].sum().reset_index(name='Total')
bar_fig = px.bar(monthly_summary, x='Date', y='Total', title="Monthly Spend Over Time")
st.plotly_chart(bar_fig)