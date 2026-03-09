import streamlit as st
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, text
from datetime import datetime

# def get_connection():
#     try:
#         if "mydb" in st.secrets.get("connections", {}):
#             return st.connection("mydb", type="sql")
#         else:
#             return st.connection("local_db", type="sql", url="sqlite:///transactions.db")
#     except (FileNotFoundError, Exception):
#         return st.connection("local_db", type="sql", url="sqlite:///transactions.db") 

def get_connection():
    return st.connection("mydb", type="sql")

conn = get_connection()

metadata = MetaData()
cred_table = Table(
    'credentials', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(20), nullable=False, unique=True),
    Column('password', String(20), nullable=False),
    Column('paircode', Integer, nullable=False)
)

friends_table = Table(
    'friends', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user1', String(20), nullable=False),
    Column('user2', String(20), nullable=False),
    Column("status", String(20), nullable=False)
)

transactions_table = Table(
    'transactions', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date_time', DateTime, default=datetime.utcnow),
    Column('lender', String(20), nullable=False),
    Column('borrower', String(20), nullable=False),
    Column('shop_category', String(20)),
    Column('item', String(20)),
    Column('amount', Float, nullable=False),
    Column('description', String(25)),
    Column('status', String(20), default='active')
)

metadata.create_all(conn.engine)
