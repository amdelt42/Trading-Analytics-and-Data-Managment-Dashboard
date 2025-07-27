ALTER TABLE TRADE_DATA ADD COLUMN Date_parsed DATE;

UPDATE TRADE_DATA SET Date_parsed = CAST("Date" AS DATE);

-- (Optional) Drop the old Date column
ALTER TABLE TRADE_DATA DROP COLUMN "Date";

-- Rename the new column
ALTER TABLE TRADE_DATA RENAME COLUMN Date_parsed TO "Date";
