import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Wedding Savings Tracker", page_icon="💍", layout="centered")

# --- Excel setup ---
FILE_PATH = "wedding_savings.xlsx"
GOAL_FILE = "wedding_goal.xlsx"  # store goal persistently

# Initialize or load existing data
def load_data():
    try:
        df = pd.read_excel(FILE_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "contributor", "amount"])
    return df

def save_data(df):
    df.to_excel(FILE_PATH, index=False)

def load_goal():
    try:
        goal_df = pd.read_excel(GOAL_FILE)
        return float(goal_df.loc[0, "goal_amount"]), pd.to_datetime(goal_df.loc[0, "goal_date"]).date()
    except:
        return 30000.0, date.today().replace(year=date.today().year + 2)

def save_goal(goal_amount, goal_date):
    goal_df = pd.DataFrame({"goal_amount": [goal_amount], "goal_date": [goal_date]})
    goal_df.to_excel(GOAL_FILE, index=False)

# --- Load Data ---
df = load_data()

# --- GOAL SECTION ---
st.subheader("1️⃣ Setup / Edit Goal")

if "goal_amount" not in st.session_state or "goal_date" not in st.session_state:
    saved_goal, saved_date = load_goal()
    st.session_state.goal_amount = saved_goal
    st.session_state.goal_date = saved_date

goal_amount = st.number_input("💰 Total Wedding Budget Goal ($)", min_value=100.0,
                              value=st.session_state.goal_amount, step=100.0)
goal_date = st.date_input("📅 Target Wedding Date", st.session_state.goal_date)

# Save updated goal if changed
if goal_amount != st.session_state.goal_amount or goal_date != st.session_state.goal_date:
    st.session_state.goal_amount = goal_amount
    st.session_state.goal_date = goal_date
    save_goal(goal_amount, goal_date)

# --- CALCULATIONS ---
today = date.today()
days_remaining = (goal_date - today).days
current_balance = df["amount"].sum()
progress = min(1.0, current_balance / goal_amount)
remaining = max(0, goal_amount - current_balance)

months_remaining = max(1, days_remaining / 30.437)
recommended_monthly = remaining / months_remaining

# --- DISPLAY PROGRESS ---
st.markdown(f"### ⏳ {days_remaining} days to go!")
st.progress(progress)
st.markdown(f"**{progress*100:.1f}% reached**")
st.metric("💵 Current Balance", f"${current_balance:,.2f}")
st.metric("🎯 Goal", f"${goal_amount:,.2f}")
st.info(f"Recommended monthly save: ${recommended_monthly:,.2f}")

# --- CONTRIBUTION INPUT ---
st.subheader("2️⃣ Register Monthly Deposit")
contributor = st.radio("Contributor", ["Tra 💙", "Da 💖"], horizontal=True)
amount = st.number_input("Deposit Amount ($)", min_value=0.01, step=10.0)
if st.button("💰 Add Deposit"):
    new_row = pd.DataFrame({
        "date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "contributor": [contributor],
        "amount": [amount]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    st.success(f"Added {contributor} deposit of ${amount:,.2f}!")

# --- CONTRIBUTION SUMMARY ---
st.subheader("💑 Contribution Summary")
tra_total = df[df["contributor"] == "Tra 💙"]["amount"].sum()
da_total = df[df["contributor"] == "Da 💖"]["amount"].sum()
col1, col2 = st.columns(2)
col1.metric("Tra 💙 Total", f"${tra_total:,.2f}")
col2.metric("Da 💖 Total", f"${da_total:,.2f}")

# --- HISTORY SECTION ---
st.subheader("3️⃣ Savings History")
if df.empty:
    st.info("No deposits recorded yet.")
else:
    st.dataframe(df.sort_values("date", ascending=False))

# --- CLEAR OPTION ---
if st.button("🗑️ Clear All History"):
    save_data(pd.DataFrame(columns=["date", "contributor", "amount"]))
    st.warning("All data cleared! Refresh to start new tracking.")
