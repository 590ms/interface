import mysql.connector
from tkinter import messagebox

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678', 
    'database': 'shop_db' 
}

products = []

def get_connection():
    return mysql.connector.connect(**db_config)

def update_memory():
    global products
    products.clear()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Selecting: ID, Name, Retail, Wholesale, Stock
        cursor.execute("SELECT product_id, name, retail_price, wholesale_price, stock_count FROM products")
        rows = cursor.fetchall()
        for row in rows:
            # Flatten into the list format your frontend expects [id, name, retail, whole, stock, id, name...]
            products.extend([str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4])])
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

def delete_product(target_code):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (target_code,))
        conn.commit()
        conn.close()
        update_memory()
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete: {e}")

def add_product(target_code, name, lprice, xprice, amount_to_add):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if ID exists
        cursor.execute("SELECT stock_count FROM products WHERE product_id = %s", (target_code,))
        id_row = cursor.fetchone()
        
        # Check if Name exists elsewhere
        cursor.execute("SELECT product_id, stock_count FROM products WHERE name = %s AND product_id != %s", (name, target_code))
        name_row = cursor.fetchone()

        if id_row:
            # CASE: ID MATCHES - Update and sum stock
            new_stock = int(id_row[0]) + int(amount_to_add)
            cursor.execute("""UPDATE products SET name=%s, retail_price=%s, wholesale_price=%s, stock_count=%s 
                           WHERE product_id=%s""", (name, lprice, xprice, new_stock, target_code))
        
        elif name_row:
            # CASE: NAME MATCHES (different ID)
            existing_id = name_row[0]
            choice = messagebox.askyesno("Name Conflict", 
                f"The name '{name}' already exists under ID: {existing_id}.\n\n"
                f"Do you want to create a NEW entry with ID {target_code}?\n"
                f"(Selecting 'No' will update the existing ID {existing_id} instead)")
            
            if choice:
                cursor.execute("INSERT INTO products VALUES (%s, %s, %s, %s, %s)", 
                               (target_code, name, lprice, xprice, amount_to_add))
            else:
                new_stock = int(name_row[1]) + int(amount_to_add)
                cursor.execute("""UPDATE products SET name=%s, retail_price=%s, wholesale_price=%s, stock_count=%s 
                               WHERE product_id=%s""", (name, lprice, xprice, new_stock, existing_id))
        else:
            # COMPLETELY NEW
            cursor.execute("INSERT INTO products VALUES (%s, %s, %s, %s, %s)", 
                           (target_code, name, lprice, xprice, amount_to_add))

        conn.commit()
        conn.close()
        update_memory()
    except Exception as e:
        messagebox.showerror("Error", f"Database Add Failed: {e}")

update_memory()