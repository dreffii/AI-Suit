import streamlit as st
import pandas as pd
from datetime import date, datetime
import time  # for animation

st.set_page_config(page_title="Wedding Savings Tracker", page_icon="💍", layout="centered")

# --- File paths ---
DATA_FILE = "wedding_savings.xlsx"
GOAL_FILE = "wedding_goal.xlsx"

# --- Load / Save Data ---
def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "contributor", "amount"])
    return df

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# --- Load / Save Goal ---
def load_goal():
    try:
        goal_df = pd.read_excel(GOAL_FILE)
        return float(goal_df.loc[0, "goal_amount"]), pd.to_datetime(goal_df.loc[0, "goal_date"]).date()
    except:
        return 30000.0, date.today().replace(year=date.today().year + 2)

def save_goal(goal_amount, goal_date):
    goal_df = pd.DataFrame({"goal_amount": [goal_amount], "goal_date": [goal_date]})
    goal_df.to_excel(GOAL_FILE, index=False)

# --- Initialize session state ---
if "df" not in st.session_state:
    st.session_state.df = load_data()

if "goal_amount" not in st.session_state or "goal_date" not in st.session_state:
    saved_goal, saved_date = load_goal()
    st.session_state.goal_amount = saved_goal
    st.session_state.goal_date = saved_date

# --- UI HEADER ---
st.markdown("<h1 style='text-align:center; color:#9A6A8D;'>💍 Wedding Savings Tracker</h1>", unsafe_allow_html=True)

# --- Goal Section ---
st.subheader("1️⃣ Setup / Edit Goal")
goal_amount = st.number_input("💰 Total Wedding Budget Goal ($)",
                              min_value=100.0,
                              value=st.session_state.goal_amount,
                              step=100.0)
goal_date = st.date_input("📅 Target Wedding Date", st.session_state.goal_date)

# Save updated goal if changed
if goal_amount != st.session_state.goal_amount or goal_date != st.session_state.goal_date:
    st.session_state.goal_amount = goal_amount
    st.session_state.goal_date = goal_date
    save_goal(goal_amount, goal_date)

# --- Calculation Function ---
def update_progress():
    today = date.today()
    st.session_state.days_remaining = (st.session_state.goal_date - today).days
    st.session_state.current_balance = st.session_state.df["amount"].sum()
    st.session_state.progress = min(1.0, st.session_state.current_balance / st.session_state.goal_amount)
    st.session_state.remaining = max(0, st.session_state.goal_amount - st.session_state.current_balance)
    st.session_state.months_remaining = max(1, st.session_state.days_remaining / 30.437)
    st.session_state.recommended_monthly = st.session_state.remaining / st.session_state.months_remaining

update_progress()

# --- Custom Gradient Progress Bar ---
def display_progress_bar(progress):
    percent = int(progress * 100)
    # Gradient: pink (#FF9AA2) to purple (#9A6A8D)
    start_color = (255, 154, 162)  # pink
    end_color = (154, 106, 141)    # purple
    r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
    g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
    b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
    color = f"rgb({r},{g},{b})"
    
    bar_html = f"""
    <div style="background-color:#eee; border-radius:15px; padding:3px; width:100%;">
        <div style="
            width:{percent}%;
            background: linear-gradient(to right, #FF9AA2, #9A6A8D);
            background-color:{color};
            text-align:center;
            padding:5px 0;
            border-radius:10px;
            color:white;
            font-weight:bold;">
            {percent}%
        </div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

# --- Display Progress ---
st.markdown(f"### ⏳ {st.session_state.days_remaining} days to go!")
progress_placeholder = st.empty()
balance_metric = st.empty()
display_progress_bar(st.session_state.progress)
balance_metric.metric("💵 Current Balance", f"${st.session_state.current_balance:,.2f}")
st.metric("🎯 Goal", f"${st.session_state.goal_amount:,.2f}")
st.info(f"Recommended monthly save: ${st.session_state.recommended_monthly:,.2f}")

# --- Animate Custom Progress Bar ---
def animate_progress(old_balance, new_balance):
    old_progress = min(1.0, old_balance / st.session_state.goal_amount)
    new_progress = min(1.0, new_balance / st.session_state.goal_amount)
    steps = 20
    for i in range(1, steps + 1):
        interp_progress = old_progress + (new_progress - old_progress) * i / steps
        progress_placeholder.empty()
        display_progress_bar(interp_progress)
        balance_metric.metric("💵 Current Balance", f"${st.session_state.current_balance:,.2f}")
        time.sleep(0.02)
    progress_placeholder.empty()
    display_progress_bar(new_progress)
    balance_metric.metric("💵 Current Balance", f"${st.session_state.current_balance:,.2f}")

# --- Contribution Input ---
st.subheader("2️⃣ Register Monthly Deposit")
contributor = st.radio("Contributor", ["Tra 💙", "Da 💖"], horizontal=True)
amount = st.number_input("Deposit Amount ($)", min_value=0.01, step=10.0)
if st.button("💰 Add Deposit"):
    old_balance = st.session_state.current_balance
    new_row = pd.DataFrame({
        "date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "contributor": [contributor],
        "amount": [amount]
    })
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
    save_data(st.session_state.df)
    update_progress()
    st.success(f"Added {contributor} deposit of ${amount:,.2f}!")
    animate_progress(old_balance, st.session_state.current_balance)

# --- Contribution Summary ---
st.subheader("💑 Contribution Summary")
tra_total = st.session_state.df[st.session_state.df["contributor"] == "Tra 💙"]["amount"].sum()
da_total = st.session_state.df[st.session_state.df["contributor"] == "Da 💖"]["amount"].sum()
col1, col2 = st.columns(2)
col1.metric("Tra 💙 Total", f"${tra_total:,.2f}")
col2.metric("Da 💖 Total", f"${da_total:,.2f}")

# --- Savings History ---
st.subheader("3️⃣ Savings History")
if st.session_state.df.empty:
    st.info("No deposits recorded yet.")
else:
    st.dataframe(st.session_state.df.sort_values("date", ascending=False))

# --- Clear Option ---
if st.button("🗑️ Clear All History"):
    st.session_state.df = pd.DataFrame(columns=["date", "contributor", "amount"])
    save_data(st.session_state.df)
    st.warning("All data cleared! Refresh to start new tracking.")
