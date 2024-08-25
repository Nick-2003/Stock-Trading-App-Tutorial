import config 
import alpaca_trade_api as tradeapi
from helpers import calculate_quantity
from get_minute_data import get_minute_data

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL, api_version = "v2") # config.py variables 

symbols = [] # FILL THIS IN WITH SYMBOLS OF INTEREST

# for symbol in symbols: 
#     quote = api.get_last_quote(symbol)
#     try: 
#         api.submit_order(
#             symbol=symbol,
#             side='buy',
#             type='market',
#             # qty='100',
#             qty=calculate_quantity(quote.bidprice),
#             time_in_force='day',
#             order_class='bracket',
#         )
#     except Exception as e:
#         print(f"Cannot submit order {e}")

# orders = api.list_orders()
# positions = api.list_positions()

def get_day_data(ticker):
    ts = TimeSeries(key=config.API_KEY, output_format='pandas', indexing_type='date')
    # df, _ = ts.get_intraday(ticker, interval='1min', outputsize='full') # RETURNS RECENT DATES
    df, _ = ts.get_daily(ticker, outputsize='full') # FOR TESTING
    df.rename(columns={"1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close", "5. volume": "volume",  "date": "date"}, inplace=True)
    df = df.iloc[::-1]
    return df

for symbol in symbols: 
#     try: 
#         api.submit_order(
#             symbol=symbol,
#             side='sell',
#             type='trailing_stop',
#             qty=calculate_quantity(quote.bidprice)/2,
#             time_in_force='day',
#             trail_price=0.5
#         ) 
#     except Exception as e:
#         print(f"Cannot submit order {e}")
        
#     try: 
#         api.submit_order(
#             symbol=symbol,
#             side='sell',
#             type='trailing_stop',
#             qty=calculate_quantity(quote.bidprice)/2,
#             time_in_force='day',
#             trail_percent=0.75
#         ) 
#     except Exception as e:
#         print(f"Cannot submit order {e}")

    daily_bars = get_day_data(symbol).tz_localize('US/Eastern')
    atr = talib.ATR(daily_bars.high.value, daily_bars.low.value, daily_bars.close.value, timeperiod=14)
    print(atr)