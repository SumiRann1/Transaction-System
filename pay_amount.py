from auth import logout
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import conn, cred_table

payments = {}
def pay():
    with st.container(border=True):
        st.markdown("### 💸 Initiate Payment")
        
        if not payments:
            st.info("No pending payments required.")
            return
            
        f = st.selectbox("Select Friend to Pay", payments.keys(), placeholder="Select a friend")
        if f:
            amount = st.number_input("Amount (₹)", min_value=0.0, max_value=float(payments[f]+0.1), value=0.0, key= f"{f}_{st.session_state.current_user}_{payments[f]}_INPUT")
            
            upi_id = st.text_input("Enter UPI ID of your friend", placeholder="e.g. friend@upi")
            
            if upi_id and amount > 0:
                st.divider()
                st.markdown("#### 📱 Step 1: Open Payment App")
                upi_url = f"upi://pay?pa={upi_id}&pn={f}&cu=INR&am={amount}"
                st.markdown(f'''
                <a href="{upi_url}" target="_blank">
                    <button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold;">
                        Pay ₹{amount} via UPI App
                    </button>
                </a>
                ''', unsafe_allow_html=True)
                
        if f and amount > 0:
            st.markdown("#### 🧾 Step 2: Verification")
            utr_id = st.text_input("Enter UTR/Transaction ID from the payment app to verify:")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Verify & Record Payment", use_container_width=True, type="primary"):
                    if utr_id.strip() == "":
                        st.error("Please provide a valid UTR/Transaction ID to verify the payment.")
                    else:
                        with conn.session as s:
                            query = '''INSERT INTO transactions (date_time, lender, borrower, shop_category, item, amount, description, status) 
                                            VALUES (CURRENT_TIMESTAMP, '{lender}', '{borrower}', '{shop}', '{item}', {amount}, '{description}', 'active')'''
                            s.execute(text(query.format(
                                        lender=st.session_state.current_user, 
                                        borrower=f, 
                                        shop="PAID BACK", 
                                        item="", 
                                        amount=amount, 
                                        description=f"Amount paid back (UTR: {utr_id})"
                            )))
                            s.commit()
                        st.success(f"Payment Recorded with UTR: {utr_id} 🎉")
                        st.session_state.show_pay_form = False
                        st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_pay_form = False
                    st.rerun()
    
def pay_amount():
    global payments
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💳 Pay Amount")
        st.write(f"Settle your dues, **{st.session_state.current_user}**.")
    with col2:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.session_state.show_pay_form = False
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    st.divider()
    
    if "show_pay_form" not in st.session_state:
        st.session_state.show_pay_form = False

    if not st.session_state.show_pay_form:
        if st.button("💸 Make a Payment", type="primary"):
            st.session_state.show_pay_form = True
            st.rerun()
        
    if st.session_state.show_pay_form:
        pay()

    st.divider()
    st.markdown("### 📊 Existing Balances")

    existing_friend = conn.query(
        f"""
        SELECT 
            CASE 
                WHEN user1 = '{st.session_state.current_user}' THEN user2
                ELSE user1 
            END as friend_name
        FROM friends
        WHERE user1 = '{st.session_state.current_user}' OR user2 = '{st.session_state.current_user}'""", ttl=0)['friend_name'].to_list()  
    
    trans_query = f"""
            SELECT lender, borrower, amount 
            FROM transactions 
            WHERE lender = '{st.session_state.current_user}' OR borrower = '{st.session_state.current_user}'
        """
    df = conn.query(trans_query, ttl=0)
    
    if not existing_friend:
        st.info("You don't have any friends yet.")
    else:

        cols = st.columns(3) # Display cards in rows of 3
        col_idx = 0

        for f in existing_friend:
            lended = 0.0
            borrowed = 0.0
            if not df.empty:
                lended = df[(df['lender'] == st.session_state.current_user) & (df['borrower'] == f)]['amount'].sum()
                borrowed = df[(df['borrower'] == st.session_state.current_user) & (df['lender'] == f)]['amount'].sum()
            net = lended - borrowed
            
            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**👤 {f}**")
                    st.caption(f"Net Balance: **₹ {net:.2f}**")
                    if net < 0:
                        st.error(f"You owe: ₹ {abs(net):.2f}")
                        payments[f] = abs(net)
                    elif net > 0:
                        st.success(f"Owes you: ₹ {net:.2f}")
                    else:
                        st.info("Settled Up ⚖️")
            
            col_idx = (col_idx + 1) % 3
    

    