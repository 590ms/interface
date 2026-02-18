

products = []

with open('products.txt', 'r') as f:
    lines = f.readlines()

for line in lines:
    line_values = line.strip().split(',')
    if len(line_values) != 5:
        print(f"Error: line '{line}' does not contain the expected number of values")
        continue
    code, productname, lprice, xprice, stock = line_values
    products.append(code)
    products.append(productname)
    products.append(lprice)
    products.append(xprice)
    products.append(stock)















