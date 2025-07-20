import sqlite3
import os
import base64
import pandas as pd
from dash import no_update

#database
def get_conn():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "tradedata.db")
    return sqlite3.connect(data_path), data_path

def init_db():
    conn, _ = get_conn()  # Use the same path as your get_conn()
    cursor = conn.cursor()
    cursor.execute("""
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
    conn.commit()
    conn.close()

#data entry and management
def insert_trade(data):
    conn, _ = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO TRADE_DATA
    ("Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def delete_recent():
    conn, _ = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM TRADE_DATA WHERE rowid = (
            SELECT rowid FROM TRADE_DATA ORDER BY Date DESC LIMIT 1
        )
    """)
    conn.commit()
    conn.close()

def top_recent():
    conn, _ = get_conn()
    df = pd.read_sql_query("SELECT * FROM TRADE_DATA ORDER BY Date DESC LIMIT 10", conn)
    conn.close()
    return df

def base64_to_bytes(base64_str):
    content_type, content_string = base64_str.split(',')
    return base64.b64decode(content_string)

#removes the no update hell
def no_updates(n):
    return [no_update] * n