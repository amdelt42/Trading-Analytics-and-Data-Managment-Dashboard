import duckdb
import os
import random
from datetime import datetime, timedelta

def get_trade_result(pl: float, risk: float, break_even: float = 0.1):
    if pl > break_even * risk:
        return "Win"
    elif pl < -break_even * risk:
        return "Loss"
    else:
        return "Break-Even"


db_path = os.path.join(os.path.dirname(__file__), "..", "data", "tradedata.duckdb")
conn = duckdb.connect(database=db_path)

conn.execute("""
CREATE TABLE IF NOT EXISTS TRADE_DATA (
    id INTEGER PRIMARY KEY,
    "Date" DATE,
    "Ticker" TEXT,
    "Type" TEXT,
    "Entry" DECIMAL(10, 2),
    "Exit" DECIMAL(10, 2),
    "Entry Time" TIME,
    "Exit Time" TIME,
    "Risk" DECIMAL(10, 2),
    "P&L" DECIMAL(10, 2),
    "Fees" DECIMAL(10, 2),
    "Tags" TEXT,
    "Grade" INTEGER,
    "Image" BLOB,
    "Trade Result" VARCHAR(10)
)

""")

conn.execute("CREATE SEQUENCE IF NOT EXISTS id START 1")

tickers = ['AAPL', 'TSLA', 'GOOG', 'AMZN', 'MSFT', 'META', 'NVDA', 'AMD', 'LUNR', 'COCA']
types = ['Long', 'Short']
tags_pool = ['Breakout', 'Reversal', 'Momentum', 'News', 'Scalp', 'Swing']
base_date = datetime.today() - timedelta(days=100)

rows = []
for i in range(100):
    date = (base_date + timedelta(days=i)).date()
    num_trades_today = random.randint(1, 3)

    #market open
    current_time = datetime.combine(date, datetime.strptime("09:00", "%H:%M").time())
    market_close = datetime.combine(date, datetime.strptime("16:00", "%H:%M").time())

    for _ in range(num_trades_today):
        if current_time >= market_close:
            break

        #trade duration
        trade_duration = timedelta(minutes=random.randint(30, 90))
        entry_dt = current_time
        exit_dt = entry_dt + trade_duration

        #market close
        if exit_dt > market_close:
            break

        current_time = exit_dt + timedelta(minutes=random.randint(5, 15))

        entry_time = entry_dt.strftime("%H:%M:%S")
        exit_time = exit_dt.strftime("%H:%M:%S")

        ticker = random.choice(tickers)
        trade_type = random.choice(types)
        entry = round(random.uniform(50, 500), 2)
        exit_price = round(entry * random.uniform(0.95, 1.05), 2)
        risk = round(random.uniform(1, 40), 2)
        fees = round(random.uniform(0.5, 5.0), 2)

        pnl = round(((exit_price - entry) * (5 if trade_type == "Long" else -5)) - fees, 2)
        tags = ", ".join(random.sample(tags_pool, k=random.randint(1, 3)))
        grade = random.randint(1, 10)
        image = None
        trade_result = get_trade_result(pnl, risk)

        rows.append((date, ticker, trade_type, entry, exit_price, entry_time, exit_time,
                     risk, pnl, fees, tags, grade, image, trade_result))


conn.executemany("""
INSERT INTO TRADE_DATA
    ("id","Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image", "Trade Result")
VALUES (nextval('id'),?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print("Dummy data inserted successfully.")
