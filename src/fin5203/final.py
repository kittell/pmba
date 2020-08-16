def q10():
    price = 28000
    apr = 0.049
    rate = apr / 12
    term = 60
    
    p = price / term
    paid = 0
    remaining = price
    
    while abs(remaining) > 0.01:
        paid = 0
        remaining = price 
        
        for t in range(term):
            remaining = remaining * (1 + rate) - p
            paid += p
            
        print(p, remaining, paid)
        
        p = p + remaining / t
        
q10()