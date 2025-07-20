#pages\functions.py
import sqlite3
import os
import base64
import pandas as pd
from dash import no_update

#database
def get_conn():
    return sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "data", "tradedata.db"))

def dbquery(query: str, params: tuple = ()):
    conn = get_conn()  
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def pdquery(query: str):
    conn = get_conn()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def init_db():
    dbquery("""
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
    dbquery("""
    INSERT INTO TRADE_DATA
    ("Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

def delete_recent():
    dbquery("""
    DELETE FROM TRADE_DATA WHERE rowid = (
    SELECT rowid FROM TRADE_DATA ORDER BY Date DESC, "Entry Time" DESC LIMIT 1
    )
    """)

def top_recent():
    return pdquery("""SELECT * FROM TRADE_DATA ORDER BY Date DESC, "Entry Time" DESC LIMIT 10""")

def base64_to_bytes(base64_str):
    content_type, content_string = base64_str.split(',')
    return base64.b64decode(content_string)

#removes the no update hell xD
def no_updates(n):
    return [no_update]*n

def get_total_pnl():
    df = pdquery("""SELECT SUM("P&L") as total_pnl 
                 FROM TRADE_DATA
    """)        
    if df.empty or df['total_pnl'].iloc[0] == 0:
        return 0
    return round(df['total_pnl'].iloc[0],2) 

def get_win_rate():
    df = pdquery("""
        SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN "P&L" > 0 THEN 1 ELSE 0 END) as total_wins
        FROM TRADE_DATA
    """)
    if df.empty or df['total_trades'].iloc[0] == 0:
        return 0
    return round(df['total_wins'].iloc[0]/df['total_trades'].iloc[0] * 100, 2)