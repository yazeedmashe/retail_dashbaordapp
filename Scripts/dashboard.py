import pandas as pd
import sqlite3
import streamlit as st
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# Load data
db = sqlite3.connect(r"Database/retail_analytics.db")
df = pd.read_sql('SELECT * FROM cleaned_data', db)

# Sidebar - Filters
st.sidebar.title("🔍 Filter Data")
store_options = st.sidebar.multiselect("Select Stores:", df['StoreName'].unique())
month_options = st.sidebar.multiselect("Select Month:", sorted(df['Month'].unique()))
brand_options = st.sidebar.multiselect("Select Brand:", df['Brand'].unique())

# Apply filters
df_filtered = df.copy()
if store_options:
    df_filtered = df_filtered[df_filtered['StoreName'].isin(store_options)]
if month_options:
    df_filtered = df_filtered[df_filtered['Month'].isin(month_options)]
if brand_options:
    df_filtered = df_filtered[df_filtered['Brand'].isin(brand_options)]

# Handle empty filter result
if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# KPI Calculations
total_profit = df_filtered['Profit'].sum()
total_sales = (df_filtered['Price'] * df_filtered['Quantity']).sum()
store_unique = df_filtered['StoreID'].nunique()
product_numbers = df_filtered['ProductID'].nunique()

def format_large_currency(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:,.2f}"

# --- Layout ---
st.title("📊 Retail Sales & Profit Dashboard")

st.markdown("Use the filters in the sidebar to slice and explore retail performance by store, brand, and month.")

# KPIs
st.markdown("### 🔢 Key Performance Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Profit", f"${total_profit:,.2f}")
col2.metric("🛒 Total Sales", format_large_currency(total_sales))
col3.metric("🏪 Stores", store_unique)
col4.metric("📦 Products", product_numbers)

st.markdown("---")

# Charts Section
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### 📂 Profit by Category")
    category_profit = df_filtered.groupby('Category')['Profit'].sum().reset_index()
    st.bar_chart(category_profit.set_index('Category'))

with col_chart2:
    st.markdown("### 📈 Monthly Profit Trend")
    monthly_profit = df_filtered.groupby('Month')['Profit'].sum().reset_index()
    st.line_chart(monthly_profit.set_index('Month'))

st.markdown("### 🥧 Profitability Distribution")
# Pie Chart
profit_dist = df_filtered['Profitability'].value_counts().reindex(['Loss', 'Low Profit', 'High Profit']).dropna()

fig, ax = plt.subplots(figsize=(5, 5))
colors = ['#ff4d4d', '#ffd11a', '#4CAF50']
ax.pie(profit_dist, labels=profit_dist.index, autopct='%1.1f%%', colors=colors, startangle=90)
ax.set_title("Profitability Distribution", fontsize=14)

st.pyplot(fig)
