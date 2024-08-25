import config 
import sqlite3 
# connection = sqlite3.connect("app.db") # Connect to database
connection = sqlite3.connect(config.DB_FILE) # Connect to database
cursor = connection.cursor() # To execute SQL statements

cursor.executescript("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY, 
        symbol TEXT NOT NULL UNIQUE, 
        name TEXT NOT NULL, 
        exchange TEXT NOT NULL, 
        shortable BOOLEAN NOT NULL
    );
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY, 
        stock_id INTEGER, 
        date NOT NULL, 
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL, 
        volume NOT NULL, 
        sma_20, 
        sma_50, 
        rsi_14,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    );
    CREATE TABLE IF NOT EXISTS strategy (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL 
    );
    CREATE TABLE IF NOT EXISTS stock_strategy (
        stock_id INTEGER NOT NULL, 
        strategy_id INTEGER NOT NULL, 
        FOREIGN KEY (stock_id) REFERENCES stock (id),
        FOREIGN KEY (strategy_id) REFERENCES strategy (id)
    );
    CREATE TABLE IF NOT EXISTS stock_price_minute (
        id INTEGER PRIMARY KEY, 
        stock_id INTEGER, 
        datetime NOT NULL, 
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL, 
        volume NOT NULL, 
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    );
""")
strategies = ["opening_range_breakout", "opening_range_breakdown", "bollinger_bands"]
for strategy in strategies: 
    cursor.execute("INSERT INTO strategy (name) VALUES (?)", (strategy, ))

connection.commit() # To commit changes to databases