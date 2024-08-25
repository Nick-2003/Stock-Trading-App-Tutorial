import sqlite3 
import config 
import alpaca_trade_api as tradeapi
import datetime 
import pytz
import pandas as pd
from timezone import is_dst
from get_minute_data import get_minute_data
# import smtplib, ssl # Notifications
import talib 
from helpers import calculate_quantity

# # Create a secure SSL context
# context = ssl.create_default_context()

connection = sqlite3.connect(config.DB_FILE) 
connection.row_factory = sqlite3.Row 
cursor = connection.cursor() 

cursor.execute("""
    SELECT id FROM strategy WHERE name = "bollinger_bands"
""")
strategy_id = cursor.fetchone()["id"]

cursor.execute("""
    SELECT symbol, name 
    FROM stock JOIN stock_strategy ON stock_strategy.stock_id = stock.id 
    WHERE stock_strategy.strategy_id = ? 
""", (strategy_id, ))
stocks = cursor.fetchall()
symbols = [stock["symbol"] for stock in stocks] # Obtain stock symbols of interest
# print(symbols)

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL, api_version = "v2") # config.py variables 

# current_date = datetime.date.today().isoformat()
current_date = datetime.datetime.strptime("2022-06-21", '%Y-%m-%d').date()

# if is_dst(): 
#     start_minute_bar = pd.to_datetime(f"{current_date} 09:30:00-05:00")
#     end_minute_bar = pd.to_datetime(f"{current_date} 16:00:00-05:00")
# else: 
#     start_minute_bar = pd.to_datetime(f"{current_date} 09:30:00-04:00")
#     end_minute_bar = pd.to_datetime(f"{current_date} 16:00:00-04:00")
start_minute_bar = pd.to_datetime(f"{current_date} 09:30:00", utc = False).tz_localize('US/Eastern')
end_minute_bar = pd.to_datetime(f"{current_date} 16:00:00", utc = False).tz_localize('US/Eastern')

# print(start_minute_bar)
# print(type(start_minute_bar))

orders = api.list_orders(status="all", after=f"{current_date}T13:30:00Z")
# existing_order_symbols = [order.symbol for order in orders]
existing_order_symbols = [order.symbol for order in orders if order.status != "canceled"]

messages = []
# print(symbols)

for symbol in symbols: 
    # minute_bars = api.polygon.historic_agg_v2(symbol, 1, "minute", _from = current_date, to = current_date).df # CANNOT BE APPLIED DUE TO NEEDING POLYGON
    minute_bars = get_minute_data(symbol).tz_localize('US/Eastern') # Fetch minute bars for each stock symbol 

    # print(minute_bars.index) # ['2024-07-15 07:07:00', '2024-07-15 07:11:00', ...]
    
    # Obtain first 15 minutes 
    market_open_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    market_open_bars = minute_bars.loc[market_open_mask]
    # print(market_open_bars)
    
    if len(market_open_bars) >= 20: 
        closes = market_open_bars["close"].values
        # closes = market_open_bars.close.values
        print(closes)

        upper, middle, lower = talib.BBANDS(closes, 20, 2, 2)
        current_candle = market_open_bars.iloc[-1]
        previous_candle = market_open_bars.iloc[-2]

        if current_candle.close > lower[-1] and previous_candle.close < lower[-2]: 
            print(f"{symbol} closed above lower Bollinger band")
            print(current_candle)
            
            if symbol not in existing_order_symbols: 
                limit_price = current_candle.close
                candle_range = current_candle.high - current_candle.close
                print(f"Placing order for {symbol} at {limit_price}")
    
                messages.append(f"Placing order for {symbol} at {limit_price}")

                try: 
                    api.submit_order(
                        symbol=symbol,
                        side='buy',
                        type='limit',
                        # qty='100',
                        qty=calculate_quantity(limit_price),
                        time_in_force='day',
                        order_class='bracket',
                        limit_price=limit_price,
                        take_profit=dict(
                            limit_price=limit_price + (candle_range * 3),
                        ),
                        stop_loss=dict(
                            stop_price=previous_candle.low,
                        )
                    )
                except Exception as e:
                    print(f"Cannot submit order {e}")
            else: 
                print(f"Already an order for {symbol}, will skip.")
    