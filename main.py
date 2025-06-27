import streamlit as st
import requests
import json
import os
import razorpay
import firebase_admin
import datetime
import random
import uuid
import smtplib
import ssl
from email.message import EmailMessage
from firebase_admin import credentials, db

# Firebase init
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": st.secrets["firebase"]["universe_domain"]
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://college-notes-hub-4416d-default-rtdb.firebaseio.com/"
    })

# Razorpay config
razorpay_client = razorpay.Client(auth=("rzp_test_OJt4GWY0dnYC7l", "6JKAlW283xDqs6rg7aTtKz07"))

# Firebase Auth API
API_KEY = "AIzaSyBZTahQjGw8Hurd1X1lnxghySR4MAl9aC0"
SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"

# Helper functions
def email_key(email):
    return email.replace(".", "_").replace("@", "_at_")

def is_user_paid(email):
    ref = db.reference(f"users/{email_key(email)}")
    data = ref.get()
    return data and data.get("is_paid") == True

def mark_user_paid(email):
    ref = db.reference(f"users/{email_key(email)}")
    ref.set({"is_paid": True})

def get_stats():
    users = db.reference("users").get() or {}
    total = len(users)
    paid = sum(1 for v in users.values() if v.get("is_paid"))
    notes = sum(len(filenames) for _, _, filenames in os.walk("uploaded_notes"))
    return total, paid, notes

def login(email, password):
    return requests.post(SIGNIN_URL, data=json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    }))

def signup(email, password):
    return requests.post(SIGNUP_URL, data=json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    }))

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    db.reference(f"users/{email_key(email)}/otp").set(otp)
    msg = EmailMessage()
    msg['Subject'] = "Your OTP for Notes Hub Login"
    msg['From'] = st.secrets["email"]["sender"]
    msg['To'] = email
    msg.set_content(f"Your OTP is: {otp}\n\nDo not share this with anyone.")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(st.secrets["email"]["sender"], st.secrets["email"]["password"])
        server.send_message(msg)
    return otp

def verify_otp(email, input_otp):
    real = db.reference(f"users/{email_key(email)}/otp").get()
    return str(input_otp) == str(real)

def update_session(email):
    sid = str(uuid.uuid4())
    db.reference(f"users/{email_key(email)}/session_id").set(sid)
    return sid

def is_same_session(email, current_id):
    saved = db.reference(f"users/{email_key(email)}/session_id").get()
    return saved == current_id

# Session init
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'paid' not in st.session_state:
    st.session_state['paid'] = False

# Auth
if not st.session_state['logged_in']:
    st.title("🔥Goenkan's Notes Hub")
    tabs = st.tabs(["🔐 Login", "📝 Signup"])

    with tabs[0]:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("✅ Login"):
            res = login(email, password)
            if res.status_code == 200:
                send_otp(email)
                otp = st.text_input("📩 Enter OTP", max_chars=6)
                if st.button("🔐 Verify OTP"):
                    if verify_otp(email, otp):
                        sid = update_session(email)
                        st.session_state['logged_in'] = True
                        st.session_state['user'] = email
                        st.session_state['session_id'] = sid
                        st.session_state['paid'] = is_user_paid(email)
                        st.success("🎉 Logged in successfully with OTP!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP")
            else:
                st.error("❌ Invalid email or password")

    with tabs[1]:
        email = st.text_input("New Email", key="signup_email")
        password = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("📝 Signup"):
            res = signup(email, password)
            if res.status_code == 200:
                st.success("✅ Signup successful! Please login.")
            elif "EMAIL_EXISTS" in res.text:
                st.warning("⚠️ Email already exists.")
            else:
                st.error("❌ Signup failed.")

# Session Verification
if st.session_state.get("logged_in") and not is_same_session(st.session_state['user'], st.session_state.get('session_id')):
    st.error("⚠️ You've been logged out because your account was accessed from another device.")
    st.session_state.clear()
    st.rerun()

# Place your existing show_dashboard() and show_payment() functions after this point
def show_dashboard():
    st.title("📘 Goenkan's Notes Dashboard")
    st.success(f"Welcome, {st.session_state['user']}")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state['user'] == "hardikaneja52@gmail.com":
        st.subheader("📊 Admin Stats")
        total, paid, notes = get_stats()
        st.info(f"👤 Total Users: {total}")
        st.info(f"💰 Paid Users: {paid}")
        st.info(f"📚 Notes Uploaded: {notes}")

        st.subheader("📤 Upload Notes")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        course = st.selectbox("Course", list(SEMESTERS_MAP.keys()))
        semester = st.selectbox("Semester", SEMESTERS_MAP[course])
        subject = st.text_input("Subject")

        if st.button("✅ Upload Notes"):
            if uploaded_file and subject:
                folder = f"uploaded_notes/{course}/{semester}"
                os.makedirs(folder, exist_ok=True)
                with open(os.path.join(folder, f"{subject}.pdf"), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("✅ Notes uploaded.")
            else:
                st.warning("⚠️ Please complete all fields.")

        st.subheader("📩 Notes Requests")
        requests_ref = db.reference("notes_requests").get() or {}
        if not requests_ref:
            st.info("🎉 No new requests.")
        else:
            for key, req in requests_ref.items():
                date = req.get("requested_on", "📆 Unknown date")
                with st.expander(f"📌 {req['course']} - {req['semester']} - {req['subject']} (📧 {req['email']})"):
                    st.write(f"🗓️ Requested On: {date}")
                    if st.button("✅ Mark as Fulfilled", key=key):
                        db.reference(f"notes_requests/{key}").delete()
                        st.success("Request removed!")
                        st.rerun()

    else:
        st.subheader("📚 Download Notes")
        course = st.selectbox("Course", list(SEMESTERS_MAP.keys()))
        semester = st.selectbox("Semester", SEMESTERS_MAP[course])
        folder = f"uploaded_notes/{course}/{semester}"
        if os.path.exists(folder):
            files = os.listdir(folder)
            search = st.text_input("🔍 Search by subject")
            found = False
            for file in files:
                if search.lower() in file.lower():
                    found = True
                    with open(os.path.join(folder, file), "rb") as f:
                        st.download_button(f"📥 Download {file.replace('.pdf','')}", f, file_name=file)
            if not found and search:
                st.error("❌ Notes not found.")
        else:
            st.info("📭 No notes found for this semester.")

        st.markdown("---")
        st.subheader("📩 Can't find your notes? Request here")
        course_req = st.selectbox("Request Course", list(SEMESTERS_MAP.keys()), key="req_course")
        sem_req = st.selectbox("Request Semester", SEMESTERS_MAP[course_req], key="req_sem")
        subject_req = st.text_input("Requested Subject", key="req_subject")
        if st.button("📨 Submit Request"):
            if subject_req.strip():
                now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                ref = db.reference("notes_requests")
                ref.push({
                    "email": st.session_state['user'],
                    "course": course_req,
                    "semester": sem_req,
                    "subject": subject_req,
                    "requested_on": now
                })
                st.success("🎉 Your request has been submitted!")
            else:
                st.warning("⚠️ Please enter subject name.")

# Show Payment
def show_payment():
    st.title("💳 ₹199 Payment for Full Access")
    order = razorpay_client.order.create({
        "amount": 19900,
        "currency": "INR",
        "payment_capture": 1
    })

    st.components.v1.html(f"""
        <form>
          <script src="https://checkout.razorpay.com/v1/checkout.js"
                  data-key="rzp_test_OJt4GWY0dnYC7l"
                  data-amount="19900"
                  data-currency="INR"
                  data-order_id="{order['id']}"
                  data-buttontext="Pay ₹199"
                  data-name="Goenkan's Notes Hub"
                  data-description="Unlock Notes"
                  data-prefill.name="User"
                  data-prefill.email="{st.session_state['user']}"
                  data-theme.color="#0a9396">
          </script>
        </form>
    """, height=300)

    st.warning("🕐 After payment, wait 30 seconds and then click below.")

    if st.button("✅ I have completed payment"):
        try:
            # 🔍 Fetch all Razorpay payments
            payments = razorpay_client.payment.fetch_all()
            for p in payments['items']:
                if p['email'] == st.session_state['user'] and p['status'] == 'captured':
                    mark_user_paid(st.session_state['user'])
                    st.session_state['paid'] = True
                    st.success("✅ Payment verified automatically!")
                    st.rerun()
                    return
            st.error("❌ Payment not found. Please wait a bit or contact admin.")
        except Exception as e:
            st.error(f"❌ Error verifying payment: {e}")




# Auth
def show_auth():
    st.title("🔥Goenkan's Notes Hub")
    tabs = st.tabs(["🔐 Login", "📝 Signup"])

    with tabs[0]:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.session_state.get('otp_pending'):
            otp_input = st.text_input("🔒 Enter OTP")
    if st.button("🔓 Verify OTP"):
        email = st.session_state['temp_user']
        if verify_otp(email, otp_input):
            if is_session_valid(email, st.session_state['session_id']):
                st.session_state['logged_in'] = True
                st.session_state['user'] = email
                st.session_state['paid'] = is_user_paid(email)
                st.success("✅ OTP verified. Login successful!")
                # Clean up temp states
                st.session_state.pop('otp_pending', None)
                st.session_state.pop('temp_user', None)
                st.rerun()
            else:
                st.error("⚠️ Session expired due to login from another device.")
        else:
            st.error("❌ Invalid OTP. Please try again.")


    with tabs[1]:
        email = st.text_input("New Email", key="signup_email")
        password = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("📝 Signup"):
            res = signup(email, password)
            if res.status_code == 200:
                st.success("✅ Signup done! Now login.")
            elif "EMAIL_EXISTS" in res.text:
                st.warning("⚠️ Email already exists.")
            else:
                st.error("❌ Signup failed.")


                st.markdown("---")
    st.subheader("📞 Contact Admin")
    st.info("✉️ Email: hardikaneja52@gmail.com")


# Main
if not st.session_state['logged_in']:
    show_auth()
elif st.session_state['user'] == "hardikaneja52@gmail.com":
    show_dashboard()  # ✅ Admin directly to dashboard
elif not st.session_state['paid']:
    show_payment()
else:
    show_dashboard()

