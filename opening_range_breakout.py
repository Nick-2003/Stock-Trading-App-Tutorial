import sqlite3 
import config 
import alpaca_trade_api as tradeapi
import datetime 
import pytz
import pandas as pd
import smtplib, ssl
from timezone import is_dst
from get_minute_data import get_minute_data
from helpers import calculate_quantity

# # Create a secure SSL context
# context = ssl.create_default_context()

connection = sqlite3.connect(config.DB_FILE) 
connection.row_factory = sqlite3.Row 
cursor = connection.cursor() 

cursor.execute("""
    SELECT id FROM strategy WHERE name = "opening_range_breakout"
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

current_date = datetime.date.today().isoformat()
# if is_dst(): 
#     start_minute_bar = f"{current_date} 09:30:00-05:00"
#     end_minute_bar = f"{current_date} 09:45:00-05:00"
# else: 
#     start_minute_bar = f"{current_date} 09:30:00-04:00"
#     end_minute_bar = f"{current_date} 09:45:00-04:00"

start_minute_bar = pd.to_datetime(f"{current_date} 09:30:00", utc = False).tz_localize('US/Eastern')
end_minute_bar = pd.to_datetime(f"{current_date} 16:00:00", utc = False).tz_localize('US/Eastern')

orders = api.list_orders(status="all", after=f"{current_date}T13:30:00Z")
# existing_order_symbols = [order.symbol for order in orders]
existing_order_symbols = [order.symbol for order in orders if order.status != "canceled"]

messages = []

for symbol in symbols: 
    # minute_bars = api.polygon.historic_agg_v2(symbol, 1, "minute", _from = current_date, to = current_date).df # CANNOT BE APPLIED DUE TO NEEDING POLYGON
    minute_bars = get_minute_data(symbol).tz_localize('US/Eastern') # Fetch minute bars for each stock symbol 
    # print(symbol)
    # print(minute_bars) # Minute bars for given time range

    print(start_minute_bar) # String 
    print(minute_bars.index) # Date time
    
    # Obtain first 15 minutes 
    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    print(opening_range_bars)

    # Obtain range of values within first 15 minutes (Maximum high, minimum low)
    opening_range_low = opening_range_bars["low"].min()
    opening_range_high = opening_range_bars["high"].max()
    opening_range = opening_range_high - opening_range_low
    # print(opening_range_low)
    # print(opening_range_high)
    # print(opening_range)

    # After first 15 minutes 
    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]
    after_opening_bar_breakout = after_opening_range_bars[after_opening_range_bars["close"] > opening_range_high]
    
    if not after_opening_bar_breakout.empty: 
        if symbol not in existing_order_symbols: 
            limit_price = after_opening_bar_breakout.iloc[0]["close"]
            print(f"Placing order for {symbol} at {limit_price}, closed above {opening_range_high} at {after_opening_bar_breakout.iloc[0]}")

            messages.append(f"Placing order for {symbol} at {limit_price}, closed above {opening_range_high}\n\n{after_opening_bar_breakout.iloc[0]}\n\n")

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
                        limit_price=limit_price + opening_range,
                    ),
                    stop_loss=dict(
                        stop_price=limit_price - opening_range,
                    )
                )
            except Exception as e:
                print(f"Cannot submit order {e}")
        else: 
            print(f"Already an order for {symbol}, will skip.")


# with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
#     server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
#     # TODO: Send email here
#     email_message = f"Subject Trade Notifications for {current_date}\n\n"
#     email_message += "\n\n".join(messages)
#     server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS) # Send email from self to self
#     server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_SMS) # Send SMS