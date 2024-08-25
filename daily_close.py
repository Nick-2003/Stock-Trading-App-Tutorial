import alpaca_trade_api as tradeapi
import config 

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL, api_version = "v2") # config.py variables 
response = api.close_all_positions()
print(response)