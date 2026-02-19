import mysql.connector
from tkinter import messagebox

# Database Configuration
db_config = {
    'host': 'shopdb.cx6wcaeg21tg.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': '123456789', 
    'database': 'nexus_db' 
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
        cursor.execute("SELECT code, name, lprice, xprice, stock FROM products")
        rows = cursor.fetchall()
        for row in rows:
            products.extend([str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4])])
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

def delete_product(target_code):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE code = %s", (target_code,))
        conn.commit()
        conn.close()
        update_memory()
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete: {e}")

def add_product(target_code, name, lprice, xprice, amount_to_add):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # FIXED: Column names changed to code and stock
        cursor.execute("SELECT stock FROM products WHERE code = %s", (target_code,))
        id_row = cursor.fetchone()
        
        # FIXED: Column names changed to code and stock
        cursor.execute("SELECT code, stock FROM products WHERE name = %s AND code != %s", (name, target_code))
        name_row = cursor.fetchone()

        if id_row:
            new_stock = int(id_row[0]) + int(amount_to_add)
            # FIXED: Column names changed to lprice, xprice, stock, code
            cursor.execute("""UPDATE products SET name=%s, lprice=%s, xprice=%s, stock=%s 
                           WHERE code=%s""", (name, lprice, xprice, new_stock, target_code))
        
        elif name_row:
            existing_id = name_row[0]
            choice = messagebox.askyesno("Name Conflict", 
                f"The name '{name}' already exists under ID: {existing_id}.\n\n"
                f"Do you want to create a NEW entry with ID {target_code}?\n"
                f"(Selecting 'No' will update the existing ID {existing_id} instead)")
            
            if choice:
                cursor.execute("INSERT INTO products (code, name, lprice, xprice, stock) VALUES (%s, %s, %s, %s, %s)", 
                               (target_code, name, lprice, xprice, amount_to_add))
            else:
                new_stock = int(name_row[1]) + int(amount_to_add)
                # FIXED: Column names changed
                cursor.execute("""UPDATE products SET name=%s, lprice=%s, xprice=%s, stock=%s 
                               WHERE code=%s""", (name, lprice, xprice, new_stock, existing_id))
        else:
            # FIXED: Explicit column naming for the INSERT
            cursor.execute("INSERT INTO products (code, name, lprice, xprice, stock) VALUES (%s, %s, %s, %s, %s)", 
                           (target_code, name, lprice, xprice, amount_to_add))

        conn.commit()
        conn.close()
        update_memory()
    except Exception as e:
        messagebox.showerror("Error", f"Database Add Failed: {e}")

update_memory()