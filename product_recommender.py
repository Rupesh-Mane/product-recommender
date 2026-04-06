import streamlit as st
import pandas as pd
import sqlite3
import base64
import random
import smtplib
from email.mime.text import MIMEText
from PIL import Image


# ---------------- UTILITY FUNCTION ---------------- #
import base64

def get_base64(path):
    """Convert an image file to base64 string"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------- EMAIL CONFIG ---------------- #
import os
SENDER_EMAIL = os.getenv("EMAIL")  # your Gmail
SENDER_PASSWORD = os.getenv("PASSWORD")    # 16-character App Password (no spaces)

# ---------------- SESSION STATE ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False

# ---------------- DATABASE ---------------- #
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    mobile TEXT,
    password TEXT,
    verified INTEGER DEFAULT 0
)
""")
conn.commit()

# ---------------- DATABASE FUNCTIONS ---------------- #
def add_user(username, email, mobile, password):
    cursor.execute(
        "INSERT INTO users(username,email,mobile,password,verified) VALUES(?,?,?,?,0)",
        (username, email, mobile, password)
    )
    conn.commit()

def verify_user(email):
    cursor.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
    conn.commit()

def login_user(email, password):
    cursor.execute(
        "SELECT username FROM users WHERE email=? AND password=? AND verified=1",
        (email, password)
    )
    return cursor.fetchone()

def user_exists(email):
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    return cursor.fetchone()








# ---------------- OTP FUNCTION ---------------- #
def send_otp(email):
    otp = str(random.randint(100000, 999999))
    st.session_state.otp = otp

    msg = MIMEText(f"Your OTP for Digital Shopping Store is: {otp}")
    msg['Subject'] = "OTP Verification"
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False








# ---------------- LOGIN / REGISTER UI ---------------- #
if not st.session_state.logged_in:

    # Login background image
    login_bg = get_base64("images/login_bg.jpg")
    login_bg1 = get_base64("images/product.jpg")

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                          url("data:image/jpg;base64,{login_bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        margin-top:-57px;
    }}
    # .login-box {{
    #     max-width:420px;
    #     margin:auto;
    #     margin-top:80px;
    #     padding:35px;
    #     border-radius:20px;
    #     text-align:center;
    #     color:white;
    #     background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
    #                       url("data:image/jpg;base64,{login_bg1}");
    #     # background: rgba(0,0,0,0.5);  /* overlay for readability */
    #      background-size: cover;
    #     background-position: center;
    #     box-shadow: 0 20px 40px rgba(0,0,0,0.7);
    # }}
    .warning {{color:#ff6b6b; font-size:13px;}}
    </style>
    """, unsafe_allow_html=True)


    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🛍 Digital ShoppingKart")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ----- LOGIN ----- #
    with tab1:
        email_login = st.text_input("Email", key="login_email")
        password_login = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            user = login_user(email_login, password_login)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.rerun()
            else:
                st.error("Invalid credentials or account not verified")

    # ----- REGISTER ----- #
    with tab2:
        username = st.text_input("Username", key="register_username")
        reg_email = st.text_input("Email", key="register_email")
        mobile = st.text_input("Mobile Number", key="register_mobile")
        reg_pass = st.text_input("Password", type="password", key="register_password")

        # Live validation
        if username and (not username.isalpha() or len(username)<8):
            st.warning("Username must be letters & 8+ characters", icon="⚠️")
        if reg_pass and (not reg_pass.isdigit() or len(reg_pass)<5):
            st.warning("Password must be numbers & 5+ digits", icon="⚠️")
        if mobile and (not mobile.isdigit() or len(mobile)!=10):
            st.warning("Enter valid 10-digit mobile number", icon="⚠️")

        if st.button("Send OTP", key="send_otp"):
            if user_exists(reg_email):
                st.warning("User already exists")
            else:
                if send_otp(reg_email):
                    st.session_state.otp_sent = True
                    st.success("OTP sent to your email")

        if st.session_state.otp_sent:
            otp_input = st.text_input("Enter OTP", key="otp_input")
            if st.button("Verify & Register", key="verify_register"):
                if otp_input == st.session_state.otp:
                    add_user(username, reg_email, mobile, reg_pass)
                    verify_user(reg_email)
                    st.success("Account created successfully!")
                    st.session_state.otp_sent = False
                else:
                    st.error("Invalid OTP")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- STREAMLIT CONFIG ---------------- #
st.set_page_config(page_title="Digital Product Recommender", layout="wide")

# ---------------- HEADER ---------------- #
st.markdown("""
<style>
.header {
    background-color: #4facfe;
    padding: 15px;
    border-radius: 12px;
    color: white;
    font-size: 24px;
    text-align:center;
    font-weight:700;
}
</style>
<div class="header">🛒 Digital Product Recommendation System</div>
""", unsafe_allow_html=True)

# ---------------- USER BAR ---------------- #
top1, top2 = st.columns([6,1])
with top1:
    st.markdown("### 👋 Welcome to Digital ShoppingKart")
with top2:
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.rerun()
st.markdown(f"**Logged in as:** {st.session_state.username}")




# ---------------- BACKGROUND ---------------- #
# ---------------- BACKGROUND ---------------- #
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

b1 = get_base64("images/bgslide1.jpg")
b2 = get_base64("images/bobby1.jpg")
b3 = get_base64("images/bgslide2.jpg")
b4 = get_base64("images/bgslide3.jpg")
b5 = get_base64("images/bgslide4.jpg")
b6 = get_base64("images/bobby5.jpg")

st.markdown(f"""
<style>
@keyframes bgSlide {{
0%   {{ background-image:url("data:image/jpg;base64,{b1}") }}
16%  {{ background-image:url("data:image/jpg;base64,{b2}") }}
33%  {{ background-image:url("data:image/jpg;base64,{b3}") }}
50%  {{ background-image:url("data:image/jpg;base64,{b4}") }}
66%  {{ background-image:url("data:image/jpg;base64,{b5}") }}
83%  {{ background-image:url("data:image/jpg;base64,{b6}") }}
100% {{ background-image:url("data:image/jpg;base64,{b1}") }}
}}
.stApp {{
animation: bgSlide 30s infinite;
background-size:cover;
background-position:center;
}}
</style>
""", unsafe_allow_html=True)


# ---------------- PRODUCT DATA ---------------- #
products = pd.DataFrame({
    "product_id":[1,2,3,4,5,6,7,8,9,10],
    "product_name":["iPhone","Samsung Galaxy","Google Pixel","OnePlus","MacBook","Dell Laptop","HP Laptop","Apple Watch","AirPods","iPad"],
    "category":["mobile","mobile","mobile","mobile","laptop","laptop","laptop","watch","audio","tablet"],
    "image":["images/iphone.jpg","images/samsung.jpg","images/pixel.jpg","images/oneplus.jpg","images/macbook.jpg","images/dell.jpg","images/hp.jpg","images/watch.jpg","images/buds.jpg","images/ipad.jpg"]
})

ratings = pd.DataFrame({
    "user_id":[1,2,2,3,3,4],
    "product_id":[1,1,8,2,9,5],
    "rating":[5,5,5,4,4,5]
})

# ---------------- HELPER FUNCTIONS ---------------- #
def get_rating(pid):
    r = ratings[ratings["product_id"]==pid]["rating"]
    if len(r)==0:
        return "⭐⭐⭐⭐☆"
    avg = round(r.mean())
    return "⭐"*avg + "☆"*(5-avg)

def content_recommend(product_name):
    category = products[products["product_name"]==product_name]["category"].values[0]
    similar = products[products["category"]==category]["product_id"].tolist()
    return similar

def collaborative_recommend(user_id, searched_pid):
    users = ratings[ratings["product_id"]==searched_pid]["user_id"].tolist()
    similar_users = [u for u in users if u != user_id]
    rec_products = ratings[ratings["user_id"].isin(similar_users)]["product_id"].tolist()
    rec_products = list(set(rec_products))
    rec_products = [p for p in rec_products if p != searched_pid]
    return rec_products

def hybrid_recommend(user_id, product_name):
    pid = products[products["product_name"]==product_name]["product_id"].values[0]
    collab = collaborative_recommend(user_id, pid)
    content = content_recommend(product_name)
    final = collab + [p for p in content if p not in collab and p != pid]
    return final

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ---------------- SEARCH ---------------- #
search_product = st.text_input("🔍 Search Product", key="search_product")

if search_product:
    search_term = search_product.lower()
    searched_row = products[
        products["product_name"].str.lower().str.contains(search_term) |
        products["category"].str.lower().str.contains(search_term)
    ]

    if searched_row.empty:
        st.error("❌ Product not found")
    else:
        row = searched_row.iloc[0]

        st.markdown("## 🎯 You searched for")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            img_b64 = img_to_base64(row["image"])
            st.markdown(f'''
            <div style="background: rgba(255,255,255,0.18); backdrop-filter: blur(20px); border-radius: 22px; padding: 16px; text-align:center; color:white;">
                <img src="data:image/jpeg;base64,{img_b64}" width="300" style="border-radius:20px; margin-bottom:15px;"/>
                <div style="font-size:22px; font-weight:700;">{row["product_name"]}</div>
                <div style="font-size:16px; color:#f5c518; margin-top:5px;">{get_rating(row['product_id'])}</div>
                <div style="font-size:14px; color:#9aa4b2; margin-top:5px;">{row["category"].upper()}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("## ✨ Recommended for you")
        rec_ids = hybrid_recommend(1, row["product_name"])
        rec_products = products[products["product_id"].isin(rec_ids)]

        st.markdown('<div style="display:flex; overflow-x:auto; gap:20px; padding-bottom:20px;">', unsafe_allow_html=True)
        for r in rec_products.itertuples():
            img_b64 = img_to_base64(r.image)
            st.markdown(f'''
            <div style="background: rgba(255,255,255,0.18); backdrop-filter: blur(20px); border-radius: 22px; padding: 10px; text-align:center; color:white; min-width:180px;">
                <img src="data:image/jpeg;base64,{img_b64}" width="160" style="border-radius:16px; margin-bottom:8px;"/>
                <div style="font-size:18px; font-weight:600;">{r.product_name}</div>
                <div style="font-size:13px; color:#9aa4b2;">{r.category.upper()}</div>
                <div style="font-size:14px; color:#f5c518;">{get_rating(r.product_id)}</div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

