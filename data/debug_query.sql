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

WHERE strftime('%Y-%m', [Date]) = strftime('%Y-%m', 'now')