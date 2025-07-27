SELECT strftime('%Y-%m', "Date") AS month,
       COUNT(*) AS trade_count
FROM TRADE_DATA
GROUP BY month
ORDER BY month;