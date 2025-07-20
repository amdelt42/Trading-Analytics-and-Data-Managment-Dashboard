import sqlite3
import os
import base64
import pandas as pd
from dash import no_update

#database
def get_conn():
    return sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "data", "tradedata.db"))

def query(query: str, params: tuple = ()):
    conn = get_conn()  
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def init_db():
    query("""
    CREATE TABLE IF NOT EXISTS TRADE_DATA (
        "Date" TEXT,
        "Ticker" TEXT,
        "Type" TEXT,
        "Entry" REAL,
        "Exit" REAL,
        "Entry Time" TEXT,
        "Exit Time" TEXT,
        "Risk" REAL,
        "P&L" REAL,
        "Fees" REAL,
        "Tags" TEXT,
        "Grade" INTEGER,
        "Image" BLOB
    )
    """)

#data entry and management
def insert_trade(data):
    query("""
    INSERT INTO TRADE_DATA
    ("Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

def delete_recent():
    query("""
    DELETE FROM TRADE_DATA WHERE rowid = (
    SELECT rowid FROM TRADE_DATA ORDER BY Date DESC LIMIT 1
    )
    """)

def top_recent():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM TRADE_DATA ORDER BY Date DESC LIMIT 10", conn)
    conn.close()
    return df

def base64_to_bytes(base64_str):
    content_type, content_string = base64_str.split(',')
    return base64.b64decode(content_string)

#removes the no update hell
def no_updates(n):
    return [no_update] * n