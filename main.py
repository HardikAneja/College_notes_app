import streamlit as st
import pyrebase as pyrebase
import pandas as pd
import os

# --- Firebase Config ---
firebaseConfig = {
    "apiKey": "AIzaSyBZTahQjGw8Hurd1X1lnxghySR4MAl9aC0",
    "authDomain": "college-notes-hub-4416d.firebaseapp.com",
    "projectId": "college-notes-hub-4416d",
    "storageBucket": "college-notes-hub-4416d.appspot.com",
    "messagingSenderId": "56762847769",
    "appId": "1:56762847769:web:0b43c88570ef3aff125088",
    "measurementId": "G-1186C2E2CY",
    "databaseURL": "https://college-notes-hub-4416d-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "paid" not in st.session_state:
    st.session_state.paid = False

# --- Admin Panel ---
def admin_panel():
    st.header("🛠️ Admin Panel - Add Notes")

    with st.form("admin_form"):
        course = st.text_input("Course (e.g., BCA, BBA)")
        semester = st.text_input("Semester (e.g., 1, 2, 3)")
        subject = st.text_input("Subject Name")
        unit = st.text_input("Unit No.")
        notes_link = st.text_input("Notes Link (Google Drive or PDF URL)")

        submitted = st.form_submit_button("➕ Add Note")
        if submitted:
            new_data = {
                "Course": course,
                "Semester": semester,
                "Subject": subject,
                "Unit": unit,
                "Notes_Link": notes_link
            }

            if os.path.exists("notes_content.csv"):
                df = pd.read_csv("notes_content.csv")
            else:
                df = pd.DataFrame(columns=["Course", "Semester", "Subject", "Unit", "Notes_Link"])

            df = df.append(new_data, ignore_index=True)
            df.to_csv("notes_content.csv", index=False)
            st.success("✅ Note added successfully!")

# --- Notes Page ---
def notes_page():
    st.title("📚 College Notes Hub")
    st.write(f"👋 Logged in as: `{st.session_state.user_email}`")

    if not st.session_state.paid:
        st.warning("🔒 Please pay ₹199 to unlock notes access.")
        if st.button("💳 Fake Pay ₹199"):
            st.session_state.paid = True
            st.success("✅ Payment successful! You can now access notes.")
        return

    st.success("✅ Notes Unlocked!")

    if os.path.exists("notes_content.csv"):
        df = pd.read_csv("notes_content.csv")

        if not df.empty:
            st.markdown("### 📚 Available Notes")
            for _, row in df.iterrows():
                st.markdown(f"- **{row['Course']} Sem-{row['Semester']} | {row['Subject']} | Unit {row['Unit']}**  → [🔗 Open Notes]({row['Notes_Link']})")
        else:
            st.info("No notes uploaded yet.")
    else:
        st.warning("⚠️ Notes file not found.")

    st.markdown("---")
    st.markdown("### 👨‍💻 Want to Upload Notes?")
    if st.button("Open Admin Panel"):
        admin_panel()

    if st.button("🚪 Logout"):
        for key in st.session_state.keys():
            st.session_state[key] = False if isinstance(st.session_state[key], bool) else ""
        st.experimental_rerun()

# --- Login / Signup Page ---
def login_page():
    st.title("🔐 College Notes Hub - Login/Signup")

    choice = st.selectbox("Login or Signup", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            try:
                auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("✅ Login successful!")
                st.experimental_rerun()
            except:
                st.error("❌ Login failed.")
    else:
        if st.button("Sign Up"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("✅ Account created! Please login.")
            except:
                st.error("❌ Signup failed.")

# --- Main App ---
if st.session_state.logged_in:
    notes_page()
else:
    login_page()


