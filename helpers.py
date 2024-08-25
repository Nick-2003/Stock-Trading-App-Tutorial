import math 
PAPER_AMT = 100000
def calculate_quantity(price): 
    quantity = math.floor(PAPER_AMT/price)
    return quantity