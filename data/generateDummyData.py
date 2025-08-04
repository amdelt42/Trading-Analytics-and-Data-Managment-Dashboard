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

from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "tradedata.duckdb"

if db_path.exists():
    os.remove(db_path)
    print(f"✅ Deleted existing database: {db_path}")
else:
    print(f"ℹ️ No existing database found at: {db_path}")

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
n_days = 365*1.5
tickers = ['AAPL', 'TSLA', 'GOOG', 'AMZN', 'MSFT', 'META', 'NVDA', 'AMD', 'LUNR', 'COCA']
types = ['Long', 'Short']
tags_pool = ['Breakout', 'Reversal', 'Momentum', 'News', 'Scalp', 'Swing']
base_date = datetime.today() - timedelta(days=n_days)

rows = []
date_counter = 0
max_trades_per_day = 3  # Hard limit

while (base_date + timedelta(days=date_counter)).date() <= datetime.today().date():
    date = (base_date + timedelta(days=date_counter)).date()
    date_counter += 1
    
    # Skip weekends
    if date.weekday() >= 5:
        continue
        
    # Market hours
    market_open_time = datetime.strptime("09:30", "%H:%M").time()
    market_close_time = datetime.strptime("16:00", "%H:%M").time()
    market_open = datetime.combine(date, market_open_time)
    market_close = datetime.combine(date, market_close_time)
    
    num_trades_today = random.randint(0, max_trades_per_day)  
    current_time = market_open
    
    trades_today = 0
    
    while trades_today < num_trades_today and current_time < market_close:
        # Calculate trade duration (longer trades for more realistic P&L)
        trade_duration = timedelta(minutes=random.randint(1, 49)) 
        
        entry_dt = current_time
        exit_dt = entry_dt + trade_duration
        
        # Don't let trades go past market close
        if exit_dt > market_close:
            exit_dt = market_close
            trade_duration = exit_dt - entry_dt
            # Skip if trade would be too short
            if trade_duration < timedelta(minutes=30):
                break
        
        entry_time = entry_dt.time()
        exit_time = exit_dt.time()
        
        ticker = random.choice(tickers)
        trade_type = random.choice(types)
        entry = round(random.uniform(50, 500), 2)
        
        # More realistic P&L based on risk
        risk = round(random.uniform(5, 20), 2)
        risk_multiplier = random.uniform(-2, 2.3)  # Win/loss size relative to risk
        
        # Calculate exit price based on risk
        if trade_type == "Long":
            exit_price = entry * (1 + (risk_multiplier * risk / 100))
        else:
            exit_price = entry * (1 - (risk_multiplier * risk / 100))
            
        exit_price = round(exit_price, 2)
        fees = round(random.uniform(0.5, 5.0), 2)
        
        # Calculate P&L based on position size (risk-based)
        position_size = 300  # Fixed size for simplicity
        pnl = round((exit_price - entry) * (position_size/entry) * (1 if trade_type == "Long" else -1) - fees, 2)
        
        tags = ", ".join(random.sample(tags_pool, k=random.randint(1, 3)))
        grade = random.randint(1, 10)
        image = None
        trade_result = get_trade_result(pnl, risk)
        
        rows.append((date, ticker, trade_type, entry, exit_price, entry_time.strftime("%H:%M:%S"), 
                     exit_time.strftime("%H:%M:%S"), risk, pnl, fees, tags, grade, image, trade_result))
        
        trades_today += 1
        
        # Move time forward (minimum 15 min between trades)
        current_time = exit_dt + timedelta(minutes=random.randint(15, 120))
    print(f"Generated {trades_today} trades for {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")  # Debug output

conn.executemany("""
INSERT INTO TRADE_DATA
    ("id","Date", "Ticker", "Type", "Entry", "Exit", "Entry Time", "Exit Time", "Risk", "P&L", "Fees", "Tags", "Grade", "Image", "Trade Result")
VALUES (nextval('id'),?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print(f"Dummy data inserted succesfully")