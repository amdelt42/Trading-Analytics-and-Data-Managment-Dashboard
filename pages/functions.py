#pages\functions.py
import duckdb

import base64
import pandas as pd

from pathlib import Path
from dash import no_update
from functools import lru_cache

from dash import html, dcc
import plotly.graph_objects as go

from typing import Optional, Tuple

#db management
def get_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(Path(__file__).resolve().parent.parent / "data" / "tradedata.duckdb")

def init_db() -> None:
    dbquery("""
    CREATE TABLE IF NOT EXISTS TRADE_DATA (
        id INTEGER PRIMARY KEY,
        "Date" DATE,
        "Ticker" TEXT,
        "Type" TEXT,
        "Entry" REAL,
        "Exit" REAL,
        "Entry Time" TIME,
        "Exit Time" TIME,
        "Risk" REAL,    
        "P&L" REAL,
        "Fees" REAL,
        "Tags" TEXT,
        "Grade" INTEGER,
        "Image" BLOB,
        "Trade Result" VARCHAR(10)
    )
    """)
    dbquery("CREATE SEQUENCE IF NOT EXISTS id START 1")
    dbquery("CREATE INDEX IF NOT EXISTS idx_date ON TRADE_DATA(Date)") #optimize date filtering

def dbquery(query: str, params: tuple = ()) -> None:
    #modify db
    with get_conn() as conn:
        conn.execute(query, params)  
        conn.commit()

def pdquery(query: str, params: tuple = ()) -> pd.DataFrame:
    #retrieve from db
    with get_conn() as conn:
        return conn.execute(query, params).fetchdf()

#data management
def insert_trade(data: tuple) -> None:
    dbquery("""
    INSERT INTO TRADE_DATA
    ("id","Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image", "Trade Result")
    VALUES (nextval('id'),?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

def delete_recent() -> None:
    dbquery("""
    DELETE FROM TRADE_DATA WHERE id = (
    SELECT id FROM TRADE_DATA ORDER BY "Date" DESC, "Entry Time" DESC LIMIT 1
    )
    """)

def top_recent() -> pd.DataFrame:
    return pdquery("""SELECT * FROM TRADE_DATA ORDER BY Date DESC, "id" DESC LIMIT 20""")

def base64_to_bytes(base64_str: str) -> bytes:
    content_type, content_string = base64_str.split(',')
    return base64.b64decode(content_string)

#gets some stats
@lru_cache(maxsize=16)
def get_stats(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> tuple: #10% breakeven threshold
    tags = list(tags)
    df = pdquery(f"""
        SELECT 
                 
            --FIND GENERAL RESULTS
            SUM("P&L") AS t_pnl,

            SUM(CASE WHEN "Trade Result" = 'Win' THEN "P&L" ELSE 0 END) AS t_pnl_win,
            SUM(CASE WHEN "Trade Result" = 'Loss' THEN "P&L" ELSE 0 END) AS t_pnl_loss,
            
            SUM(CASE WHEN "Trade Result" = 'Win' THEN "P&L" ELSE 0 END) / 
                NULLIF(ABS(SUM(CASE WHEN "Trade Result" = 'Loss' THEN "P&L" ELSE 0 END)), 0) AS p_factor,
            100.0 * SUM(CASE WHEN "Trade Result" = 'Win' THEN 1 ELSE 0 END) / COUNT(*) AS wr,
            
            AVG(CASE WHEN "Trade Result" = 'Win' AND "Risk" <> 0 THEN "P&L" / "Risk" ELSE NULL END) AS avg_rr,
            AVG(CASE WHEN "Trade Result" = 'Win' THEN "P&L" ELSE NULL END) AS avg_win,
            AVG(CASE WHEN "Trade Result" = 'Loss' THEN "P&L" ELSE NULL END) AS avg_loss,
            
            COUNT(*) AS t_count,
            SUM(CASE WHEN "Trade Result" = 'Win' THEN 1 ELSE 0 END) AS t_win,
            SUM(CASE WHEN "Trade Result" = 'Loss' THEN 1 ELSE 0 END) AS t_loss,
            SUM(CASE WHEN "Trade Result" = 'Break-Even' THEN 1 ELSE 0 END) AS t_breakeven,
                    

            --FIND LONG/SHORT RESULTS
            100.0 * SUM(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Long' THEN 1 ELSE 0 END) / SUM(CASE WHEN "Trade Result" = 'Win' THEN 1 ELSE 0 END) AS long_wr,
            100.0 * SUM(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Short' THEN 1 ELSE 0 END) / SUM(CASE WHEN "Trade Result" = 'Win' THEN 1 ELSE 0 END) AS short_wr,
                
            SUM(CASE WHEN "Type" = 'Long' THEN "P&L" ELSE 0 END) AS t_pnl_long,
            SUM(CASE WHEN "Type" = 'Short' THEN "P&L" ELSE 0 END) AS t_pnl_short,
                
            AVG(CASE WHEN "Trade Result" = 'Win' AND "Risk" <> 0 AND "Type" = 'Long' THEN "P&L" / "Risk" ELSE NULL END) AS avg_rr_long,
            AVG(CASE WHEN "Trade Result" = 'Win' AND "Risk" <> 0 AND "Type" = 'Short' THEN "P&L" / "Risk" ELSE NULL END) AS avg_rr_short,
                
            SUM(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Long' THEN "P&L" ELSE 0 END) / 
                NULLIF(ABS(SUM(CASE WHEN "Trade Result" = 'Loss' AND "Type" = 'Long' THEN "P&L" ELSE 0 END)), 0) AS p_factor_long,
            SUM(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Short' THEN "P&L" ELSE 0 END) / 
                NULLIF(ABS(SUM(CASE WHEN "Trade Result" = 'Loss' AND "Type" = 'Short' THEN "P&L" ELSE 0 END)), 0) AS p_factor_short,
                
            AVG(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Long' THEN "P&L" ELSE NULL END) AS avg_win_long,
            AVG(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Short' THEN "P&L" ELSE NULL END) AS avg_win_short,
                
            AVG(CASE WHEN "Trade Result" = 'Loss' AND "Type" = 'Long' THEN "P&L" ELSE NULL END) AS avg_loss_long,
            AVG(CASE WHEN "Trade Result" = 'Loss' AND "Type" = 'Short' THEN "P&L" ELSE NULL END) AS avg_loss_short,

            SUM(CASE WHEN "Type" = 'Long' THEN 1 ELSE 0 END) AS t_long,
            SUM(CASE WHEN "Type" = 'Short' THEN 1 ELSE 0 END) AS t_short
        FROM TRADE_DATA
        {build_filters(period, tags)}
    """)

    if df.empty:
        return tuple(0 for col in df.columns)
    df = df.fillna(0)
    return tuple(round(df[col].iloc[0], 2) for col in df.columns)

@lru_cache(maxsize=16)
def get_cum_pnl(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> dcc.Graph:
    tags = list(tags)
    df = pdquery(f"""
    SELECT 
                 
    SUM("P&L") OVER (ORDER BY Date, "id") AS "Cumulative P&L",
    Date,
    "Exit Time"
                 
    FROM TRADE_DATA
    {build_filters(period, tags)}
    ORDER BY Date, "id"
    """) 
    
    if df.empty:
        return html.Div("No data for the selected period or tag.")
        
    df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Exit Time'].astype(str))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['DateTime'],
        y=df['Cumulative P&L'],  
        line_shape='spline',
        line_smoothing = 0.5,
        name="Cumulative P&L"
    ))
    return dcc.Graph(figure=fig)

def build_filters(period: str, tags: list[str]) -> str:
    period_filter = get_period_filter(period)
    tag_filter = get_tag_filter(tags)

    if period_filter and tag_filter:
        return period_filter + " AND " + tag_filter.replace("WHERE ", "")
    return period_filter or tag_filter

def get_period_filter(period: str) -> str:
    if period == "monthly":
        return "WHERE strftime('%Y-%m', Date) = strftime('%Y-%m', CURRENT_DATE)"
    elif period == "weekly":
        return "WHERE strftime('%Y-%W', Date) = strftime('%Y-%W', CURRENT_DATE)"
    elif period == "daily":
        return "WHERE DATE(Date) = CURRENT_DATE"
    return ""

def get_tag_filter(tags: list[str]) -> str:
    if not tags:
        return ""
    
    tag_conditions = [
        f'"Tags" ILIKE \'%{tag.replace("'", "''")}%\'' for tag in tags
    ]
    
    return "WHERE " + " OR ".join(tag_conditions)

#simple handy functions
def get_trade_result(pl: float, risk: float, break_even:float=0.1): #10% risk break-even
    if pl > break_even * risk:
        return "Win"
    elif pl < -break_even * risk:
        return "Loss"
    else:
        return "Break-Even"

def percent(var: float) -> str:
    return f"{var:.1f}%"

def eur(var: float) -> str:
    return f"\u20ac{var:.2f}"

def no_updates(n: int) -> list:
    #removes the no update hell xD
    return [no_update]*n