import streamlit as st
import requests
import json

# Firebase Web API Key
API_KEY = "AIzaSyBZTahQjGw8Hurd1X1lnxghySR4MAl9aC0"

# Firebase login endpoint
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

def login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(FIREBASE_SIGNIN_URL, data=json.dumps(payload))
    return response

# UI
st.title("🔥 College Notes Hub - Login")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    res = login(email, password)
    if res.status_code == 200:
        st.success("✅ Login Successful!")
        st.json(res.json())
    else:
        st.error("❌ Invalid email or password")
        st.code(res.text)



