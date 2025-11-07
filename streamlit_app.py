import streamlit as st
import pandas as pd
import os
from datetime import date

# ---------------- Setup ----------------
FILE_PATH = "wedding_savings.xlsx"
GOAL_FILE = "goal.txt"
DATE_FILE = "target_date.txt"

# Initialize Data
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH)
    return pd.DataFrame(columns=["Name", "Amount", "Date"])

def save_data(df):
    df.to_excel(FILE_PATH, index=False)

def load_goal():
    if os.path.exists(GOAL_FILE):
        with open(GOAL_FILE) as f:
            return float(f.read().strip())
    return 0.0

def save_goal(goal):
    with open(GOAL_FILE, "w") as f:
        f.write(str(goal))

def load_target_date():
    if os.path.exists(DATE_FILE):
        with open(DATE_FILE) as f:
            return date.fromisoformat(f.read().strip())
    return date.today()

def save_target_date(d):
    with open(DATE_FILE, "w") as f:
        f.write(str(d))

# ---------------- Load persistent data ----------------
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "goal" not in st.session_state:
    st.session_state.goal = load_goal()
if "target_date" not in st.session_state:
    st.session_state.target_date = load_target_date()

# ---------------- Page Style ----------------
st.set_page_config(page_title="Wedding Savings Tracker 💍", layout="centered")

st.markdown("""
    <style>
    body {background-color: #fffafc;}
    .main {background-color: #fffafc;}
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #4CAF50 !important;
    }
    .cute-box {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .pink-btn {
        background-color: #c79ad8 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }
    .pink-btn:hover {
        background-color: #b682c2 !important;
        color: white !important;
    }
    .label {
        color: #b682c2;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- Title ----------------
st.markdown("<h1 style='text-align:center; color:#a054b7;'>💒 Wedding Savings Tracker</h1>", unsafe_allow_html=True)

days_left = (st.session_state.target_date - date.today()).days
st.markdown(f"<h4 style='text-align:center; color:gray;'>{days_left} Days to Go!</h4>", unsafe_allow_html=True)

# ---------------- Top Summary ----------------
total_saved = st.session_state.df["Amount"].sum()
goal = st.session_state.goal
progress = (total_saved / goal * 100) if goal > 0 else 0

st.markdown(f"""
<div class='cute-box' style='text-align:center;'>
    <h2 style='color:#4CAF50;'>${total_saved:,.2f}</h2>
    <p style='color:#c79ad8;'>Goal: ${goal:,.2f}</p>
    <progress value='{progress}' max='100' style='width:90%; height:15px; border-radius:8px;'></progress>
    <p style='color:gray; font-size:0.9rem;'>{progress:.1f}% Reached</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Partner Totals ----------------
col1, col2 = st.columns(2)
with col1:
    tra_total = st.session_state.df.query("Name == 'Tra'")["Amount"].sum()
    st.markdown(f"<div class='cute-box' style='text-align:center;'><p>Tra 💙 Total:</p><h3>${tra_total:,.2f}</h3></div>", unsafe_allow_html=True)
with col2:
    da_total = st.session_state.df.query("Name == 'Da'")["Amount"].sum()
    st.markdown(f"<div class='cute-box' style='text-align:center;'><p>Da 💖 Total:</p><h3>${da_total:,.2f}</h3></div>", unsafe_allow_html=True)

# ---------------- Section 1: Goal Setup ----------------
st.markdown("### 1. Setup/Edit Goal")

goal_input = st.number_input("💰 Total Wedding Budget Goal", min_value=0.0, value=st.session_state.goal, step=100.0)
target_input = st.date_input("📅 Target Date", value=st.session_state.target_date)

if st.button("Set/Update Goal", use_container_width=True, key="goal_btn"):
    st.session_state.goal = goal_input
    st.session_state.target_date = target_input
    save_goal(goal_input)
    save_target_date(target_input)
    st.success("🎯 Goal and date updated successfully!")

# ---------------- Section 2: Add Deposit ----------------
st.markdown("### 2. Register Monthly Deposit")

months_left = max((st.session_state.target_date.year - date.today().year) * 12 + (st.session_state.target_date.month - date.today().month), 1)
recommended = (st.session_state.goal - total_saved) / months_left if months_left > 0 else 0
st.info(f"Recommended monthly save: ${recommended:,.2f}")

colA, colB = st.columns([1,1])
with colA:
    depositor = st.radio("Who deposited?", ["Tra 💙", "Da 💖"], horizontal=True)
with colB:
    amount = st.number_input("💵 Enter amount deposited", min_value=0.0, step=10.0)

if st.button("Deposit", use_container_width=True, key="deposit_btn"):
    if amount > 0:
        name = "Tra" if "Tra" in depositor else "Da"
        new_row = pd.DataFrame([[name, amount, pd.Timestamp.now().date()]], columns=["Name", "Amount", "Date"])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_data(st.session_state.df)
        st.success("💖 Deposit recorded!")
    else:
        st.warning("Please enter a valid amount.")

# ---------------- Section 3: History ----------------
st.markdown("### 3. Savings History")
if len(st.session_state.df) == 0:
    st.info("No deposits yet. Start saving for your big day! 💍")
else:
    for _, row in st.session_state.df.iloc[::-1].iterrows():
        emoji = "💙" if row["Name"] == "Tra" else "💖"
        st.markdown(
            f"<div class='cute-box' style='display:flex; justify-content:space-between; align-items:center;'>"
            f"<span>{emoji} <b>{row['Name']}</b></span>"
            f"<span>${row['Amount']:,.2f}</span>"
            f"<span style='color:gray; font-size:0.85rem;'>{row['Date']}</span>"
            f"</div>", unsafe_allow_html=True
        )

st.caption("💾 Data saved locally and stays synced across sessions.")
