import streamlit as st
import pandas as pd
from datetime import date
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Mumbai Realty", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 15px;
    background: white;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    margin-bottom: 15px;
}
.price {
    font-size: 20px;
    font-weight: bold;
    color: #0a8f5a;
}
.header {
    font-size: 28px;
    font-weight: bold;
}
.small {
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILE STORAGE ----------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------------- SESSION INIT ----------------
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Type","Location","Start","End","Rent","Deposit",
        "Commission","Agents","PerAgent","Owner"
    ])

# ✅ ALLOWED USERS LIST (EDIT THIS)
ALLOWED_USERS = [
    "agent1@gmail.com",
    "agent2@gmail.com",
    "surajfrom21987@gmail.com"
]

# ---------------- LOGIN SYSTEM ----------------
def login():
    st.title("🏙 Om Sai Estate Agents")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # LOGIN
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.user = email
                st.success("✅ Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # SIGNUP (RESTRICTED)
    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if new_email not in ALLOWED_USERS:
                st.error("❌ Access Denied. Contact Admin")
            elif new_email in st.session_state.users:
                st.warning("User already exists")
            else:
                st.session_state.users[new_email] = new_password
                save_users(st.session_state.users)
                st.success("✅ Account created")

# ---------------- MAIN APP ----------------
def app():

    col1, col2 = st.columns([6,1])
    col1.markdown('<div class="header">🏠 Om Sai Estate Agents Dashboard</div>', unsafe_allow_html=True)

    if col2.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # SIDEBAR INPUT
    st.sidebar.header("➕ Add Property")

    ptype = st.sidebar.selectbox("Property Type", ["1RK","1BHK","2BHK","3BHK"])
    location = st.sidebar.text_input("Location (Andheri, Bandra, etc.)")
    start = st.sidebar.date_input("Start Date", date.today())
    end = st.sidebar.date_input("End Date", date.today())

    rent = st.sidebar.number_input("Monthly Rent ₹", 0)
    deposit = st.sidebar.number_input("Deposit ₹", 0)
    commission = st.sidebar.number_input("Commission ₹", 0)
    agents = st.sidebar.number_input("Total Agents", min_value=1)

    if st.sidebar.button("Add Property"):
        per_agent = commission / agents

        new = pd.DataFrame([[
            ptype, location, start, end, rent, deposit,
            commission, agents, per_agent,
            st.session_state.user
        ]], columns=st.session_state.data.columns)

        st.session_state.data = pd.concat([st.session_state.data, new], ignore_index=True)
        st.sidebar.success("✅ Property Added")

    # FILTER USER DATA
    df = st.session_state.data
    df = df[df["Owner"] == st.session_state.user]

    if df.empty:
        st.info("No properties added yet")
        return

    # SUMMARY
    st.subheader("📊 Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rent", f"₹{df['Rent'].sum():,}")
    c2.metric("Total Deposit", f"₹{df['Deposit'].sum():,}")
    c3.metric("Total Commission", f"₹{df['Commission'].sum():,}")

    # LISTINGS
    st.subheader("🏘 Listings")

    cols = st.columns(2)

    for i, row in df.iterrows():
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <b>{row['Type']} in {row['Location']}</b>
                <div class="price">₹{int(row['Rent']):,} / month</div>
                <div class="small">📅 {row['Start']} → {row['End']}</div>
                <div class="small">Deposit: ₹{int(row['Deposit']):,}</div>
                <hr>
                <div>Commission: ₹{int(row['Commission']):,}</div>
                <div>Agents: {int(row['Agents'])}</div>
                <div>Per Agent: ₹{int(row['PerAgent']):,}</div>
            </div>
            """, unsafe_allow_html=True)

    # SEARCH
    st.subheader("🔍 Search")

    search = st.text_input("Search by location")

    if search:
        filtered = df[df["Location"].str.contains(search, case=False)]
    else:
        filtered = df

    st.dataframe(filtered, use_container_width=True)

    # DOWNLOAD
    csv = filtered.to_csv(index=False)
    st.download_button("⬇ Download Data", csv, "properties.csv")

    # INSIGHTS
    st.subheader("💡 Insights")
    st.write(f"Average Rent: ₹{round(df['Rent'].mean(),2)}")
    st.write(f"Avg Commission per Agent: ₹{round(df['PerAgent'].mean(),2)}")

    st.markdown("---")
    st.caption("📱 Private Mumbai Real Estate App for Agents")

# ---------------- ROUTER ----------------
if not st.session_state.logged_in:
    login()
else:
    app()