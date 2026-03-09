import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy import text
from auth import login_page, logout, signup_page
from database import conn
from config import SHOPS, NJC, TECH_CAFE, KRISHNA_KRRIPA, AMUL

def add_transaction_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💸 Add Transaction")
        st.write("Record a new lending or borrowing activity")
    with col2:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    st.divider()
    
    friends_query = f"""
        SELECT 
            CASE 
                WHEN user1 = '{st.session_state.current_user}' THEN user2
                ELSE user1 
            END as friend_name
        FROM friends
        WHERE user1 = '{st.session_state.current_user}' OR user2 = '{st.session_state.current_user}'
    """
    users = conn.query(friends_query, ttl=0)['friend_name'].to_list()
    
    with st.container(border=True):
        st.markdown("### 📝 Transaction Details")
        transactee = st.selectbox("Select the person you want to transact with", users, placeholder="🧑‍🤝‍🧑 Select Friend", index=None)
        
        amount = 0
        description = ""
        food_item = ""
        
        transaction = st.selectbox("Enter transaction / shop category", SHOPS, index=None, placeholder="🏪 Select Category")

        if transaction == "NJC":
            food_item = st.selectbox("Enter food item", list(NJC.keys()))
            amount = NJC[food_item]
            if amount == 0:
                amount = st.number_input("Enter amount", min_value=1, max_value=100000, value=1, step=5)   

        elif transaction == "Tech Cafe":
            food_item = st.selectbox("Enter food item", list(TECH_CAFE.keys()))
            amount = TECH_CAFE[food_item]
            if amount == 0:
                amount = st.number_input("Enter amount", min_value=1, max_value=100000, value=1, step=5)   

        elif transaction == "Krishna Krripa":
            food_item = st.selectbox("Enter food item", list(KRISHNA_KRRIPA.keys()))
            amount = KRISHNA_KRRIPA[food_item]
            if amount == 0:
                amount = st.number_input("Enter amount", min_value=1, max_value=100000, value=1, step=5)   

        elif transaction == "Amul":
            food_item = st.selectbox("Enter food item", list(AMUL.keys()))
            amount = AMUL[food_item]
            if amount == 0:
                amount = st.number_input("Enter amount", min_value=9, max_value=1000, value=9, step=5)   

        elif transaction in ["BlinkIT", "Auto/Rentals", "Outside", "Others"]:
            amount = st.number_input("Enter amount", min_value=-1000, max_value=1000, value=1, step=5)
            description = st.text_input("Enter description / note", value="", placeholder="e.g. Movie tickets")

        if transaction and transactee:
            if st.button("➕ Save Transaction", type="primary"):
                st.session_state.changes = amount
                with conn.session as s:
                    query = '''INSERT INTO transactions (date_time, lender, borrower, shop_category, item, amount, description, status) 
                               VALUES (CURRENT_TIMESTAMP, '{lender}', '{borrower}', '{shop}', '{item}', {amount}, '{description}', 'active')'''
                    s.execute(text(query.format(
                        lender=st.session_state.current_user, 
                        borrower=transactee, 
                        shop=transaction, 
                        item=food_item, 
                        amount=amount, 
                        description=description
                    )))
                    s.commit()
                st.success(f"Transaction recorded successfully! 🎉")
                
                with st.expander("Show Latest Transaction Details", expanded=True):
                    colA, colB = st.columns(2)
                    with colA:
                        st.write(f"**Transactee:** {transactee}")
                        st.write(f"**Shop:** {transaction}")
                    with colB:
                        if food_item:
                            st.write(f"**Item:** {food_item}")
                        st.write(f"**Amount:** ₹ {amount}")
                        if description:
                            st.write(f"**Note:** {description}")
                    
    st.divider()

    if transactee:
        st.markdown(f"### 📊 History with {transactee}")

        query = f"""
            SELECT date_time, lender, borrower, shop_category, item, amount, description, status
            FROM transactions 
            WHERE (lender = '{st.session_state.current_user}' AND borrower = '{transactee}')
               OR (lender = '{transactee}' AND borrower = '{st.session_state.current_user}')
            ORDER BY date_time DESC
        """
        
        df = conn.query(query, ttl=0)

        if not df.empty:
            lended = df[df['lender'] == st.session_state.current_user]['amount'].sum()
            borrowed = df[df['borrower'] == st.session_state.current_user]['amount'].sum()
            net_balance = lended - borrowed

            row = st.container(horizontal=True)
            with row:
                st.metric("Total Lended 🟢", f":green[₹{lended:.2f}]", delta = st.session_state.changes, )
                st.metric("Total Borrowed 🔴", f":red[₹{borrowed:.2f}]")
                st.metric("Net Balance ⚖️", f"₹{net_balance:.2f}", delta = st.session_state.changes)

            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "date_time": st.column_config.DatetimeColumn("Date & Time ⏰", format="DD MMM YY, HH:mm"),
                    "lender": st.column_config.TextColumn("Lender 🔼"),
                    "borrower": st.column_config.TextColumn("Borrower 🔽"),
                    "shop_category": st.column_config.TextColumn("Shop 🏪"),
                    "item": st.column_config.TextColumn("Item 🛍️"),
                    "amount": st.column_config.NumberColumn("Amount 💸", format="₹ %.2f"),
                    "description": st.column_config.TextColumn("Note 🗒️"),
                    "status": st.column_config.TextColumn("Status 🚦")
                }
            )
        else:
            st.info("No transaction history found with this person yet.")
