import config 
import sqlite3 
import pandas 
import csv 
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries
from dateutil.relativedelta import relativedelta

connection = sqlite3.connect(config.DB_FILE) # Connect to database
connection.row_factory = sqlite3.Row # To get dictionaries instead of tuples
cursor = connection.cursor() # To execute SQL statements

# ISSUE: MAY NOT BE ABLE TO ACCESS datetime WITH THIS FUNCTION
def get_minute_data_pop(ticker, month):
    ts = TimeSeries(key=config.API_KEY, output_format='pandas', indexing_type='date')
    # df, _ = ts.get_intraday(ticker, interval='1min', outputsize='full') # RETURNS RECENT DATES
    df, _ = ts.get_intraday(ticker, interval='1min', outputsize='full', month=month) # FOR TESTING
    df.rename(columns={"1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close", "5. volume": "volume",  "date": "date"}, inplace=True)
    df = df.iloc[::-1]
    return df

symbols = []
stock_dict = {} # Easy access of symbol and corresponding id
with open("qqq.csv") as f: 
    reader = csv.reader(f)
    for line in reader: 
        symbols.append(line[1])
cursor.execute("""
    SELECT * FROM stock
""")
stocks = cursor.fetchall() # Fetch results of query; returns list of tuples
for stock in stocks: 
    symbol = stock['symbol']
    stock_dict[symbol] = stock["id"]

valid_symbols = list(set(symbols).intersection(list(stock_dict.keys()))) # Ensure that stock id can be obtained
print(len(valid_symbols))

for symbol in valid_symbols: 
    start_date = datetime(2020, 1, 6).date() # Can change accordingly
    end_date_range = datetime(2020, 11, 20).date() # Can change accordingly
    while start_date < end_date_range: 
        # end_date = start_date + timedelta(days = 4) # ISSUE: Cannot access specific week with get_intraday(), will likely have to do whole month
        yearmonth = start_date.strftime('%Y-%m')
        print(f"===Fetching minute bars for {symbol} in year and month {yearmonth}==")
        api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL, api_version = "v2") # config.py variables 
        minute_bars = get_minute_data_pop(symbol, yearmonth).tz_localize('US/Eastern').resample("1min").ffill() # Results not guranteed
    
        # Index is timestamp, row is stock data
        for index, row in minute_bars.iterrows(): 
            # print(index) 
            # print(row) 
            cursor.execute("""
                INSERT INTO stock_price_minute (stock_id, datetime, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_dict[symbol], index.isoformat(), row["open"], row["high"], row["low"], row["close"], row["volume"]))
            # cursor.execute("""
            #     INSERT INTO stock_price_minute (stock_id, datetime, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)
            # """, (None, None, row["open"], None, None, None, None))
        
        # start_date = start_date + timedelta(days = 7) # Increment only after all other code has run
        start_date = start_date + relativedelta(months=1)

connection.commit() # To commit changes to databases