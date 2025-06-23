import streamlit as st
import requests
import json

# Firebase Web API Key
API_KEY = "AIzaSyBZTahQjGw8Hurd1X1lnxghySR4MAl9aC0"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

# Firebase login function
def login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(FIREBASE_SIGNIN_URL, data=json.dumps(payload))
    return response

# --- UI Logic ---

# Dashboard if already logged in
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    st.title("📘 Notes Dashboard")
    st.write(f"Welcome, {st.session_state['user']} 👋")
    st.success("You're logged in!")
    # You can add upload/view buttons here
    st.stop()  # prevent login form from showing

# Login Page
st.title("🔥 College Notes Hub - Login")
email = st.text_input("Login Email")  # changed label to avoid duplicate ID
password = st.text_input("Login Password", type="password")  # changed label

if st.button("Login"):
    res = login(email, password)
    if res.status_code == 200:
        data = res.json()
        st.session_state['logged_in'] = True
        st.session_state['user'] = data['email']
        st.rerun()
    else:
        st.error("❌ Invalid email or password")
