import streamlit as st
import pandas as pd
from datetime import date, datetime
import time  # for animation

st.set_page_config(page_title="Tra 💖 Da Saving💍", page_icon="💍", layout="centered")

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
st.markdown("<h1 style='text-align:center; color:#9A6A8D;'>Saving for Wedding💍</h1>", unsafe_allow_html=True)

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
# Accept placeholder as argument
def show_progress_bar(placeholder, progress): 
    progress = max(0, min(1, progress))
    def interpolate_color(p):
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2],16) for i in (0,2,4))
        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb
        start = hex_to_rgb("#FF69B4")  # pink
        end = hex_to_rgb("#800080")    # purple
        interp = tuple(int(start[i] + (end[i]-start[i])*p) for i in range(3))
        return rgb_to_hex(interp)
    
    color = interpolate_color(progress)
    percent = int(progress*100)
    bar_html = f"""
    <div style='
        border-radius: 12px;
        background-color: #eee;
        width: 100%;
        height: 30px;
        border: 1px solid #ccc;
        overflow: hidden;
    '>
        <div style='
            width: {percent}%;
            height: 100%;
            background: linear-gradient(90deg, #FF69B4, {color});
            text-align: center;
            line-height: 30px;
            color: white;
            font-weight: bold;
            transition: width 0.5s ease;
        '>{percent}%</div>
    </div>
    """
    # Use the placeholder to replace the content
    placeholder.markdown(bar_html, unsafe_allow_html=True) 

# --- Display initial progress ---
st.markdown(f"### ⏳ {st.session_state.days_remaining} days to go!")
# Create a placeholder for the progress bar
progress_placeholder = st.empty() 
show_progress_bar(progress_placeholder, st.session_state.progress) 
balance_metric = st.empty()
balance_metric.metric("💵 Current Balance", f"${st.session_state.current_balance:,.2f}")
st.metric("🎯 Goal", f"${st.session_state.goal_amount:,.2f}")
st.info(f"Recommended monthly save: ${st.session_state.recommended_monthly:,.2f}")

# --- Animate Progress Bar ---
def animate_progress(old_balance, new_balance):
    old_progress = max(0, min(1, old_balance / st.session_state.goal_amount))
    new_progress = max(0, min(1, new_balance / st.session_state.goal_amount))
    steps = 20
    for i in range(1, steps+1):
        interp_progress = old_progress + (new_progress - old_progress) * i / steps
        # Pass the placeholder to show_progress_bar
        show_progress_bar(progress_placeholder, interp_progress) 
        balance_metric.metric("💵 Current Balance", f"${st.session_state.current_balance:,.2f}")
        time.sleep(0.02)
    # Final state
    show_progress_bar(progress_placeholder, new_progress)
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
