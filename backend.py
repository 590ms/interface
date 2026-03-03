import pymysql as mysql
from tkinter import messagebox

# Database Configuration
db_config = {
    'host': 'shopdb.cx6wcaeg21tg.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': '123456789', 
    'database': 'nexus_db' 
}

products = []
clients= []


def get_connection():
    return mysql.connect(**db_config)

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

def is_valid_id(item_id):
    try:
        int(item_id)
        return True
    except (ValueError, TypeError):
        messagebox.showerror("Invalid Input", "The Item ID must be a whole number (integer).")
        return False

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
    if not is_valid_id(target_code):
        return
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        
        cursor.execute("SELECT stock FROM products WHERE code = %s", (target_code,))
        id_row = cursor.fetchone()
        
       
        cursor.execute("SELECT code, stock FROM products WHERE name = %s AND code != %s", (name, target_code))
        name_row = cursor.fetchone()

        if id_row:
            new_stock = int(id_row[0]) + int(amount_to_add)
            
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
                
                cursor.execute("""UPDATE products SET name=%s, lprice=%s, xprice=%s, stock=%s 
                               WHERE code=%s""", (name, lprice, xprice, new_stock, existing_id))
        else:
            
            cursor.execute("INSERT INTO products (code, name, lprice, xprice, stock) VALUES (%s, %s, %s, %s, %s)", 
                           (target_code, name, lprice, xprice, amount_to_add))

        conn.commit()
        conn.close()
        update_memory()
    except Exception as e:
        messagebox.showerror("Error", f"Database Add Failed: {e}")


def quantity_remove(item_id, quantity):
    """
    quantity: The amount to subtract from stock.
    - If positive (e.g. 1): Removes 1 from database.
    - If negative (e.g. -1): Adds 1 back to database (e.g. when reducing cart qty).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check current stock first
        cursor.execute("SELECT stock FROM products WHERE code = %s", (item_id,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Product not found in database.")
            return False
            
        current_db_stock = int(result[0])
        
        # FAILSAFE: Ensure the change doesn't make stock negative
        if current_db_stock - int(quantity) < 0:
            messagebox.showwarning("Out of Stock", f"Only {current_db_stock} units remaining.")
            conn.close()
            return False

        # Update the existing stock
        sql = "UPDATE products SET stock = stock - %s WHERE code = %s"
        cursor.execute(sql, (quantity, item_id))
        conn.commit()
        conn.close()
        
        update_memory() # Sync global products list
        return True
        
    except Exception as e:
        print(f"Backend Error: {e}")
        return False
def update_clients_memory():
    global clients
    clients.clear()
    try:
        conn=get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT client_id, name, phone,tin, balance FROM clients")
        rows=cursor.fetchall()
        for row in rows:
            clients.extend([str(row[0]), str(row[1]), str(row[2]), str(row[3]) ,str(row[4])])
        conn.close()
    except Exception as e:
        print(f"Database Error (Clients): {e}")


def add_client(client_id, name, phone, email,tin,profession, initial_balance=0):
    if not is_valid_id(client_id):
        return
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO clients (client_id, name, phone, email,tin,profession ,balance ) VALUES (%s, %s, %s, %s, %s,%s,%s)"
        cursor.execute(sql, (client_id, name, phone, email, tin,profession , initial_balance))

        conn.commit()
        conn.close()
        update_clients_memory()
        messagebox.showinfo("Success", "Client added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add client: {e}")


def delete_client(client_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
        conn.commit()
        conn.close()
        update_clients_memory()
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete client: {e}")



update_memory()
update_clients_memory()