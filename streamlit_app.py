import streamlit as st
import pandas as pd
from datetime import date, datetime
import time # for animation
import os # ADDED for file manipulation (PIN reset)
import requests # ADDED for Telegram notification

# Set page configuration with a romantic icon
st.set_page_config(page_title="Tra 💖 Da Saving💍", page_icon="💖", layout="centered")

# --- Telegram Configuration (REPLACE THESE WITH YOUR ACTUAL VALUES) ---
# 1. Get your Bot Token from BotFather on Telegram.
TELEGRAM_BOT_TOKEN = "8187368929:AAHFoCQIATHz3ymLvotteHCLTFRW0jrlNK8" 
# 2. Get your Chat ID by sending a message to your bot and checking the API response: 
# https://api.telegram.org/bot<8187368929:AAHFoCQIATHz3ymLvotteHCLTFRW0jrlNK8>/getUpdates
TELEGRAM_CHAT_ID = "-1002080927811" 
# -----------------------------------------------------------------------

# --- Telegram Notification Function ---
def send_telegram_notification(message):
    """Sends a message to the configured Telegram chat."""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        print("Telegram notification skipped: Please configure BOT_TOKEN and CHAT_ID.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() # Raise exception for bad status codes
        print(f"Telegram notification sent successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        # Note: In a production environment, you might log this error instead of printing.
        print(f"Failed to send Telegram notification: {e}")
        

# --- Custom Styling for Cuteness (Floating Card on Light Lavender Theme) ---
st.markdown("""
<style>
    /* 1. Outer Background - Light Lavender/Purple */
    .stApp {
        background: #F5EEF8; /* Very soft lavender/purple */
    }

    /* Main Header Styling */
    .cute-header {
        text-align: center;
        color: #C71585; /* Deep Pink/Medium Violet Red */
        font-family: 'Georgia', serif;
        padding: 10px 0 20px 0;
        border-bottom: 3px solid #FFC0CB; /* Light Pink separator */
    }
    /* Subheader Styling */
    h3 {
        color: #800080; /* Purple for subheaders */
        border-left: 5px solid #FFC0CB; /* Pink accent line */
        padding-left: 10px;
    }
    
    /* General input/container styling - Individual components now look like cards */
    /* NOTE: stDataFrame has been removed from this list to apply specialized styling below */
    .stNumberInput, .stDateInput, .stRadio, .stMetric, .stInfo, .stTextInput {
        border-radius: 12px !important;
        background-color: #FFFFFF; /* White background for individual components */
        padding: 15px; /* Increased padding slightly for better card look */
        box-shadow: 0 4px 12px rgba(199, 21, 133, 0.1); /* Slightly deeper soft shadow */
        margin-bottom: 20px; /* Increased margin for separation */
        border: 1px solid #FFC0CB; /* Soft border */
    }
    
    /* Info box styling */
    .stAlert {
        border-radius: 12px !important;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #FFC0CB; /* Pink */
        color: #800080; /* Purple text */
        font-weight: bold;
        border: 2px solid #C71585;
        border-radius: 10px;
        transition: all 0.2s ease;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #C71585;
        color: white;
        transform: translateY(-2px);
    }
    
    /* --- FIX FOR DATAFRAME ALIGNMENT --- */
    /* Target the parent container of the dataframe widget specifically for card styling */
    .stDataFrame {
        /* Apply card styling */
        border-radius: 12px !important;
        background-color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(199, 21, 133, 0.1);
        margin-bottom: 20px;
        border: 1px solid #FFC0CB;
        
        /* Override default internal padding that caused misalignment */
        padding: 0 !important;
        overflow: hidden; /* Ensures borders are rounded correctly */
    }

    /* Apply internal padding to the specific area where the table content starts */
    .stDataFrame .stDataFrame-base {
        padding: 15px !important; /* Matches the 15px used in other card components */
    }

</style>
""", unsafe_allow_html=True)

# --- File paths ---
DATA_FILE = "wedding_savings.xlsx"
GOAL_FILE = "wedding_goal.xlsx"
PIN_FILE = "wedding_pin.xlsx" # New file for PIN storage

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
    """Loads goal amount and date from the goal file."""
    try:
        goal_df = pd.read_excel(GOAL_FILE)
        # Ensure goal_date is read as a date object
        goal_date = pd.to_datetime(goal_df.loc[0, "goal_date"]).date()
        goal_amount = float(goal_df.loc[0, "goal_amount"])
        return goal_amount, goal_date
    except Exception:
        # Default values if file not found or corrupted
        return 30000.0, date.today().replace(year=date.today().year + 2)

def save_goal(goal_amount, goal_date):
    """Saves both goal amount and date to the goal file."""
    goal_df = pd.DataFrame({"goal_amount": [goal_amount], "goal_date": [goal_date]})
    goal_df.to_excel(GOAL_FILE, index=False)
    
# --- Load / Save PIN ---
def load_pin():
    """Loads the PIN from the PIN file."""
    try:
        pin_df = pd.read_excel(PIN_FILE)
        return str(pin_df.loc[0, "pin_code"])
    except Exception:
        # Default PIN if file not found or corrupted (e.g., '1234')
        return None

def save_pin(pin_code):
    """Saves the PIN to the PIN file."""
    pin_df = pd.DataFrame({"pin_code": [pin_code]})
    pin_df.to_excel(PIN_FILE, index=False)

# --- Delete PIN function ---
def delete_pin():
    """Deletes the PIN file to reset the PIN."""
    try:
        # Check if the file exists before trying to remove it
        if os.path.exists(PIN_FILE):
            os.remove(PIN_FILE)
            return True
        return False
    except Exception as e:
        # Log the error, but continue execution
        print(f"Error resetting PIN file: {e}")
        return False

# --- Callback function to handle login submission (used by Enter key and button) ---
def handle_login_submit(input_key, current_pin):
    input_pin = st.session_state[input_key]
    RESET_CODE = "330533"

    if input_pin == RESET_CODE:
        delete_pin()
        st.session_state.logged_in = False
        st.success("🔒 PIN successfully reset! Please set a new 4-digit PIN below.")
        # Note: st.rerun() is unnecessary here as a rerun is automatically scheduled after the callback.
    
    elif current_pin is None:
        # Handling initial PIN setup submission
        if input_pin and len(input_pin) == 4 and input_pin.isdigit():
            save_pin(input_pin)
            st.session_state.logged_in = True
        else:
            st.error("Please enter a valid 4-digit numeric PIN.")
            st.session_state.logged_in = False

    elif len(input_pin) == 4 and input_pin == current_pin:
        # Handling normal login
        st.session_state.logged_in = True
    
    else:
        st.error("Incorrect Love PIN or invalid code. Try again!")
        st.session_state.logged_in = False

    # Check if the login state changed. If it did, the app needs to rerender 
    # (which happens automatically, but we ensure the state is marked for rerun if needed).
    # Removing st.rerun() but keeping the state tracking might be useful for other features later.
    if st.session_state.logged_in != st.session_state.get('prev_logged_in_state', False):
        st.session_state.prev_logged_in_state = st.session_state.logged_in
        # st.rerun() removed here to clear the warning.


# --- Initialize session state ---
if "df" not in st.session_state:
    st.session_state.df = load_data()

if "goal_amount" not in st.session_state or "goal_date" not in st.session_state:
    saved_goal, saved_date = load_goal()
    st.session_state.goal_amount = saved_goal
    st.session_state.goal_date = saved_date
    
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
# --- Authentication Logic ---

def login_app():
    # 1. Load the stored PIN
    current_pin = load_pin()
    
    st.markdown("<h1 class='cute-header'>🔒 Welcome to Our Secret Fund! 💖</h1>", unsafe_allow_html=True)

    if current_pin is None:
        # --- PIN Setup Screen ---
        st.subheader("Set Up Your Love PIN (4-digit)")
        
        # Pass the callback function to on_change
        new_pin = st.text_input("Choose a 4-digit PIN", 
                                type="password", 
                                max_chars=4, 
                                key="new_pin_input",
                                on_change=handle_login_submit,
                                args=("new_pin_input", None)) # Pass None for current_pin during setup
        
        if st.button("🔐 Save PIN and Enter App"):
            handle_login_submit("new_pin_input", None)
        
        st.markdown("<p style='text-align: center; color: #800080; margin-top: 20px;'>*This PIN will protect access to your budget tracker.*</p>", unsafe_allow_html=True)
        
    else:
        # --- PIN Login Screen (Modified for Reset Code) ---
        st.subheader("Enter Your Love PIN or Reset Code")
        
        # Pass the callback function to on_change
        input_pin = st.text_input("Love PIN", 
                                  type="password", 
                                  max_chars=6, 
                                  key="login_pin_input",
                                  on_change=handle_login_submit,
                                  args=("login_pin_input", current_pin))
        
        if st.button("💖 Unlock Fund"):
            handle_login_submit("login_pin_input", current_pin)

        # Update the helper text to mention the reset code
        RESET_CODE = "330533"
        st.markdown(
            f"<p style='text-align: center; color: #800080; margin-top: 20px;'>"
            f"*If you forget your PIN, enter the 6-digit reset code **{RESET_CODE}** above.*"
            f"</p>", unsafe_allow_html=True)
    
    # Stop execution here if not logged in
    # Since we are modifying session state in the callback, a rerun is needed 
    # to show the main content, which happens automatically after this function returns.
    return False

# Check authentication status
if not st.session_state.logged_in:
    login_app()
    st.stop()
    
# --- Main Application Content (Only runs if logged_in is True) ---

# --- UI HEADER (Now using the cute-header class) ---
st.markdown("<h1 class='cute-header'>💖 Our Wedding Fund 💍</h1>", unsafe_allow_html=True)

# --- Goal Section ---
st.subheader("1️⃣ Set Our Dream Goal")
goal_amount = st.number_input("💸 Total Dream Budget ($)",
                             min_value=100.0,
                             value=st.session_state.goal_amount,
                             step=100.0)
goal_date = st.date_input("🗓️ Target 'I Do' Date", st.session_state.goal_date)

# Save updated goal if changed (This ensures both amount and date are saved together)
if goal_amount != st.session_state.goal_amount or goal_date != st.session_state.goal_date:
    st.session_state.goal_amount = goal_amount
    st.session_state.goal_date = goal_date
    save_goal(goal_amount, goal_date)

# --- Calculation Function ---
def update_progress():
    today = date.today()
    # Ensure goal_date is a date object for subtraction
    if isinstance(st.session_state.goal_date, datetime):
        goal_date_obj = st.session_state.goal_date.date()
    else:
        goal_date_obj = st.session_state.goal_date

    st.session_state.days_remaining = (goal_date_obj - today).days
    st.session_state.current_balance = st.session_state.df["amount"].sum()
    st.session_state.progress = min(1.0, st.session_state.current_balance / st.session_state.goal_amount)
    st.session_state.remaining = max(0, st.session_state.goal_amount - st.session_state.current_balance)
    st.session_state.months_remaining = max(1, st.session_state.days_remaining / 30.437)
    st.session_state.recommended_monthly = st.session_state.remaining / st.session_state.months_remaining

update_progress()

# --- Custom Gradient Progress Bar ---
def show_progress_bar(placeholder, progress):
    progress = max(0, min(1, progress))
    def interpolate_color(p):
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2],16) for i in (0,2,4))
        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb
        start = hex_to_rgb("#FFC0CB")  # Light Pink
        end = hex_to_rgb("#C71585")    # Deep Pink
        interp = tuple(int(start[i] + (end[i]-start[i])*p) for i in range(3))
        return rgb_to_hex(interp)

    color = interpolate_color(progress)
    percent = int(progress*100)
    bar_html = f"""
    <div style='
        border-radius: 12px;
        background-color: #f7f7f7;
        width: 100%;
        height: 30px;
        border: 2px solid #FFC0CB; /* Light Pink border */
        overflow: hidden;
        margin-bottom: 20px; /* Added margin here */
    '>
        <div style='
            width: {percent}%;
            height: 100%;
            background: linear-gradient(90deg, #FFC0CB, {color});
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

# --- Display initial progress (Cuter Language) ---
st.markdown(f"### 💖 {st.session_state.days_remaining} Days Until We Say 'I Do'! 🥂")
# Check if goal is reached or date passed
if st.session_state.remaining <= 0 and st.session_state.days_remaining >= 0:
    st.balloons()
    st.success("🎉 Goal Reached! Time to plan the details!")

progress_placeholder = st.empty()
show_progress_bar(progress_placeholder, st.session_state.progress)
balance_metric = st.empty()
balance_metric.metric("✨ Current Balance", f"${st.session_state.current_balance:,.2f}", delta_color="normal")
st.metric("🎯 Dream Goal", f"${st.session_state.goal_amount:,.2f}")

if st.session_state.remaining > 0 and st.session_state.days_remaining > 0:
    st.info(f"💌 Suggested Monthly Love Deposit: **${st.session_state.recommended_monthly:,.2f}**")


# --- Animate Progress Bar ---
def animate_progress(old_balance, new_balance):
    old_progress = max(0, min(1, old_balance / st.session_state.goal_amount))
    new_progress = max(0, min(1, new_balance / st.session_state.goal_amount) if st.session_state.goal_amount > 0 else 1)
    steps = 20
    for i in range(1, steps+1):
        interp_progress = old_progress + (new_progress - old_progress) * i / steps
        # Pass the placeholder to show_progress_bar
        show_progress_bar(progress_placeholder, interp_progress)
        # Recalculate and update the current balance metric during animation
        current_display_balance = old_balance + (new_balance - old_balance) * i / steps
        balance_metric.metric("✨ Current Balance", f"${current_display_balance:,.2f}")
        time.sleep(0.02)
    # Final state
    show_progress_bar(progress_placeholder, new_progress)
    balance_metric.metric("✨ Current Balance", f"${st.session_state.current_balance:,.2f}")

# --- Contribution Input (Cuter Language) ---
st.subheader("2️⃣ Record Our Love Deposit")
contributor = st.radio("Who's contributing this time?", ["Tra 💙", "Da 💖"], horizontal=True)
amount = st.number_input("Love Deposit Amount ($)", min_value=0.01, step=10.0)
if st.button("💖 Add Love Deposit"):
    old_balance = st.session_state.current_balance
    new_row = pd.DataFrame({
        "date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "contributor": [contributor],
        "amount": [amount]
    })
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
    save_data(st.session_state.df)
    update_progress()
    st.success(f"A beautiful deposit of ${amount:,.2f} added by {contributor}!")
    
    # --- Telegram Notification Trigger ---
    notification_message = (
        f"💖 *Love Deposit Alert!* 💖\n\n"
        f"Deposited by: {contributor}\n"
        f"Amount: *${amount:,.2f}*\n"
        f"Current Total: *${st.session_state.current_balance:,.2f}*\n"
        f"Remaining Goal: *${st.session_state.remaining:,.2f}*"
    )
    send_telegram_notification(notification_message)
    # ------------------------------------

    animate_progress(old_balance, st.session_state.current_balance)

# --- Contribution Summary (Cuter Language) ---
st.subheader("💑 Our Combined Love Totals")
tra_total = st.session_state.df[st.session_state.df["contributor"] == "Tra 💙"]["amount"].sum()
da_total = st.session_state.df[st.session_state.df["contributor"] == "Da 💖"]["amount"].sum()
col1, col2 = st.columns(2)
# Added Emojis to the metrics
col1.metric("Tra 💙's Total", f"💰 ${tra_total:,.2f}", delta_color="off")
col2.metric("Da 💖's Total", f"💐 ${da_total:,.2f}", delta_color="off")

# --- Savings History (Cuter Language) ---
st.subheader("3️⃣ Our Funding Journey")
if st.session_state.df.empty:
    st.info("The journey begins! Add your first Love Deposit above.")
else:
    # Rename columns for display
    display_df = st.session_state.df.sort_values("date", ascending=False).rename(columns={
        "date": "Date & Time",
        "contributor": "Depositor",
        "amount": "Amount ($)"
    })
    
    # Render the dataframe with container width for responsiveness
    st.dataframe(display_df, use_container_width=True)

# --- Clear Option ---
st.markdown("---")
if st.button("💔 Reset Everything (Use with caution!)"):
    st.session_state.df = pd.DataFrame(columns=["date", "contributor", "amount"])
    save_data(st.session_state.df)
    st.warning("All history cleared! Please refresh the page to restart your beautiful journey.")
