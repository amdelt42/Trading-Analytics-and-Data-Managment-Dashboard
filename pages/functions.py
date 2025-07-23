#pages\functions.py
import sqlite3
import os
import base64
import pandas as pd
from dash import no_update

#connect to db
def get_conn():
    return sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "data", "tradedata.db"))

#modify db
def dbquery(query: str, params: tuple = ()) -> None:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

#retrieve from db to df
def pdquery(query: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(query, conn)

#init db
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
def insert_trade(data: tuple) -> None:
    dbquery("""
    INSERT INTO TRADE_DATA
    ("Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

def delete_recent() -> None:
    dbquery("""
    DELETE FROM TRADE_DATA WHERE rowid = (
    SELECT rowid FROM TRADE_DATA ORDER BY Date DESC, [Entry Time] DESC LIMIT 1
    )
    """)

def top_recent() -> pd.DataFrame:
    return pdquery("""SELECT * FROM TRADE_DATA ORDER BY Date DESC, [Entry Time] DESC LIMIT 10""")

def base64_to_bytes(base64_str: str) -> bytes:
    content_type, content_string = base64_str.split(',')
    return base64.b64decode(content_string)

#removes the no update hell xD
def no_updates(n: int) -> list:
    return [no_update]*n

#0. total_pnl
#1. total_profits
#2. total_loss
#3. profit_factor
#4. win_rate
#5. avg_rr
#6. avg_win
#7. avg_loss
def get_stats(period: str = None) -> tuple:
    base_select = ("""
        SELECT 
                 
        SUM([P&L]) AS t_pnl,
        SUM(CASE WHEN [P&L] > 0 THEN [P&L] ELSE 0 END) AS t_profit,
        SUM(CASE WHEN [P&L] < 0 THEN [P&L] ELSE 0 END) AS t_loss,
        SUM(CASE WHEN [P&L] > 0 THEN [P&L] ELSE 0 END) / NULLIF(ABS(SUM(CASE WHEN [P&L] < 0 THEN [P&L] ELSE 0 END)), 0) AS p_factor,   
                        
        100.00 * SUM(CASE WHEN [P&L] > 0 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate,
                 
        AVG(CASE WHEN [P&L] > 0 AND [Risk] <> 0 THEN [P&L] / [Risk] ELSE NULL END) AS avg_rr,
        AVG(CASE WHEN [P&L] > 0 THEN [P&L] ELSE NULL END) AS avg_win,
        AVG(CASE WHEN [P&L] < 0 THEN [P&L] ELSE NULL END) AS avg_loss              
                 
        FROM TRADE_DATA
    """)

    #period filtering (idk, it seems to work I guess)
    where_clause = ""
    if period == "monthly":
        where_clause = """
        WHERE strftime('%Y-%m', [Date]) = strftime('%Y-%m', 'now')
        """
    elif period == "weekly":
        where_clause = """
        WHERE strftime('%Y-%W', [Date]) = strftime('%Y-%W', 'now')
        """
    elif period == "daily":
        where_clause = """
        WHERE DATE([Date]) = DATE('now')
        """

    query = base_select + where_clause

    df = pdquery(query)

    if df.empty:
        return tuple(0 for col in df.columns)
    return tuple(round(df[col].iloc[0], 2) for col in df.columns)

#simple handy display functions
def percent(var: float) -> str:
    return f"{var:.1f}%"

def eur(var: float) -> str:
    return f"\u20ac{var:.2f}"