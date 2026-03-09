from auth import logout
from database import conn
from sqlalchemy import text
import streamlit as st

def delete_trans_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🗑️ Delete Ledger")
        st.write("Manage your transaction deletion requests")
    with col2:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    st.divider()

    query = f"""
        SELECT date_time, lender, borrower, shop_category, item, amount, description, status 
        FROM transactions 
        WHERE lender = '{st.session_state.current_user}' OR borrower = '{st.session_state.current_user}'
        ORDER BY date_time DESC
    """
    data = conn.query(query, ttl=0)

    if data.empty:
        st.info("You don't have any transactions to manage.")
    
    else:
        needs_my_approval = data[
            ((data['lender'] == st.session_state.current_user) & (data['status'] == 'pending_deletion_borrower')) |
            ((data['borrower'] == st.session_state.current_user) & (data['status'] == 'pending_deletion_lender'))
        ]

        waiting_on_other = data[
            ((data['lender'] == st.session_state.current_user) & (data['status'] == 'pending_deletion_lender')) |
            ((data['borrower'] == st.session_state.current_user) & (data['status'] == 'pending_deletion_borrower'))
        ]
        
        active_trans = data[data['status'] == 'active']
        
        if not needs_my_approval.empty:
            st.warning(f"⚠️ You have {len(needs_my_approval)} deletion request(s) awaiting your approval!")
            st.markdown("### 🔔 Pending Your Approval")
            for index, row in needs_my_approval.iterrows():
                with st.container(border=True):
                    colA, colB, colC = st.columns([3,1,1])
                    with colA:
                        st.markdown(f"**Request to delete:** {row['date_time']} | 🏪 {row['shop_category']} | 💸 ₹{row['amount']}")
                        requester = row['borrower'] if row['lender'] == st.session_state.current_user else row['lender']
                        st.caption(f"Requested by: {requester}")
                    with colB:
                        if st.button("✅ Approve & Delete", key=f"approve_{index}", use_container_width=True):
                            with conn.session as s:
                                del_query = f"""
                                    DELETE FROM transactions 
                                    WHERE date_time = '{row['date_time']}'
                                    AND lender = '{row['lender']}'
                                    AND borrower = '{row['borrower']}'
                                    AND amount = {row['amount']}
                                """
                                s.execute(text(del_query))
                                s.commit()
                            st.success("Transaction permanently deleted.")
                            st.rerun()
                    with colC:
                        if st.button("❌ Reject", type="primary", key=f"reject_{index}", use_container_width=True):
                            with conn.session as s:
                                rej_query = f"""
                                    UPDATE transactions SET status = 'active'
                                    WHERE date_time = '{row['date_time']}'
                                    AND lender = '{row['lender']}'
                                    AND borrower = '{row['borrower']}'
                                    AND amount = {row['amount']}
                                """
                                s.execute(text(rej_query))
                                s.commit()
                            st.error("Deletion request rejected. Transaction restored to active status.")
                            st.rerun()

        if not waiting_on_other.empty:
            st.markdown("### ⏳ Deletion Requests Sent (Pending)")
            st.dataframe(
                waiting_on_other.drop(columns=['status']), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "date_time": st.column_config.DatetimeColumn("Date & Time ⏰", format="DD MMM YY, HH:mm"),
                    "lender": st.column_config.TextColumn("Lender 🔼"),
                    "borrower": st.column_config.TextColumn("Borrower 🔽"),
                    "shop_category": st.column_config.TextColumn("Shop 🏪"),
                    "item": st.column_config.TextColumn("Item 🛍️"),
                    "amount": st.column_config.NumberColumn("Amount 💸", format="₹ %.2f"),
                    "description": st.column_config.TextColumn("Note 🗒️")
                }
            )

        st.divider()

        if not active_trans.empty:
            st.markdown("### 📜 Active Transactions")
            st.dataframe(
                active_trans.drop(columns=['status']), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "date_time": st.column_config.DatetimeColumn("Date & Time ⏰", format="DD MMM YY, HH:mm"),
                    "lender": st.column_config.TextColumn("Lender 🔼"),
                    "borrower": st.column_config.TextColumn("Borrower 🔽"),
                    "shop_category": st.column_config.TextColumn("Shop 🏪"),
                    "item": st.column_config.TextColumn("Item 🛍️"),
                    "amount": st.column_config.NumberColumn("Amount 💸", format="₹ %.2f"),
                    "description": st.column_config.TextColumn("Note 🗒️")
                }
            )
            
            with st.container(border=True):
                st.markdown("#### 🗑️ Request to Delete a Transaction")
                st.caption("Select transactions below to send deletion requests to the other user.")
                for index, row in active_trans.iterrows():
                    trans_check = st.checkbox(f"Request Deletion for {row['date_time']} (₹{row['amount']})", key=f"req_delete_{index}")
                    
                    if trans_check:
                        if row['lender'] == st.session_state.current_user:
                            new_status = 'pending_deletion_lender'
                        else:
                            new_status = 'pending_deletion_borrower'

                        with conn.session as s:
                            req_query = f"""
                                UPDATE transactions SET status = '{new_status}'
                                WHERE date_time = '{row['date_time']}'
                                AND lender = '{row['lender']}'
                                AND borrower = '{row['borrower']}'
                                AND shop_category = '{row['shop_category']}' 
                                AND amount = {row['amount']}
                            """
                            s.execute(text(req_query))
                            s.commit()
                        st.success("Deletion request sent to the other person for approval.")
                        st.rerun()