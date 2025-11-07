import streamlit as st
import pandas as pd
from datetime import date, datetime
import time  # for animation

st.set_page_config(page_title="Tra 💖 Da Saving💍", page_icon="💍", layout="centered")

# --- File paths ---
# Note: In a real Streamlit app, these would manage local files. 
# In this environment, we rely on the internal file system persistence.
DATA_FILE = "wedding_savings.xlsx"
GOAL_FILE = "wedding_goal.xlsx"

# --- Load / Save Data (Using simplified Excel persistence for the context) ---
def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
        # Ensure 'date' is a string if loaded from excel for consistent display
        df['date'] = df['date'].astype(str)
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
with st.form("goal_form"):
    goal_amount = st.number_input("💰 Total Wedding Budget Goal ($)",
                                  min_value=100.0,
                                  value=st.session_state.goal_amount,
                                  step=100.0)
    goal_date = st.date_input("📅 Target Wedding Date", st.session_state.goal_date)
    
    submitted = st.form_submit_button("Save Goal")
    if submitted:
        st.session_state.goal_amount = goal_amount
        st.session_state.goal_date = goal_date
        save_goal(goal_amount, goal_date)
        st.experimental_rerun() # Rerun to update calculations immediately

# --- Calculation Function ---
def update_progress():
    today = date.today()
    # Ensure goal_date is a date object for subtraction
    goal_date_obj = st.session_state.goal_date
    if isinstance(goal_date_obj, datetime):
        goal_date_obj = goal_date_obj.date()
        
    st.session_state.days_remaining = max(0, (goal_date_obj - today).days)
    st.session_state.current_balance = st.session_state.df["amount"].sum()
    st.session_state.progress = min(1.0, st.session_state.current_balance / st.session_state.goal_amount)
    st.session_state.remaining = max(0, st.session_state.goal_amount - st.session_state.current_balance)
    
    # Calculate months remaining safely
    if st.session_state.days_remaining > 0:
        st.session_state.months_remaining = st.session_state.days_remaining / 30.437
    else:
        st.session_state.months_remaining = 1 # Avoid division by zero if goal is today or past

    st.session_state.recommended_monthly = st.session_state.remaining / max(1, st.session_state.months_remaining)

update_progress()

# --- Custom Liquid Progress Bar (Refactored) ---
def show_progress_bar(placeholder, progress):
    # Ensure a minimum value so the text and animation can display nicely
    progress = max(0.01, min(1, progress)) 
    percent = int(progress * 100)
    
    # This height controls the liquid level in the bar
    fill_height = f"{percent}%"
    
    # CSS for the Liquid/Wave effect
    liquid_css = """
    <style>
    /* Keyframe animation for the wave motion */
    @keyframes wave-motion {
        0% { transform: translate(-50%, -100%) rotate(0deg); }
        100% { transform: translate(-50%, -100%) rotate(360deg); }
    }
    .liquid-bar-container {
        border-radius: 12px;
        background-color: #eee;
        width: 100%;
        height: 30px;
        border: 2px solid #9A6A8D; /* Darker border for emphasis */
        overflow: hidden; 
        position: relative;
    }
    /* The element that controls the height of the fill */
    .liquid-level {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 0; /* Default height is controlled by the style attribute below */
        background: linear-gradient(90deg, #FF69B4, #800080); /* Pink to Purple */
        transition: height 0.5s ease; /* Animate the level change */
    }
    /* Wave container for pseudo-elements */
    .liquid-wave {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
    }
    /* First wave layer */
    .liquid-wave::before, .liquid-wave::after {
        content: '';
        position: absolute;
        width: 200%; /* Wider than container for wave shape */
        height: 200%;
        left: -50%;
        top: -100%; 
        border-radius: 40%; /* Creates the circular/wave shape */
        background: rgba(255, 255, 255, 0.4); /* Semi-transparent white for wave crests */
        z-index: 1; 
        animation: wave-motion 6s linear infinite;
    }
    /* Second wave layer for depth */
    .liquid-wave::after {
        border-radius: 45%;
        background: rgba(255, 255, 255, 0.2); 
        animation: wave-motion 8s linear infinite reverse;
        z-index: 2; 
    }
    /* Text overlay */
    .progress-text {
        position: absolute;
        width: 100%;
        text-align: center;
        line-height: 30px;
        font-weight: bold;
        color: #000; /* Black text for contrast */
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        z-index: 3; /* Always on top */
    }
    </style>
    """
    
    # HTML structure to apply the liquid effect
    bar_html = f"""
    {liquid_css}
    <div class='liquid-bar-container'>
        <div class='progress-text'>{percent}%</div>
        <div class='liquid-level' style='height: {fill_height};'>
            <div class='liquid-wave'></div>
        </div>
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
        
        # Calculate interpolated balance for smoother metric update
        interp_balance = old_balance + (new_balance - old_balance) * i / steps
        # Update the balance metric, though Streamlit might rate-limit this
        balance_metric.metric("💵 Current Balance", f"${interp_balance:,.2f}")
        
        time.sleep(0.02)
    
    # Final state
    show_progress_bar(progress_placeholder, new_progress)
    balance_metric.metric("💵 Current Balance", f"${new_balance:,.2f}")

# --- Contribution Input ---
st.subheader("2️⃣ Register Monthly Deposit")
# Use a form to clear inputs automatically after submission
with st.form("deposit_form", clear_on_submit=True):
    contributor = st.radio("Contributor", ["Tra 💙", "Da 💖"], horizontal=True, key="contributor_radio")
    amount = st.number_input("Deposit Amount ($)", min_value=0.01, step=10.0, key="deposit_amount")
    
    if st.form_submit_button("💰 Add Deposit"):
        if amount > 0:
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
            # Run animation logic
            animate_progress(old_balance, st.session_state.current_balance)
            # Rerun to update the entire state/dataframe display after animation
            st.rerun()
        else:
            st.error("Please enter a valid deposit amount.")

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
    # Prepare dataframe for display
    display_df = st.session_state.df.copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
    display_df = display_df.rename(columns={'date': 'Date/Time', 'contributor': 'Partner', 'amount': 'Amount ($)'})
    
    st.dataframe(display_df.sort_values("Date/Time", ascending=False), 
                 hide_index=True)

# --- Clear Option ---
st.markdown("---")
if st.button("🗑️ Clear All History", type="secondary"):
    st.session_state.df = pd.DataFrame(columns=["date", "contributor", "amount"])
    save_data(st.session_state.df)
    st.session_state.current_balance = 0.0
    st.warning("All data cleared! Refreshing...")
    st.experimental_rerun()
