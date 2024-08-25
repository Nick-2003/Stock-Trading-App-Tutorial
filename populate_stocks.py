import config 
import sqlite3 
import alpaca_trade_api as tradeapi 
import os

# path = "app.db"
# path = "./app.db" # Ensures that the app.db used is in the same folder as populate_db.py
# path = "/Users/student/database_storage/app.db" # Ensures that the same app.db is used

connection = sqlite3.connect(config.DB_FILE) # Connect to database
connection.row_factory = sqlite3.Row # To get dictionaries instead of tuples
cursor = connection.cursor() # To execute SQL statements

# cursor.executescript("""
#     INSERT INTO stock (symbol, company) VALUES ('ADBE', 'Adobe Inc.'); 
#     INSERT INTO stock (symbol, company) VALUES ('VZ', 'Verizon'); 
#     INSERT INTO stock (symbol, company) VALUES ('Z', 'Zillow'); 
# """)
# connection.commit() # To commit changes to databases

cursor.execute("""
    SELECT symbol, name, exchange FROM stock
""")
rows = cursor.fetchall() # Fetch results of query; returns list of tuples
symbols = [row["symbol"] for row in rows] # Get list of symbols

# https://app.alpaca.markets/paper/dashboard/overview
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL) # config.py variables 
assets = api.list_assets() # Return list of symbols
for asset in assets: 
    # print(asset)
    try: 
        if (asset.status == "active") and (asset.tradable) and (asset.symbol not in symbols): # To avoid overlaps with inactive ones; want only info of interest
            print(f"Added a new stock {asset.symbol} {asset.name}")
            cursor.execute("INSERT INTO stock (symbol, name, exchange, shortable) VALUES (?, ?, ?, ?)", (asset.symbol, asset.name, asset.exchange, asset.shortable))
    except Exception as e: 
        print(asset.symbol) # symbol was set to be unique
        print(e)

connection.commit() # To commit changes to databases