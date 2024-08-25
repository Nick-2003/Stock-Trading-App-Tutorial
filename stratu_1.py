# import yfinance 
# df = yfinance.download("AAPL", start="2020-01-01", end="2020-10-02")
# df.to_csv("AAPL.csv")
import talib 
import numpy
import collections
import datetime

dict = {"A": {"o": 1, "h": 2, "l": -1, "c": 1}, "B": {"o": 2, "h": 10, "l": 0, "c": 3}, "C": {"o": 2, "h": 2, "l": 1, "c": 1}}

print(dict)
print(dict["A"])
print(dict["A"]["c"])
print(dict["B"]["c"])

print(talib.SMA(numpy.array([1.0, 2.0, 3.0, 4.0]),3)) # [nan nan  2.  3.]
print(talib.SMA(numpy.array([1.0, 2.0, 3.0, 4.0]),3)[-1]) # 3.0

print(talib.RSI(numpy.array([1.0, 2.0, 3.0, 4.0]),3)) # [ nan  nan  nan 100.]
print(talib.RSI(numpy.array([1.0, 2.0, 3.0, 4.0]),3)[-1]) # 100.0

# For splitting barsets by their symbol
dict_list = [{"o": 1, "h": 2, "l": -1, "c": "1"}, {"o": 2, "h": 10, "l": 0, "c": "3"}, {"o": 2, "h": 2, "l": 1, "c": "1"}]
print(dict_list)
result = collections.defaultdict(list)
for d in dict_list:
    result[d['c']].append(d)
print(result)
print(result["1"])
print(len(result["1"]))
for r in result: 
    print(r)

for d in [1, 2, 3]:
    for q in [3, 2, 3]: 
        list1 = [] 
        if d == q:
            list1.append(d)
        print(list1) # list1 resets each time

current_date = datetime.datetime.strptime("2022-04-21", '%Y-%m-%d').date()
print(current_date)