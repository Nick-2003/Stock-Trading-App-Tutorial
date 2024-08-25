import config 
import sqlite3 
# connection = sqlite3.connect("app.db") # Connect to database
connection = sqlite3.connect(config.DB_FILE) # Connect to database
cursor = connection.cursor() # To execute SQL statements

cursor.executescript("""
    DELETE FROM stock;
    DELETE FROM stock_price;
    DELETE FROM strategy;
    DELETE FROM stock_strategy; 
""")
connection.commit() # To commit changes to databases