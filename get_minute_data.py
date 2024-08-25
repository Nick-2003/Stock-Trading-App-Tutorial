from alpha_vantage.timeseries import TimeSeries
import config 
# https://www.youtube.com/watch?v=RZ_4OI_K6Aw&list=PLvzuUVysUFOuoRna8KhschkVVUo2E2g6G&index=9

def get_minute_data(ticker):
    ts = TimeSeries(key=config.API_KEY, output_format='pandas', indexing_type='date')
    # df, _ = ts.get_intraday(ticker, interval='1min', outputsize='full') # RETURNS RECENT DATES
    df, _ = ts.get_intraday(ticker, interval='1min', outputsize='full', month="2022-06") # FOR TESTING
    df.rename(columns={"1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close", "5. volume": "volume",  "date": "date"}, inplace=True)
    df = df.iloc[::-1]
    return df