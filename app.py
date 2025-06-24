import streamlit as st
import pyrebase

# --- Firebase Config ---
firebaseConfig = {
    "apiKey": "AIzaSyBZTahQjGw8Hurd1X1lnxghySR4MAl9aC0",
    "authDomain": "college-notes-hub-4416d.firebaseapp.com",
    "projectId": "college-notes-hub-4416d",
    "storageBucket": "college-notes-hub-4416d.appspot.com",
    "messagingSenderId": "56762847769",
    "appId": "1:56762847769:web:0b43c88570ef3aff125088",
    "measurementId": "G-1186C2E2CY"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# --- Session Management ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "paid" not in st.session_state:
    st.session_state.paid = False

# --- Notes Page ---
def notes_page():
    st.title("📚 Welcome to College Notes Hub")
    st.write(f"✅ Logged in as: `{st.session_state.user_email}`")

    if not st.session_state.paid:
        st.warning("🔒 You need to pay ₹199 to access notes.")
        if st.button("💳 Pay ₹199 (Fake Payment)"):
            st.success("✅ Payment successful! Access granted.")
            st.session_state.paid = True
        return

    st.success("🎉 You have full access to notes!")

    # Example content — replace with your CSV logic
    st.markdown("### 📥 Download Notes")
    st.write("- BCA Semester 1 - [Download PDF](https://example.com/notes1)")
    st.write("- BBA Semester 2 - [Download PDF](https://example.com/notes2)")

    if st.button("🚪 Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# --- Login/Signup Page ---
def login_page():
    st.title("🔐 College Notes Hub - Login/Signup")

    choice = st.selectbox("Login or Signup", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("Login successful!")
                st.experimental_rerun()
            except:
                st.error("Invalid email or password.")

    else:
        if st.button("Sign Up"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Account created successfully! Please login.")
            except:
                st.error("Signup failed. Try again with a different email.")

# --- Main App ---
if st.session_state.logged_in:
    notes_page()
else:
    login_page()