import streamlit as st
from database import conn, cred_table
from sqlalchemy import text
import random

if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "paircode" not in st.session_state:
    st.session_state.paircode = None

if "changes" not in st.session_state:
    st.session_state.changes = 0

def login_page():
    _, col, _ = st.columns([1, 8, 1])
    
    with col:
        st.markdown("<h1 style='text-align: center;'>🔐 Welcome Back</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Transaction Management System</p>", unsafe_allow_html=True)
        st.write("")
        
        with st.container(border=True):
            with st.form("login_form"):
                st.markdown("### Sign In")
                username = st.text_input("Username 👤", max_chars=20, placeholder="Enter your username")
                password = st.text_input("Password 🔑", type="password", max_chars=20, placeholder="Enter your password")
                
                # We defer database checking until submit to avoid unnecessary queries on load
                submit = st.form_submit_button("Login ➡️", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.warning("Please enter both username and password.")
                    else:
                        users = conn.query("SELECT username FROM credentials", ttl=0)["username"].tolist()
                        passwd = conn.query(f"SELECT password, paircode FROM credentials WHERE username = '{username}'", ttl=0)
                        
                        if passwd.empty:
                            st.error("Username does not exist ❌")
                        elif password != passwd.iloc[0]["password"]:
                            st.error("Invalid Password ❌")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.current_user = username
                            st.session_state.paircode = passwd.iloc[0]["paircode"]
                            st.session_state.page = "dashboard"
                            st.rerun()
                            
            st.divider()
            st.write("Don't have an account?")
            if st.button("📝 Create an Account", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()

def signup_page():
    _, col, _ = st.columns([1, 8, 1])
    
    with col:
        st.markdown("<h1 style='text-align: center;'>✨ Join Us</h1>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; color: gray;'>Start splitting and tracking expenses today</p>", unsafe_allow_html=True)
        st.write("")
        
        with st.container(border=True):
            with st.form("signup_form"):
                st.markdown("### Create New Account")
                username = st.text_input("Choose Username 👤", max_chars=20, placeholder="e.g. hravis_tead")
                password = st.text_input("Choose Password 🔑", type="password", max_chars=20, placeholder="e.g. 19November2023")
                
                submit = st.form_submit_button("Sign Up ✅", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.warning("Please fill out all fields.")
                    else:
                        users = conn.query("SELECT username FROM credentials", ttl=0)["username"].tolist()
                        paircode = random.randint(1000, 9999)
                        existing_paircodes = conn.query("SELECT paircode FROM credentials", ttl=0)["paircode"].tolist()
                        
                        if username in users:
                            st.error("Username already exists. Please choose a different one. ⚠️")
                        else:
                            while paircode in existing_paircodes:
                                paircode = random.randint(1000, 9999)
                            with conn.session as s:
                                cursor = cred_table.insert().values(
                                    username=username,
                                    password=password,
                                    paircode=paircode
                                )
                                s.execute(cursor)
                                s.commit()

                            st.balloons()
                            st.success(f"Account created successfully! 🎉")
                            st.info(f"Your Paircode is: **{paircode}**. Ask friends to use this code to connect with you.")
            
            st.divider()
            if st.button("⬅️ Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()    

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "login"
    st.session_state.changes = 0
    t.session_state.paircode = None
    st.rerun()
