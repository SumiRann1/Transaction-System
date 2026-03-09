import streamlit as st
from auth import login_page, signup_page, logout
from sqlalchemy import text
from database import conn, cred_table

def view_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📜 View History")
        st.write(f"Logged in as: **{st.session_state.current_user.upper()}** (Paircode: `{st.session_state.paircode}`)")
    with col2:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    st.divider()

    st.markdown("### 🧑‍🤝‍🧑 Your Friend Ledgers")

    friends_query = f"""
        SELECT 
            CASE 
                WHEN user1 = '{st.session_state.current_user}' THEN user2
                ELSE user1 
            END as friend_name
        FROM friends
        WHERE user1 = '{st.session_state.current_user}' OR user2 = '{st.session_state.current_user}'
    """
    friend_list = conn.query(friends_query, ttl=0)['friend_name'].to_list()
        
    if friend_list:
        if len(friend_list) == 1:
            friend_list.append(friend_list[0])
        code_list = conn.query(f"SELECT paircode FROM credentials WHERE username IN {tuple(friend_list)}", ttl=0)['paircode'].to_list()
        
        for name, code in zip(friend_list, sorted(code_list)):
            query = f"""
                SELECT date_time, lender, borrower, shop_category, item, amount, description, status
                FROM transactions 
                WHERE (lender = '{st.session_state.current_user}' AND borrower = '{name}')
                   OR (lender = '{name}' AND borrower = '{st.session_state.current_user}')
                ORDER BY date_time DESC
            """
            data = conn.query(query, ttl=0)
            
            with st.container(border=True):
                st.markdown(f"#### 👤 {name} (Code: `{code}`)")
                if not data.empty:
                    st.dataframe(
                        data, 
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
                    st.info(f"No transactions found with {name}.")
    else:
        st.info("You don't have any friends yet.")
