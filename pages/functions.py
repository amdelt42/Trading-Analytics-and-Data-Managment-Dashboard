#pages\functions.py
import duckdb
import math
import base64
import pandas as pd

from pathlib import Path
from dash import no_update
from functools import lru_cache

from dash import html, dcc
import plotly.graph_objects as go
#import plotly.express as px

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
            100.0 * SUM(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Long' THEN 1 ELSE 0 END) / SUM(CASE WHEN "Type" = 'Long' THEN 1 ELSE 0 END) AS long_wr,
            100.0 * SUM(CASE WHEN "Trade Result" = 'Win' AND "Type" = 'Short' THEN 1 ELSE 0 END) / SUM(CASE WHEN "Type" = 'Short' THEN 1 ELSE 0 END) AS short_wr,
                
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
            SUM(CASE WHEN "Type" = 'Short' THEN 1 ELSE 0 END) AS t_short,
                 
            SUM(CASE WHEN "Type" = 'Long' AND "Trade Result" = 'Win' THEN 1 ELSE 0 END) AS t_win_long,
            SUM(CASE WHEN "Type" = 'Short' AND "Trade Result" = 'Win' THEN 1 ELSE 0 END) AS t_win_short,
                 
            SUM(CASE WHEN "Type" = 'Long' AND "Trade Result" = 'Loss' THEN 1 ELSE 0 END) AS t_loss_long,
            SUM(CASE WHEN "Type" = 'Short' AND "Trade Result" = 'Loss' THEN 1 ELSE 0 END) AS t_loss_short
        FROM TRADE_DATA
        {build_filters(period, tags)}
    """)

    if df.empty:
        return tuple(0 for col in df.columns)
    df = df.fillna(0)
    return tuple(round(df[col].iloc[0], 2) for col in df.columns)

def get_tradeFreq_hist(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> dcc.Graph:
    df = pdquery(f"""
    WITH daily_counts AS (
        SELECT 
            strftime('%w', Date) AS weekday,
            Date,
            COUNT(*) AS trades_on_day
        FROM TRADE_DATA
        {build_filters(period, tags)}
        GROUP BY Date
    )
    SELECT 
        weekday,
        AVG(trades_on_day) AS "Trades per Day"
    FROM daily_counts
    GROUP BY weekday
    """)

    if df.empty:
        return ""

    weekday_map = {'0': 'Sun', '1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu', '5': 'Fri', '6': 'Sat'}
    df['Week Day'] = df['weekday'].map(weekday_map)

    fig = go.Figure()

    #positive P&L (green)
    fig.add_trace(go.Histogram(
        x=df["Week Day"],
        y=df["Trades per Day"],
        histfunc="avg",
        name="Trades per Day"
    ))

    fig.update_layout(
        xaxis_title="Week Day",
        yaxis_title="Average Trades Per Day"  
    )

    return dcc.Graph(figure=fig)
def get_tradeDur_hist(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> dcc.Graph:
    df = pdquery(f"""
    SELECT 
        EXTRACT(EPOCH FROM (
        CAST("Date" || ' ' || "Exit Time" AS TIMESTAMP) -
        CAST("Date" || ' ' || "Entry Time" AS TIMESTAMP)
        ))/60 AS "Trade Duration", --in minutes
                 
        "P&L"/"Risk" AS "RR"
    FROM TRADE_DATA
    {build_filters(period, tags)}
    """)

    if df.empty:
        return ""
    
    bin_width= 0.5
    nbins = math.ceil((df["RR"].max() - df["RR"].min()) / bin_width)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df["RR"],
        y=df["Trade Duration"],
        histfunc="avg",
        name="Trade Duration",
        nbinsx=nbins
    ))

    fig.update_layout(
        xaxis_title="RR",
        yaxis_title="Average Trade Duration",
        yaxis_type="log"  
    )

    return dcc.Graph(figure=fig)
def get_marketDist_hist(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> dcc.Graph:
    filters = build_filters(period, tags)

    if filters:
        filters += " AND \"Trade Result\" <> 'Break-Even'"
    else:
        filters = "WHERE \"Trade Result\" <> 'Break-Even'"

    df = pdquery(f"""
    SELECT  
        "P&L",
        "Exit Time" AS "Market Hour"
    FROM TRADE_DATA
    {filters}
    """)
    
    if df.empty:
        return ""

    df['Market Hour (sec)'] = pd.to_timedelta(df["Market Hour"].astype(str)).dt.total_seconds()
    df_positive = df[df["P&L"] > 0]
    df_negative = df[df["P&L"] < 0] 

    fig = go.Figure()

    #positive P&L (green)
    fig.add_trace(go.Histogram(
        x=df_positive["Market Hour (sec)"],
        y=df_positive["P&L"],
        histfunc="avg",
        name="Positive P&L",
        marker_color="green",
        xbins=dict(
            start=0,
            end=24 * 3600, 
            size=1800
        ),
        opacity=0.5
    ))

    #negative P&L (red)
    fig.add_trace(go.Histogram(
        x=df_negative["Market Hour (sec)"],
        y=-1*df_negative["P&L"],
        histfunc="avg",
        name="Negative P&L",
        marker_color="red",
        xbins=dict(
            start=0,
            end=24 * 3600, 
            size=1800
        ),
        opacity=0.5
    ))

    fig.update_layout(
        barmode='overlay',
        xaxis=dict(
            tickmode='array',
            tickvals=[i * 3600 for i in range(0, 25)],
            ticktext=[f"{i:02d}:00" for i in range(0, 25)]
        ),
        xaxis_title="Market Hour",
        yaxis_title="Average P&L",
        yaxis_type="log"  
    )

    return dcc.Graph(figure=fig)

@lru_cache(maxsize=16)
def get_cum_pnl(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> Tuple[dcc.Graph, pd.DataFrame]:
    tags = list(tags)
    df = pdquery(f"""
    SELECT            
        SUM("P&L") OVER (ORDER BY Date, "id") AS "Cumulative P&L",
        SUM(CASE WHEN "Type" = 'Long' THEN "P&L" ELSE 0 END) OVER (ORDER BY Date, "id") As "Cumulative P&L Long",
        SUM(CASE WHEN "Type" = 'Short' THEN "P&L" ELSE 0 END) OVER (ORDER BY Date, "id") As "Cumulative P&L Short",
        Date,
        "Exit Time"      
    FROM TRADE_DATA
    {build_filters(period, tags)}
    ORDER BY Date, "id"
    """) 
    
    if df.empty:
        return html.Div("No data for the selected period or tag."), pd.DataFrame()
        
    df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Exit Time'].astype(str))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['DateTime'],
        y=df['Cumulative P&L'],  
        line_shape='spline',
        line_smoothing = 0.25,
        name="Cumulative P&L"
    ))
    return dcc.Graph(figure=fig), df
def get_cum_stats(period: Optional[str] = None, tags: Optional[Tuple[str, ...]] = ()) -> tuple:
    _, df = get_cum_pnl(period, tags)
    
    if df.empty:
        return 0.0, 0.0, 0.0

    df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Exit Time'].astype(str))
    df['Cummax'] = df['Cumulative P&L'].cummax()
    df['Drawdown'] = df['Cumulative P&L'] - df['Cummax']
    max_dd = -df['Drawdown'].min()

    df['Cummax Long'] = df['Cumulative P&L Long'].cummax()
    df['Drawdown Long'] = df['Cumulative P&L Long'] - df['Cummax Long']
    max_dd_long = -df['Drawdown Long'].min()

    df['Cummax Short'] = df['Cumulative P&L Short'].cummax()
    df['Drawdown Short'] = df['Cumulative P&L Short'] - df['Cummax Short']
    max_dd_short = -df['Drawdown Short'].min()
    return round(max_dd, 2), round(max_dd_long, 2), round(max_dd_short, 2)

def build_filters(period: str, tags: list[str]) -> str:
    period_filter = get_period_filter(period)
    tag_filter = get_tag_filter(tags)

    if period_filter and tag_filter:
        return period_filter + " AND " + tag_filter.replace("WHERE ", "")
    return period_filter or tag_filter
def get_period_filter(period: str) -> str:
    if period == "1m":
        return "WHERE Date >= CURRENT_DATE - INTERVAL '1 month'"
    elif period == "1w":
        return "WHERE Date >= CURRENT_DATE - INTERVAL '1 week'"
    elif period == "1d":
        return "WHERE Date >= CURRENT_DATE - INTERVAL '1 day'"
    elif period == "ytd":
        return "WHERE strftime('%Y', Date) = strftime('%Y', CURRENT_DATE)"
    elif period == "1y":
        return "WHERE Date >= CURRENT_DATE - INTERVAL '1 year'"
    else:
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