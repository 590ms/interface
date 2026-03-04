import pymysql as mysql
from tkinter import messagebox
from fpdf import FPDF
from datetime import datetime
import tkinter as tk

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
        
        # Ensure the change doesn't make stock negative
        if current_db_stock - int(quantity) < 0:
            messagebox.showwarning("Out of Stock", f"Only {current_db_stock} units remaining.")
            conn.close()
            return False

        # Update the existing stock
        sql = "UPDATE products SET stock = stock - %s WHERE code = %s"
        cursor.execute(sql, (quantity, item_id))
        conn.commit()
        conn.close()
        
        update_memory() 
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


def generate_receipt_pdf(cart_items, total_sum):
    try:
        # 80mm width, 200mm length (standard receipt)
        pdf = FPDF(format=(80, 200))
        pdf.add_page()
        
        # --- HEADER ---
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 8, "NEXUS SOLUTIONS", ln=True, align="C")
        pdf.set_font("Helvetica", '', 8)
        pdf.cell(0, 4, "123 Tech Avenue, Silicon District", ln=True, align="C")
        pdf.cell(0, 4, "Thessaloniki, GR - Tel: +30 2310 000 000", ln=True, align="C")
        pdf.ln(4)
        
        pdf.set_font("Helvetica", 'I', 7)
        pdf.cell(0, 4, f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="L")
        pdf.line(10, pdf.get_y(), 70, pdf.get_y())
        pdf.ln(2)

        # --- TABLE HEADER ---
        pdf.set_font("Helvetica", 'B', 8)
        pdf.cell(35, 5, "PRODUCT NAME", 0)
        pdf.cell(10, 5, "QTY", 0, 0, 'C')
        pdf.cell(15, 5, "TOTAL", 0, 1, 'R')
        pdf.ln(1)

        pdf.set_font("Helvetica", '', 8)
        for line in cart_items:
            clean_line = line.replace('€', '')
            
            # Split from the left to get the ID
            parts_start = clean_line.split(maxsplit=1)
            item_id = parts_start[0]

            # Split the rest from the right to get Qty and Price
            remaining = parts_start[1].rsplit(maxsplit=2)
            p_name = remaining[0].upper() 
            p_qty = remaining[1]
            p_total = remaining[2]
            
            start_y = pdf.get_y()
            
            # Print full name - it will wrap to the next line if longer than 35mm
            pdf.multi_cell(35, 4, p_name, 0, 'L')
            
            end_y = pdf.get_y()
            
            # Align Qty and Price to the top Y of the current item
            pdf.set_xy(45, start_y)
            pdf.cell(10, 4, p_qty, 0, 0, 'C')
            pdf.cell(15, 4, f"{float(p_total):.2f}", 0, 0, 'R')
            
            # Ensure next item starts after the name block
            pdf.set_y(end_y)
            pdf.ln(1)

        # --- TOTALS ---
        pdf.ln(2)
        pdf.line(10, pdf.get_y(), 70, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(40, 8, "TOTAL TO PAY", 0)
        pdf.cell(20, 8, f"{total_sum:.2f} EUR", 0, 1, 'R')
        
        # --- QR DECORATION ---
        pdf.ln(5)
        pdf.set_fill_color(0, 0, 0)
        # Center the QR square
        pdf.rect(30, pdf.get_y(), 20, 20, 'F') 
        pdf.ln(22)
        
        pdf.set_font("Helvetica", 'B', 7)
        pdf.cell(0, 4, "SCAN FOR DIGITAL COPY", ln=True, align="C")
        pdf.set_font("Helvetica", 'I', 7)
        pdf.cell(0, 5, "Thank you for shopping at Nexus!", ln=True, align="C")

        filename = f"receipt_{datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(filename)
        messagebox.showinfo("Success", f"Receipt generated: {filename}")
        
    except Exception as e:
        messagebox.showerror("PDF Error", f"Error: {e}")

def process_checkout(listbox_widget, total_sum):
    items = listbox_widget.get(0, tk.END)
    if not items: return False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # --- PRE-CHECK STOCK ---
        for line in items:
            parts_start = line.split(maxsplit=1)
            item_id = parts_start[0]
            remaining = parts_start[1].rsplit(maxsplit=2)
            qty_needed = int(remaining[1])
            
            cursor.execute("SELECT stock, name FROM products WHERE code = %s", (item_id,))
            res = cursor.fetchone()
            
            if not res:
                messagebox.showerror("Error", f"Product ID {item_id} no longer exists.")
                conn.close()
                return False
            
            current_stock = int(res[0])
            product_name = res[1]
            
            if current_stock < qty_needed:
                messagebox.showerror("Out of Stock", 
                                     f"Insufficient stock for: {product_name}\n"
                                     f"Requested: {qty_needed}\n"
                                     f"Available: {current_stock}\n\n"
                                     "Please double-click the item in the cart to reduce quantity.")
                conn.close()
                return False

        # If we reach here, all items are in stock
        for line in items:
            parts_start = line.split(maxsplit=1)
            item_id = parts_start[0]
            remaining = parts_start[1].rsplit(maxsplit=2)
            quantity = remaining[1]
            quantity_remove(item_id, quantity)
            
        conn.commit()
        conn.close()
        generate_receipt_pdf(items, total_sum)
        update_memory()
        return True
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False



update_memory()
update_clients_memory()