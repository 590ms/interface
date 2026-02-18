from tkinter import messagebox
import os 

products= []

def update_memory():
    # We clear the global products list and refill it from the file
    global products
    products.clear() 
    
    if os.path.exists('products.txt'):
        with open('products.txt', 'r') as f:
            for line in f:
                line_values = [v.strip() for v in line.strip().split(',')]
                if len(line_values) == 5:
                    products.extend(line_values)

def delete_product(target_code):
    file_path = 'products.txt'
    if not os.path.exists(file_path):
        return

    # Read all lines and keep only the ones that DON'T match the ID
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    with open(file_path, 'w') as f:
        for line in lines:
            if not line.strip(): continue
            if not line.startswith(f"{target_code},"):
                f.write(line)
    
    # Refresh the global list immediately
    update_memory()



def add_product(target_code, name, lprice, xprice, amount_to_add):
    file_path = 'products.txt'
    all_products = []
    id_exists = False
    name_exists_elsewhere = False
    existing_id_for_name = ""

    # 1. Read and Process
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                if not line.strip(): continue
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) == 5:
                    p_code, p_name, p_lprice, p_xprice, p_stock = parts
                    
                    # CASE: ID MATCHES
                    if p_code == target_code:
                        # We update EVERYTHING to the new inputs, and SUM the stock
                        new_stock = int(p_stock) + int(amount_to_add)
                        all_products.append(f"{target_code}, {name}, {lprice}, {xprice}, {new_stock}\n")
                        id_exists = True
                    
                    # CASE: NAME MATCHES (but different ID)
                    elif p_name.lower() == name.lower():
                        name_exists_elsewhere = True
                        existing_id_for_name = p_code
                        all_products.append(line)
                    
                    else:
                        all_products.append(line)

    # 2. Fail-Safe Logic
    if name_exists_elsewhere and not id_exists:
        choice = messagebox.askyesno("Name Conflict", 
            f"The name '{name}' already exists under ID: {existing_id_for_name}.\n\n"
            f"Do you want to create a NEW entry with ID {target_code}?\n"
            f"(Selecting 'No' will update the existing ID {existing_id_for_name} instead)")
        
        if choice:
            all_products.append(f"{target_code}, {name}, {lprice}, {xprice}, {amount_to_add}\n")
        else:
            # Update the old ID with new prices/name and add quantity
            for i, line in enumerate(all_products):
                if line.startswith(f"{existing_id_for_name},"):
                    parts = [p.strip() for p in line.split(',')]
                    new_qty = int(parts[4]) + int(amount_to_add)
                    # We update name and prices here too
                    all_products[i] = f"{existing_id_for_name}, {name}, {lprice}, {xprice}, {new_qty}\n"
    
    elif not id_exists:
        # COMPLETELY NEW ID AND NAME
        all_products.append(f"{target_code}, {name}, {lprice}, {xprice}, {amount_to_add}\n")

    # 3. Save
    with open(file_path, 'w') as f:
        f.writelines(all_products)


update_memory()




















