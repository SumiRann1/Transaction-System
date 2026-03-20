from auth import logout
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import conn, cred_table

def friends_page():
    USERS = conn.query("SELECT username, paircode FROM credentials", ttl=0)
    USERS = USERS.drop(USERS.loc[USERS["username"] == st.session_state.current_user].index, axis = 0)

    friends_query = f"""
        SELECT 
            CASE 
                WHEN user1 = '{st.session_state.current_user}' THEN user2
                ELSE user1 
            END as friend_name
        FROM friends
        WHERE (user1 = '{st.session_state.current_user}' OR user2 = '{st.session_state.current_user}') AND status = 'accepted'
    """
    existing_friend = conn.query(friends_query, ttl=0)['friend_name'].to_list()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("👥 Friends")
        st.write(f"Welcome back, **{st.session_state.current_user}**! 👋")
    with col2:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    st.divider()

    st.markdown("### ➕ Add a New Friend")
    with st.container(border=True):
        st.radio("Search Method", ("By UserName", "By PairCode"), index=0, key="radio", horizontal=True)
        if st.session_state.radio == "By UserName":
            friend = st.selectbox("Select friend to add", sorted(USERS["username"]),index=None, placeholder = "🔍 Search by UserName")
            if friend:
                st.write("You Selected : ", friend)
            submit = st.button("Send Friend Request", type="primary")
        elif st.session_state.radio == "By PairCode":
            paircode = st.selectbox("Get friend via paircode", sorted(USERS["paircode"]),index=None, placeholder = "🔑 Search by PairCode")
            if paircode:
                st.write("You selected : ", paircode)
            submit = st.button("Send Friend Request", type="primary")
            try:
                friend =  USERS[(USERS["paircode"] == paircode)]["username"].to_list()[0]
                if paircode:
                    st.write("Username : ", friend)
            except:
                if paircode:
                    st.error("Friend not found")

        if submit:
            with conn.session as s:
                check_query = '''SELECT id, status FROM friends 
                                 WHERE (user1 = '{user}' AND user2 = '{friend}')
                                    OR (user1 = '{friend}' AND user2 = '{user}')'''
                existing = conn.query(check_query.format(user=st.session_state.current_user, friend=friend), ttl=0)
                
                if not existing.empty:
                    st.error(f"You and {friend} are already friends or have a pending request.")
                else:
                    insert_query = '''INSERT INTO friends (user1, user2, status) VALUES ('{user}', '{friend}', 'sent')'''
                    s.execute(text(insert_query.format(user=st.session_state.current_user, friend=friend)))
                    s.commit()
                    st.success(f"Friend request sent to {friend} successfully! ✅")
    
    st.divider()
    all_query = """
        SELECT user1, user2, status FROM friends WHERE user2 = '{}'
    """
    all_friend = conn.query(all_query.format(st.session_state.current_user), ttl=0)
    pending_friend = all_friend[all_friend['status'] == 'sent']

    st.markdown("### 🔔 Pending Friend Requests")
    if pending_friend.empty:
        st.info("You don't have any pending friend requests right now.")
    else:
        for f in pending_friend['user1'].to_list():
            with st.container(border=True):
                colA, colB, colC = st.columns([3,1,1])
                with colA:
                    st.markdown(f"**👤 {f}** wants to be your friend!")
                with colB:
                    if st.button("✅ Accept", key=f"accept_{f}", use_container_width=True):
                        with conn.session as s:
                            accept_query = f"""
                            UPDATE friends SET status = 'accepted'
                            WHERE user1 = '{st.session_state.current_user}' AND user2 = '{f}'
                            OR user1 = '{f}' AND user2 = '{st.session_state.current_user}'
                            """
                            s.execute(text(accept_query))
                            s.commit()
                        st.success(f"Friend request from {f} accepted!")
                        st.rerun()
                with colC:
                    if st.button("❌ Decline", key=f"decline_{f}", type="primary", use_container_width=True):
                        with conn.session as s:
                            decline_query = f"""
                            DELETE FROM friends 
                            WHERE user1 = '{st.session_state.current_user}' AND user2 = '{f}'
                            OR user1 = '{f}' AND user2 = '{st.session_state.current_user}'
                            """
                            s.execute(text(decline_query))
                            s.commit()
                        st.error(f"Friend request from {f} declined.")
                        st.rerun()

    st.divider()
    
    st.markdown("### 🤝 My Friends List")

    if not existing_friend:
        st.info("You don't have any friends yet.")
    else:
        # BUG FIX: transactions table has 'active' or 'pending_deletion_lender' status, NOT 'accepted'.
        # We can just fetch all non-deleted transactions the user is involved in.
        trans_query = f"""
            SELECT lender, borrower, amount 
            FROM transactions 
            WHERE (lender = '{st.session_state.current_user}' OR borrower = '{st.session_state.current_user}')
        """
        df_trans = conn.query(trans_query, ttl=0)
        
        friends_data = []
        total = 0
        for f in existing_friend:
            lended = 0.0
            borrowed = 0.0
            if not df_trans.empty:
                lended = df_trans[(df_trans['lender'] == st.session_state.current_user) & (df_trans['borrower'] == f)]['amount'].sum()
                borrowed = df_trans[(df_trans['borrower'] == st.session_state.current_user) & (df_trans['lender'] == f)]['amount'].sum()
            net = lended - borrowed
            total += net
            friends_data.append({
                "Friend": f,
                "Lended (₹)": lended,
                "Borrowed (₹)": borrowed,
                "Net Balance (₹)": net
            })
            
        friends_df = pd.DataFrame(friends_data)
        st.dataframe(
            friends_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Friend": st.column_config.TextColumn("Friend 👤"),
                "Lended (₹)": st.column_config.NumberColumn("Lended 🟢", format="₹ %.2f"),
                "Borrowed (₹)": st.column_config.NumberColumn("Borrowed 🔴", format="₹ %.2f"),
                "Net Balance (₹)": st.column_config.NumberColumn("Net Balance ⚖️", format="₹ %.2f")
            }
        )

    if total < 0:
        st.subheader(":red[Total Debt Amount :]")
    else:
        st.subheader(":green[Total Incoming Amount :]")
    st.metric(value=total)
    
