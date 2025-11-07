import streamlit as st
import pandas as pd
import os

FILE_PATH = "wedding_data.xlsx"
BUDGET_FILE = "budget_goal.txt"

# --- Load or initialize Excel data ---
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH)
    else:
        df = pd.DataFrame(columns=["Date", "Description", "Amount"])
        df.to_excel(FILE_PATH, index=False)
        return df

def save_data(df):
    df.to_excel(FILE_PATH, index=False)

# --- Load persistent budget goal ---
def load_budget_goal():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            try:
                return float(f.read().strip())
            except ValueError:
                return 0.0
    return 0.0

def save_budget_goal(value):
    with open(BUDGET_FILE, "w") as f:
        f.write(str(value))

# --- Initialize session state ---
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "budget_goal" not in st.session_state:
    st.session_state.budget_goal = load_budget_goal()

# --- UI ---
st.title("💍 2-Year Wedding Savings Tracker")

# --- Budget goal ---
budget_goal = st.number_input(
    "🎯 Total Wedding Budget Goal ($)",
    min_value=0.0,
    value=st.session_state.budget_goal,
    step=100.0,
    key="budget_input"
)

if budget_goal != st.session_state.budget_goal:
    st.session_state.budget_goal = budget_goal
    save_budget_goal(budget_goal)

# --- Add entry ---
st.subheader("➕ Add Transaction")
desc = st.text_input("Description")
amt = st.number_input("Amount ($)", step=1.0, key="amount_input")

if st.button("Add Entry"):
    if desc and amt != 0:
        new_entry = pd.DataFrame([[pd.Timestamp.now(), desc, amt]], columns=["Date", "Description", "Amount"])
        st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
        save_data(st.session_state.data)
        st.success("✅ Entry added!")
    else:
        st.warning("Please enter a description and amount.")

# --- Current data table ---
st.subheader("📜 Transaction History")
st.dataframe(st.session_state.data, use_container_width=True)

# --- Real-time calculations ---
total_saved = st.session_state.data["Amount"].sum()
budget_goal = st.session_state.budget_goal
balance = budget_goal - total_saved

progress = total_saved / budget_goal * 100 if budget_goal > 0 else 0

# --- Display summary ---
st.markdown(f"### 💵 Current Balance: **${balance:,.2f}**")
st.markdown(f"### 💰 Total Saved: **${total_saved:,.2f} / ${budget_goal:,.2f}**")
st.progress(min(progress / 100, 1.0))

# --- Footer ---
st.caption("Your data and goal are automatically saved and will persist across sessions.")
