import sqlite3
import os
import random
from datetime import datetime, timedelta

#define DB path
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "tradedata.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

#create table  duckdb stuff -> #ID INTEGER PRIMARY KEY AUTOINCREMENT,
conn.execute("""
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

#dummy data generation
tickers = ['AAPL', 'TSLA', 'GOOG', 'AMZN', 'MSFT', 'META', 'NVDA', 'AMD']
types = ['Long', 'Short']
tags_pool = ['Breakout', 'Reversal', 'Momentum', 'News', 'Scalp', 'Swing']
base_date = datetime.today() - timedelta(days=100)

rows = []
for i in range(100):
    date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
    ticker = random.choice(tickers)
    trade_type = random.choice(types)
    entry = round(random.uniform(50, 500), 2)
    exit_price = round(entry * random.uniform(0.95, 1.05), 2)
    entry_time = f"{random.randint(9, 10)}:{random.randint(0, 59):02d}"
    exit_time = f"{random.randint(14, 15)}:{random.randint(0, 59):02d}"
    risk = round(random.uniform(1, 40), 2)
    pnl = round((exit_price - entry) * (5 if trade_type == "Long" else -5), 2)
    fees = round(random.uniform(0.5, 5.0), 2)
    tags = ", ".join(random.sample(tags_pool, k=random.randint(1, 3)))
    grade = random.randint(1, 10)
    image = None

    rows.append((date, ticker, trade_type, entry, exit_price, entry_time, exit_time,
                 risk, pnl, fees, tags, grade, image))

#insert into table
cursor.executemany("""
INSERT INTO TRADE_DATA
    ("Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
""", rows)
conn.commit()
conn.close()
