import streamlit as st
from auth import login_page, signup_page, logout
from friends import friends_page
from view_trans import view_page
from add_trans import add_transaction_page
from pay_amount import pay_amount
from delete_trans import delete_trans_page
from database import conn
from sqlalchemy import text
from ui_styles import apply_custom_css

st.set_page_config(page_title="DASHBOARD - Transaction System", layout="wide")
apply_custom_css()

if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def dashboard_page():
    st.title("Dashboard")

    st.write(f"Welcome back, **{st.session_state.current_user}**! 👋")
    st.write(f"Your Paircode is {st.session_state.paircode}")
    
    alert_query = f"""
        SELECT COUNT(*) as pending_count FROM transactions
        WHERE (lender = '{st.session_state.current_user}' AND status = 'pending_deletion_borrower')
           OR (borrower = '{st.session_state.current_user}' AND status = 'pending_deletion_lender')
    """
    try:
        pending_data = conn.query(alert_query, ttl=0)
        pending_count = pending_data.iloc[0]['pending_count']
        if pending_count > 0:
            st.warning(f"⚠️ You have {pending_count} pending transaction deletion request(s) awaiting your approval! Go to 'Delete Transaction' to review.")
    except Exception as e:
        pass

    friend_alert_query_sent = f"""
        SELECT COUNT(*) as pending_count FROM friends
        WHERE (user2 = '{st.session_state.current_user}' AND status IN ('sent', 'pending'))
    """

    friend_alert_query_pending = f'''
        SELECT COUNT(*) as pending_count FROM friends
        WHERE (user1 = '{st.session_state.current_user}' AND status IN ('sent', 'pending'))
    '''

    try:
        pending_data = conn.query(friend_alert_query_sent, ttl=0)
        sent_data = conn.query(friend_alert_query_pending, ttl=0)
        pending_count = pending_data.iloc[0]['pending_count']
        sent_count = sent_data.iloc[0]["pending_count"]
        if pending_count > 0:
            st.warning(f"⚠️ You have {pending_count} pending friend request(s) awaiting your approval! Go to 'Add Friends' to review.")
        if sent_count > 0:
            st.warning(f"⚠️ Your {sent_count} sent friend request(s) is still awaiting for approval! ")
    except Exception as e:
        pass

    st.divider()
    
    st.markdown("### 🧭 Navigation Menu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 💸 Add Transaction")
            st.caption("Record a new lending or borrowing activity.")
            if st.button("➕ Add", use_container_width=True):
                st.session_state.page = "add_transaction"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 📜 View History")
            st.caption("See a summary of your past transactions.")
            if st.button("🔍 View", use_container_width=True):
                st.session_state.page = "view_transactions"
                st.rerun()

        with st.container(border=True):
            st.markdown("### 🗑️ Delete Ledger")
            st.caption("Request to permanently delete a transaction.")
            if st.button("🚮 Delete", use_container_width=True):
                st.session_state.page = "delete_transaction"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 👥 Friends")
            st.caption("Manage your friends and connections.")
            if st.button("🤝 Connect", use_container_width=True):
                st.session_state.page = "add_friends"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 💳 Pay Amount")
            st.caption("Execute a UPI payment settlement.")
            if st.button("💸 Pay", use_container_width=True):
                st.session_state.page = "pay_amount"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 🚪 Account")
            st.caption("Sign out of your active session.")
            if st.button("🚪 Logout", type="primary", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "login"
                st.rerun()

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "add_friends":
    friends_page()
elif st.session_state.page == "view_transactions":
    view_page()
elif st.session_state.page == "add_transaction":
    add_transaction_page()
elif st.session_state.page == "pay_amount":
    pay_amount()
elif st.session_state.page == "delete_transaction":
    delete_trans_page()
elif st.session_state.logged_in:
    dashboard_page()
else:
    st.session_state.page = "login"
    st.rerun()