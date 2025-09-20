import base64
import re
from typing import Dict, Any, List, Tuple
import streamlit as st
import random

# -----------------------------
# Configuration
# -----------------------------
APP_TITLE = "Finance Chatbot"
BG_IMAGE_PATH = "silvia_bg.jpg"  # Optional local image
BG_IMAGE_URL = ""  # Optional URL background

DEFAULT_EMAIL = "2k24cse112@kiot.ac.in"
DEFAULT_PASSWORD = "12345678"

# -----------------------------
# Finance Bot Helper Functions
# -----------------------------
def extract_number(text):
    m = re.search(r"(\d+(\.\d+)?)", str(text).replace(",", ""))
    return float(m.group(1)) if m else None

def format_inr(x):
    return f"₹{int(x):,}" if abs(x - int(x)) < 0.01 else f"₹{x:,.2f}"

def monthly_tax(income):
    annual = income * 12
    tax = 0
    if annual <= 250000:
        tax = 0
    elif annual <= 500000:
        tax = (annual - 250000) * 0.05
    elif annual <= 1000000:
        tax = 250000*0.05 + (annual - 500000)*0.2
    else:
        tax = 250000*0.05 + 500000*0.2 + (annual - 1000000)*0.3
    return round(tax/12,2)

def compound_amount(P, rate, years):
    A = P * ((1 + rate) ** years)
    return round(A,2)

def simple_finance_bot(user_msg, chat_history=None, state=None):
    if chat_history is None:
        chat_history = []
    if state is None:
        state = {"step":0, "mode":None, "idea":None, "budget":None, "deposit":None, 
                 "years":None, "senior":None, "salary":None, "spending":None}

    text = user_msg.strip().lower()
    
    def add_bot_message(msg):
        chat_history.append(("bot", msg))
    
    def add_user_message(msg):
        chat_history.append(("user", msg))

    # Add user message first (only if not empty)
    if user_msg.strip():
        add_user_message(user_msg)

    # Step 0: Greeting
    if state["step"] == 0:
        add_bot_message("✨ Hi there! What would you like to do today?\nOptions: Business, Interest, Profit-Loss")
        state["step"] = 1
        return chat_history, state

    # Step 1: Choose mode
    if state["step"] == 1:
        if "business" in text:
            state["mode"] = "business"
            state["step"] = 2
            add_bot_message("Great! Enter your business idea.")
        elif "interest" in text:
            state["mode"] = "interest"
            state["step"] = 10
            add_bot_message("Interest mode selected. Enter deposit amount:")
        elif "profit" in text or "loss" in text:
            state["mode"] = "profit"
            state["step"] = 20
            add_bot_message("Profit/Loss mode. Enter your monthly income:")
        else:
            add_bot_message("Please type one: Business, Interest, Profit-Loss.")
        return chat_history, state

    # ---------- Business ----------
    if state["mode"] == "business":
        if state["step"] == 2:  # idea
            state["idea"] = user_msg
            state["step"] = 3
            add_bot_message(f"Got it! Now enter your planned budget in numbers for {state['idea']}:")
            return chat_history, state
        if state["step"] == 3:  # budget
            amt = extract_number(user_msg)
            if amt:
                state["budget"] = amt
                add_bot_message(f"Awesome! Your business '{state['idea']}' with budget {format_inr(amt)} is ready to start. Simple advice: Keep your expenses lean and start small!")
                state["step"] = 99
            else:
                add_bot_message("Please enter a valid number for budget.")
            return chat_history, state

    # ---------- Interest ----------
    if state["mode"] == "interest":
        if state["step"] == 10:
            amt = extract_number(user_msg)
            if amt:
                state["deposit"] = amt
                state["step"] = 11
                add_bot_message("Enter tenure in years (e.g., 2 or 3.5):")
            else:
                add_bot_message("Enter a valid deposit amount in numbers.")
            return chat_history, state
        if state["step"] == 11:
            yrs = extract_number(user_msg)
            if yrs:
                state["years"] = yrs
                state["step"] = 12
                add_bot_message("Are you a senior citizen? (yes/no)")
            else:
                add_bot_message("Enter a valid number for years.")
            return chat_history, state
        if state["step"] == 12:
            state["senior"] = True if "yes" in text else False
            rate = 0.08 if state["senior"] else 0.06
            A = compound_amount(state["deposit"], rate, state["years"])
            monthly = round(A/(state["years"]*12),2)
            add_bot_message(f"Deposit: {format_inr(state['deposit'])}\nYears: {state['years']}\nRate: {rate*100:.1f}%\nTotal after {state['years']} years: {format_inr(A)}\nMonthly average: {format_inr(monthly)}")
            state["step"] = 99
            return chat_history, state

    # ---------- Profit-Loss ----------
    if state["mode"] == "profit":
        if state["step"] == 20:
            salary = extract_number(user_msg)
            if salary:
                state["salary"] = salary
                state["step"] = 21
                add_bot_message("Enter your monthly spending:")
            else:
                add_bot_message("Enter valid salary in numbers.")
            return chat_history, state
        if state["step"] == 21:
            spend = extract_number(user_msg)
            if spend:
                state["spending"] = spend
                profit = state["salary"] - spend
                tax = monthly_tax(state["salary"])
                net = profit - tax
                add_bot_message(f"Monthly Income: {format_inr(state['salary'])}\nSpending: {format_inr(spend)}\nProfit before tax: {format_inr(profit)}\nCorporate Tax: {format_inr(tax)}\nNet Profit: {format_inr(net)}")
                state["step"] = 99
            else:
                add_bot_message("Enter valid spending amount.")
            return chat_history, state

    # ---------- Reset / Done ----------
    if state["step"] == 99:
        add_bot_message("Done ✅. Type 'reset' to start over or choose another mode.")
        if "reset" in text:
            state = {"step":0,"mode":None,"idea":None,"budget":None,"deposit":None,"years":None,"senior":None,"salary":None,"spending":None}
            add_bot_message("Chat reset! What would you like to do?\nOptions: Business, Interest, Profit-Loss")
            state["step"] = 1
        return chat_history, state

    add_bot_message("I didn't understand. Type 'Business', 'Interest', or 'Profit-Loss'.")
    return chat_history, state

# -----------------------------
# Session State Initialization
# -----------------------------
if "users" not in st.session_state:
    st.session_state.users: Dict[str, Dict[str, Any]] = { # type: ignore
        DEFAULT_EMAIL.lower(): {
            "first": "Default",
            "last": "User",
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD,
            "role": "Student",
            "core": "Default Core",
            "first_login": True,
        }
    }

if "page" not in st.session_state:
    st.session_state.page = "login"

if "budget_data" not in st.session_state:
    st.session_state.budget_data: Dict[str, Any] = {} # type: ignore

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Initialize chatbot state
if "chatbot_history" not in st.session_state:
    st.session_state.chatbot_history = []

if "chatbot_state" not in st.session_state:
    st.session_state.chatbot_state = {"step":0, "mode":None, "idea":None, "budget":None, 
                                      "deposit":None, "years":None, "senior":None, 
                                      "salary":None, "spending":None}

# -----------------------------
# Helpers
# -----------------------------
def _encode_bg(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

def set_background():
    b64 = _encode_bg(BG_IMAGE_PATH) if BG_IMAGE_PATH else ""
    if b64:
        bg_css = f"background-image: url('data:image/jpg;base64,{b64}');"
    elif BG_IMAGE_URL:
        bg_css = f"background-image: url('{BG_IMAGE_URL}');"
    else:
        bg_css = "background-image: radial-gradient(ellipse at top, #524a7b 0%, #1a1a2e 60%, #0f0f1a 100%);"

    st.markdown(f"""
        <style>
            .stApp {{
                {bg_css}
                background-size: cover;
                background-position: center center;
                background-attachment: fixed;
            }}
            .overlay {{
                position: fixed;
                inset: 0;
                background: rgba(10, 12, 22, 0.35);
                backdrop-filter: blur(1.2px);
                z-index: 0;
            }}
            .glass {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.18);
                box-shadow: 0 10px 30px rgba(0,0,0,0.25);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                border-radius: 16px;
                padding: 28px;
            }}
            .hero h1 {{
                color: #ffffff;
                font-weight: 700;
                letter-spacing: 0.2px;
                margin-bottom: 6px;
            }}
            .chat-message {{
                padding: 10px;
                margin: 5px 0;
                border-radius: 10px;
                max-width: 80%;
            }}
            .user-message {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
                text-align: right;
            }}
            .bot-message {{
                background: rgba(255, 255, 255, 0.15);
                color: white;
                margin-right: auto;
                text-align: left;
            }}
            .chat-container {{
                height: 400px;
                overflow-y: auto;
                padding: 20px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                margin: 20px 0;
            }}
            footer {{visibility: hidden;}}
            a {{ text-decoration: none; }}
            /* Custom styling for account buttons */
            .account-button {{
                width: 2.5cm !important;
                max-width: 2.5cm !important;
                min-width: 2.5cm !important;
                height: 32px !important;
                padding: 4px 8px !important;
                font-size: 12px !important;
                margin: 2px 0 !important;
                text-align: center !important;
            }}
            .stButton[data-testid="baseButton-secondary"] > button {{
                width: 2.5cm !important;
                max-width: 2.5cm !important;
                min-width: 2.5cm !important;
                height: 32px !important;
                padding: 4px 8px !important;
                font-size: 12px !important;
                margin: 2px 0 !important;
            }}
        </style>
        <div class="overlay"></div>
    """, unsafe_allow_html=True)

def email_valid(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))

def passwords_ok(pw: str, confirm: str) -> str:
    if len(pw) < 8:
        return "Password must be at least 8 characters."
    if pw != confirm:
        return "Passwords do not match."
    return ""

def user_exists(email: str) -> bool:
    return email.lower() in st.session_state.users

def create_user(profile: Dict[str, Any]) -> None:
    profile["first_login"] = True
    st.session_state.users[profile["email"].lower()] = profile

def auth_user(email: str, password: str) -> bool:
    u = st.session_state.users.get(email.lower())
    if not u:
        return False
    if u.get("password") == password:
        st.session_state.current_user = email.lower()
        return True
    return False

def nav_to(page: str):
    st.session_state.page = page

# -----------------------------
# UI Sections
# -----------------------------
def hero_section():
    st.markdown(f"""
        <div class="hero" style="text-align:center; margin-top: 6vh; margin-bottom: 2vh;">
            <h1 style="font-size:2.5rem; color:white; font-weight:700;">{APP_TITLE}</h1>
        </div>
    """, unsafe_allow_html=True)

def account_dropdown():
    user = st.session_state.users.get(st.session_state.current_user, {})
    with st.sidebar.expander("👤 Account"):
        st.write(f"**Name:** {user.get('first','')} {user.get('last','')}")
        st.write(f"**Email:** {user.get('email','')}")
        
        # Fixed width buttons (2.5cm)
        st.markdown("""
            <style>
            div[data-testid="stExpander"] button[kind="secondary"] {
                width: 2.5cm !important;
                max-width: 2.5cm !important;
                min-width: 2.5cm !important;
                height: 32px !important;
                padding: 4px 8px !important;
                font-size: 12px !important;
                margin: 2px 0 !important;
                border-radius: 6px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("Help", key="help_btn", type="secondary"):
            st.info("Contact support@financechat.com for assistance.")
        if st.button("Logout", key="logout_btn", type="secondary"):
            st.session_state.current_user = None
            nav_to("login")

def login_card():
    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if not email_valid(email):
                st.error("Please enter a valid email.")
            elif not auth_user(email, password):
                st.error("Invalid email or password.")
            else:
                user = st.session_state.users[email.lower()]
                if user.get("first_login", True):
                    nav_to("predefined_questions")
                else:
                    nav_to("dashboard")

        # Add buttons for additional options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Forgot Password?", type="secondary"):
                nav_to("forgot_password")
        with col2:
            if st.button("Sign Up", type="secondary"):
                nav_to("signup")
        
        st.markdown("</div>", unsafe_allow_html=True)

def signup_card():
    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Create Account")

        with st.form("signup_form"):
            fcol, lcol = st.columns(2)
            with fcol:
                first = st.text_input("First Name")
            with lcol:
                last = st.text_input("Last Name")

            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")

            role = st.selectbox("Select Role", ["Role", "Student", "Professional"], index=0)

            extra: Dict[str, Any] = {}
            if role == "Student":
                extra["core"] = st.text_input("Enter Core")
            elif role == "Professional":
                extra["industry"] = st.text_input("Enter Industry Name")

            create = st.form_submit_button("Create Account", use_container_width=True)

        if create:
            if not first or not last:
                st.error("Please enter your first and last name.")
            elif not email_valid(email):
                st.error("Please enter a valid email address.")
            elif role == "Role":
                st.error("Please select a role.")
            elif role == "Student" and not extra.get("core"):
                st.error("Please enter your Core.")
            elif role == "Professional" and not extra.get("industry"):
                st.error("Please enter your Industry Name.")
            else:
                msg = passwords_ok(pw, confirm)
                if msg:
                    st.error(msg)
                elif user_exists(email):
                    st.error("An account with this email already exists.")
                else:
                    profile = {
                        "first": first.strip(),
                        "last": last.strip(),
                        "email": email.strip(),
                        "password": pw,
                        "role": role,
                        **extra,
                    }
                    create_user(profile)
                    st.success("Account created! You can log in now.")
                    nav_to("login")

        if st.button("⬅ Back to Login"):
            nav_to("login")
        st.markdown("</div>", unsafe_allow_html=True)

def forgot_password_card():
    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Forgot Password")
        with st.form("forgot_form"):
            email = st.text_input("Enter your registered Email")
            submitted = st.form_submit_button("Submit", use_container_width=True)
        if submitted:
            if not email_valid(email):
                st.error("Please enter a valid email address.")
            elif not user_exists(email):
                st.error("No account found with this email.")
            else:
                st.success("Password reset instructions have been sent to your email.")
        if st.button("Back to Login", type="secondary"):
            nav_to("login")
        st.markdown("</div>", unsafe_allow_html=True)

def predefined_questions_page():
    user = st.session_state.users.get(st.session_state.current_user, {})
    role = user.get("role", "")

    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Predefined Questions")
        st.write(f"Role: **{role}**")

        purpose = st.text_input("What is the purpose you want to save for?")
        target = st.number_input("Target Amount to Save:", min_value=0.0, step=50.0)

        if role == "Student":
            pocket = st.number_input("What is your Daily Pocket Money?", min_value=0.0, step=10.0)
            spending = st.number_input("Your Daily Spending:", min_value=0.0, step=10.0)
            if st.button("Submit"):
                st.session_state.budget_data = {
                    "role": "Student",
                    "pocket": pocket,
                    "spending": spending,
                    "purpose": purpose,
                    "target": target,
                    "saved": 0.0
                }
                user["first_login"] = False
                st.success("Data saved! Redirecting to dashboard...")
                nav_to("dashboard")
                st.rerun()

        elif role == "Professional":
            salary = st.number_input("Monthly Salary:", min_value=0.0, step=100.0)
            spending = st.number_input("Daily Spending:", min_value=0.0, step=10.0)
            if st.button("Submit"):
                st.session_state.budget_data = {
                    "role": "Professional",
                    "salary": salary,
                    "spending": spending,
                    "purpose": purpose,
                    "target": target,
                    "saved": 0.0
                }
                user["first_login"] = False
                st.success("Data saved! Redirecting to dashboard...")
                nav_to("dashboard")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Dashboard and Pages
# -----------------------------
def dashboard_page():
    # Check if user completed first login
    user = st.session_state.users.get(st.session_state.current_user, {})
    if user.get("first_login", True):
        nav_to("predefined_questions")
        st.rerun()
        return

    account_dropdown()

    st.markdown("""
    <style>
    .dashboard-buttons {display: flex; flex-direction: column; align-items: center; margin-top: 20px;}
    .stButton>button {width: 280px; margin: 12px 0; padding: 16px; font-size: 20px; font-weight: 600; color: white !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 12px; cursor: pointer;}
    .stButton>button:hover {transform: scale(1.07); background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="dashboard-buttons">', unsafe_allow_html=True)
    if st.button("💬 ProfitMate AI"):
        nav_to("finance_chatbot")
    if st.button("🌱 EcoTally"):
        nav_to("ecotally")
    if st.button("📊 Budget Summary"):
        nav_to("budget_summary")
    st.markdown('</div>', unsafe_allow_html=True)

def ecotally_page():
    user = st.session_state.users.get(st.session_state.current_user, {})
    role = user.get("role", "")
    
    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("🌱 EcoTally")

        if role == "Student":
            pocket = st.number_input("Daily Pocket Money:", min_value=0.0, step=10.0)
            spending = st.number_input("Daily Spending:", min_value=0.0, step=10.0)
            remaining = pocket - spending
            st.write(f"**Daily Remaining Balance:** {remaining:.2f}")
            
            monthly_remaining = remaining * 30
            st.write(f"**Monthly Projection:** {monthly_remaining:.2f}")
            
            if remaining > 0:
                st.success(f"Daily Profit: {remaining:.2f}")
            elif remaining < 0:
                st.error(f"Daily Loss: {-remaining:.2f}")
            else:
                st.info("No Profit, No Loss")
                
        else:  # Professional
            salary = st.number_input("Monthly Salary:", min_value=0.0, step=100.0)
            spending = st.number_input("Daily Spending:", min_value=0.0, step=10.0)
            
            monthly_spending = spending * 30
            remaining = salary - monthly_spending
            st.write(f"**Monthly Remaining Balance:** {remaining:.2f}")
            
            if remaining > 0:
                st.success(f"Monthly Profit: {remaining:.2f}")
            elif remaining < 0:
                st.error(f"Monthly Loss: {-remaining:.2f}")
            else:
                st.info("No Profit, No Loss")

        if st.button("⬅ Back to Dashboard"):
            nav_to("dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

def budget_summary_page():
    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📊 Budget Summary")

        data = st.session_state.budget_data
        if data:
            st.write(f"**Purpose:** {data.get('purpose','')}")
            st.write(f"**Target Amount:** ₹{data.get('target',0):,.2f}")
            st.write(f"**Amount Saved:** ₹{data.get('saved', 0):,.2f}")

            daily_savings = 0
            if data.get("role") == "Student":
                daily_savings = data.get("pocket", 0) - data.get("spending", 0)
                st.write(f"**Daily Pocket Money:** ₹{data.get('pocket', 0):.2f}")
                st.write(f"**Daily Spending:** ₹{data.get('spending', 0):.2f}")
                st.write(f"**Daily Savings:** ₹{daily_savings:.2f}")
            elif data.get("role") == "Professional":
                monthly_salary = data.get("salary", 0)
                daily_spending = data.get("spending", 0)
                daily_income = monthly_salary / 30
                daily_savings = daily_income - daily_spending
                st.write(f"**Monthly Salary:** ₹{monthly_salary:,.2f}")
                st.write(f"**Daily Income:** ₹{daily_income:.2f}")
                st.write(f"**Daily Spending:** ₹{daily_spending:.2f}")
                st.write(f"**Daily Savings:** ₹{daily_savings:.2f}")

            # Calculate days to achieve target
            remaining_amount = data.get("target", 0) - data.get("saved", 0)
            
            if daily_savings > 0:
                days_needed = remaining_amount / daily_savings
                if days_needed <= 0:
                    st.success(f"🎉 Congratulations! Goal of ₹{data['target']:,.2f} for {data['purpose']} achieved!")
                else:
                    st.info(f"⏳ You need approximately **{int(days_needed)} days** ({int(days_needed/30)} months and {int(days_needed%30)} days) to reach your goal.")
                    
                    # Show progress bar
                    progress = min(data.get("saved", 0) / data.get("target", 1), 1.0)
                    st.progress(progress)
                    st.write(f"**Progress:** {progress*100:.1f}% complete")
            else:
                st.error("⚠️ Your spending is higher than or equal to your income. You cannot save with current spending habits.")
                st.write("💡 **Suggestion:** Reduce daily spending to start saving towards your goal.")
        else:
            st.info("No budget data available. Please complete the Predefined Questions first.")
            if st.button("Go to Predefined Questions"):
                nav_to("predefined_questions")

        if st.button("⬅ Back to Dashboard"):
            nav_to("dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

def finance_chatbot_page():
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("💬 ProfitMate AI - Your Finance Assistant")
    
    user = st.session_state.users.get(st.session_state.current_user, {})
    st.write(f"**Welcome, {user.get('first','User')}!**")
    
    # Initialize chatbot if first visit
    if not st.session_state.chatbot_history:
        st.session_state.chatbot_history, st.session_state.chatbot_state = simple_finance_bot("", [], st.session_state.chatbot_state)
    
    # Display chat history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for sender, message in st.session_state.chatbot_history:
        if sender == "user":
            st.markdown(f'<div class="chat-message user-message">{message}</div>', unsafe_allow_html=True)
        else:
            # Replace newlines with <br> for proper display
            formatted_message = message.replace('\n', '<br>')
            st.markdown(f'<div class="chat-message bot-message">{formatted_message}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message here...", key="chat_input")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            send_button = st.form_submit_button("Send", use_container_width=True)
        with col2:
            reset_button = st.form_submit_button("Reset Chat", use_container_width=True)
        with col3:
            back_button = st.form_submit_button("⬅ Back", use_container_width=True)
    
    if send_button and user_input:
        st.session_state.chatbot_history, st.session_state.chatbot_state = simple_finance_bot(
            user_input, 
            st.session_state.chatbot_history, 
            st.session_state.chatbot_state
        )
        st.rerun()
    
    if reset_button:
        st.session_state.chatbot_history = []
        st.session_state.chatbot_state = {"step":0, "mode":None, "idea":None, "budget":None, 
                                         "deposit":None, "years":None, "senior":None, 
                                         "salary":None, "spending":None}
        st.session_state.chatbot_history, st.session_state.chatbot_state = simple_finance_bot("", [], st.session_state.chatbot_state)
        st.rerun()
    
    if back_button:
        nav_to("dashboard")
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# App Layout
# -----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="💬", layout="centered")
set_background()
hero_section()

st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
col = st.columns([1, 3, 1])[1]
with col:
    if st.session_state.page == "login":
        login_card()
    elif st.session_state.page == "signup":
        signup_card()
    elif st.session_state.page == "forgot_password":
        forgot_password_card()
    elif st.session_state.page == "predefined_questions":
        predefined_questions_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "ecotally":
        ecotally_page()
    elif st.session_state.page == "budget_summary":
        budget_summary_page()
    elif st.session_state.page == "finance_chatbot":
        finance_chatbot_page()
st.markdown("</div>", unsafe_allow_html=True)