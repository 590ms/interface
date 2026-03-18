import pymysql as mysql
from tkinter import messagebox
from fpdf import FPDF
from datetime import datetime
import tkinter as tk
import random
import string

# Database Configuration
db_config = {
    'host': 'shopdb.cx6wcaeg21tg.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': '123456789',
    'database': 'nexus_db'
}

products = []
clients = []


def get_connection():
    return mysql.connect(**db_config)


def check_stock(item_id):
    """Returns current stock for a product, or None if not found."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM products WHERE code = %s", (item_id,))
        result = cursor.fetchone()
        conn.close()
        return int(result[0]) if result else None
    except Exception as e:
        print(f"Stock check error: {e}")
        return None


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
        messagebox.showerror("Invalid Input", "The ID must be a whole number (integer).")
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

        cursor.execute("SELECT stock FROM products WHERE code = %s", (item_id,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Product not found in database.")
            return False

        current_db_stock = int(result[0])

        if current_db_stock - int(quantity) < 0:
            messagebox.showwarning("Out of Stock", f"Only {current_db_stock} units remaining.")
            conn.close()
            return False

        cursor.execute("UPDATE products SET stock = stock - %s WHERE code = %s", (quantity, item_id))
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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT client_id, name, phone, tin, balance FROM clients")
        rows = cursor.fetchall()
        for row in rows:
            clients.extend([str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4])])
        conn.close()
    except Exception as e:
        print(f"Database Error (Clients): {e}")


def add_client(client_id, name, phone, email, tin, profession, initial_balance=0):
    if not is_valid_id(client_id):
        return
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO clients (client_id, name, phone, email, tin, profession, balance) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (client_id, name, phone, email, tin, profession, initial_balance))
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


def generate_receipt_pdf(cart_items, total_sum, member_data=None):
    try:
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
            parts = clean_line.split()

            if "LOYALTY" in clean_line:
                pdf.set_font("Helvetica", 'I', 8)
                discount_val = abs(float(parts[-1]))
                pdf.cell(45, 4, f"LOYALTY DISCOUNT x{parts[-2]}", 0)
                pdf.cell(15, 4, f"-{discount_val:.2f}", 0, 1, 'R')
                pdf.set_font("Helvetica", '', 8)
                continue

            item_id = parts[0]
            p_qty = parts[-2]
            p_total = parts[-1]
            p_name = " ".join(parts[1:-2]).upper()

            start_y = pdf.get_y()
            pdf.multi_cell(35, 4, p_name, 0, 'L')
            end_y = pdf.get_y()

            pdf.set_xy(45, start_y)
            pdf.cell(10, 4, p_qty, 0, 0, 'C')
            pdf.cell(15, 4, f"{float(p_total):.2f}", 0, 0, 'R')
            pdf.set_y(end_y)
            pdf.ln(1)

        # --- TOTALS ---
        pdf.ln(2)
        pdf.line(10, pdf.get_y(), 70, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(40, 8, "TOTAL TO PAY", 0)
        pdf.cell(20, 8, f"{total_sum:.2f} EUR", 0, 1, 'R')

        # --- LOYALTY SECTION ---
        if member_data:
            pdf.ln(2)
            pdf.set_font("Helvetica", 'B', 8)
            pdf.cell(0, 4, "LOYALTY MEMBER INFO", ln=True)
            pdf.set_font("Helvetica", '', 7)
            pdf.cell(0, 4, f"Member ID: {member_data['id']}", ln=True)
            pdf.cell(0, 4, f"Customer: {member_data['name']}", ln=True)

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT points, coupons FROM loyalty_members WHERE card_id = %s", (member_data['id'],))
                db_res = cursor.fetchone()
                conn.close()

                if db_res:
                    current_pts, current_cpns = db_res
                    pdf.cell(0, 4, f"Available Coupons: {current_cpns}", ln=True)
                    pdf.cell(0, 4, f"Current Points: {current_pts} (250 for next coupon)", ln=True)
            except Exception as e:
                print(f"Loyalty receipt error: {e}")

        # --- FOOTER ---
        pdf.ln(5)
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
        messagebox.showerror("PDF Error", f"Error generating receipt: {e}")


def process_checkout(listbox_widget, total_sum, member_data=None):
    items = listbox_widget.get(0, tk.END)
    if not items:
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for line in items:
            if "LOYALTY" in line:
                continue
            parts = line.split()
            item_id = parts[0]
            quantity = int(parts[-2])

            cursor.execute("SELECT stock FROM products WHERE code = %s", (item_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", f"Product ID {item_id} not found.")
                conn.close()
                return False
            if int(result[0]) < quantity:
                messagebox.showerror("Stock Error", f"Not enough stock for product {item_id}.")
                conn.close()
                return False

        conn.close()

        for line in items:
            if "LOYALTY" in line:
                continue
            parts = line.split()
            item_id = parts[0]
            quantity = parts[-2]
            quantity_remove(item_id, quantity)

        generate_receipt_pdf(items, total_sum, member_data)
        update_memory()
        return True

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False


def add_loyalty_member(name, phone):
    if not name or not phone:
        messagebox.showwarning("Input Error", "All fields are required.")
        return None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        while True:
            new_code = str(random.randint(10000000, 99999999))
            cursor.execute("SELECT card_id FROM loyalty_members WHERE card_id = %s", (new_code,))
            if not cursor.fetchone():
                break

        cursor.execute("INSERT INTO loyalty_members (card_id, name, phone) VALUES (%s, %s, %s)",
                       (new_code, name, phone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Member: {name}\nCard ID: {new_code}")
        return new_code
    except Exception as e:
        messagebox.showerror("Error", f"Registration Failed: {e}")
        return None

def delete_loyalty_member(card_id):
    if not card_id:
        messagebox.showwarning("Input Error", "Card ID is required.")
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT card_id FROM loyalty_members WHERE card_id = %s", (card_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", f"No member found with Card ID: {card_id}")
            conn.close()
            return False
        cursor.execute("DELETE FROM loyalty_members WHERE card_id = %s", (card_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Member with Card ID {card_id} has been deleted.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Deletion Failed: {e}")
        return False


def find_loyalty_member(identifier):
    """Identifier can be card_id or phone."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT card_id, name, points, coupons FROM loyalty_members WHERE card_id = %s OR phone = %s"
        cursor.execute(sql, (identifier, identifier))
        res = cursor.fetchone()
        conn.close()
        return res  # Returns (id, name, points, coupons) or None
    except Exception as e:
        print(f"Lookup error: {e}")
        return None


def update_member_rewards(card_id, total_spent, coupons_used):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT points, coupons FROM loyalty_members WHERE card_id = %s", (card_id,))
        res = cursor.fetchone()
        if not res:
            return None

        current_pts, current_cpns = int(res[0]), int(res[1])
        earned_pts = int(float(total_spent) * 2)

        new_pts_total = current_pts + earned_pts
        earned_coupons = new_pts_total // 250
        remaining_pts = new_pts_total % 250

        final_cpns = (current_cpns + earned_coupons) - int(coupons_used)
        if final_cpns < 0:
            final_cpns = 0

        cursor.execute("UPDATE loyalty_members SET points=%s, coupons=%s WHERE card_id=%s",
                       (remaining_pts, final_cpns, card_id))
        conn.commit()
        conn.close()

        return {"id": card_id, "points": remaining_pts, "coupons": final_cpns, "earned": earned_pts}
    except Exception as e:
        print(f"Update error: {e}")
        return None


# Load initial data into memory on import
update_memory()
update_clients_memory()
