import config 
import sqlite3 
import alpaca_trade_api as tradeapi 
from alpaca_trade_api.rest import TimeFrame
import datetime as dt
import pytz
import numpy
import talib 
import collections

connection = sqlite3.connect(config.DB_FILE) # Connect to database
connection.row_factory = sqlite3.Row # To get dictionaries instead of tuples
cursor = connection.cursor() # To execute SQL statements

# cursor.execute("""
#     SELECT id, symbol, name FROM stock
# """) # Need to account for alpaca_trade_api.rest.APIError: invalid symbol: BCH/USD
cursor.execute("""
    SELECT id, symbol, name FROM stock WHERE symbol NOT LIKE ("%/%")
""")
rows = cursor.fetchall() # Fetch results of query; returns list of tuples
# print(rows)
# symbols = [row["symbol"] for row in rows] # Get list of symbols

symbols = []
stock_dict = {} # Easy access of symbol and corresponding id
for row in rows: 
    symbol = row["symbol"]
    symbols.append(symbol) 
    stock_dict[symbol] = row["id"]
# print(stock_dict)

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL, api_version = "v2") # config.py variables 

timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
# current_date = timeNow.date().isoformat()
current_date = dt.datetime.strptime("2022-06-21", '%Y-%m-%d').date()
# oneDayAgo = (timeNow - dt.timedelta(days=1)).strftime('%Y-%m-%d')
oneDayAgo = (timeNow - dt.timedelta(days=1)).isoformat()

chunk_size = 200 # Iterate over data, 200 at a time
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]

    #  Need to acquire list of most recent closes for SMA 
    # barsets = api.get_bars(symbol_chunk, TimeFrame.Day, start = oneDayAgo, end = oneDayAgo, limit = 1)._raw # Results not guranteed
    barsets = api.get_bars(symbol_chunk,TimeFrame.Day,"2022-03-21", "2022-06-21")._raw
    barsets_final = collections.defaultdict(list) # Obtain barsets split by symbol
    for bar in barsets:
        barsets_final[bar['S']].append(bar)
    # print(barsets[:10])
    # print(barsets_final)
    # print(list(barsets_final.keys()))

    for symbol in list(barsets_final.keys()): # For each symbol
        recent_closes = [bar["c"] for bar in barsets_final[symbol]]
        for bar in barsets_final[symbol]: # Loop through each bar in barset of given symbol
            print(f"processing symbol {symbol}")
            # print(bar)
            stock_id = stock_dict[bar["S"]]
            stock_time = dt.datetime.strptime(bar["t"], '%Y-%m-%dT%H:%M:%SZ').date()
            # NEED TO FIND WHERE current_date WAS IN THE VIDEO
            # print(type(recent_closes))
            # print(type(numpy.array(recent_closes)))
            if len(recent_closes) >= 50 and current_date == stock_time:
                sma_20 = talib.SMA(numpy.array(recent_closes, dtype=numpy.float64), 20)[-1]
                sma_50 = talib.SMA(numpy.array(recent_closes, dtype=numpy.float64), 50)[-1]
                rsi_14 = talib.RSI(numpy.array(recent_closes, dtype=numpy.float64), 14)[-1]
            else: 
                sma_20, sma_50, rsi_14 = None, None, None
            
            cursor.execute("""
            INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, stock_time, bar["o"], bar["h"], bar["l"], bar["c"], bar["v"], sma_20, sma_50, rsi_14))
    
connection.commit() # To commit changes to databases