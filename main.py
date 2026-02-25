import tkinter as tk
from tkinter import messagebox, simpledialog
from backend import *

class POSSystem:
    def __init__(self, root):
        self.sum = 0.0
        self.root = root
        self.root.title("Nexus POS")
        self.root.attributes("-fullscreen", True)
        
        self.bg_color = "#121212"      
        self.card_color = "#1e1e1e"    
        self.accent_color = "#3498db"  
        self.text_color = "#ffffff"    
        self.danger_color = "#e74c3c"  
        self.success_color = "#2ecc71" 

        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill="both")
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.show_pos_screen()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_pos_screen(self):
        self.clear_frame()
        self.root.bind("<Return>", lambda e: self.add_item())

        self.navi1 = tk.Button(self.main_frame, text="STOCK", bg=self.card_color, fg=self.accent_color, 
                                font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", command=self.stock)
        self.navi1.place(relx=0.02, rely=0.02, relwidth=0.06, relheight=0.04)

        order_container = tk.Frame(self.main_frame, bg=self.card_color, bd=0)
        order_container.place(relx=0.62, rely=0.08, relwidth=0.35, relheight=0.8)

        tk.Label(order_container, text="CURRENT ORDER", font=("Segoe UI", 12, "bold"), 
                 bg=self.card_color, fg=self.text_color).pack(pady=10)

        # Updated Listbox with binding
        self.product_list = tk.Listbox(order_container, font=("Consolas", 10), bg=self.bg_color, 
                                        fg=self.text_color, bd=0, highlightthickness=0)
        self.product_list.pack(padx=15, pady=5, fill="both", expand=True)
        
        # BINDING: Double click to change quantity
        self.product_list.bind("<Double-Button-1>", self.change_quantity)

        total_frame = tk.Frame(order_container, bg=self.card_color)
        total_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(total_frame, text="TOTAL:", font=("Segoe UI", 14, "bold"), 
                 bg=self.card_color, fg=self.text_color).pack(side="left")
        
        self.totalnum = tk.Label(total_frame, text=f"{self.sum:.2f}€", font=("Segoe UI", 18, "bold"), 
                                  bg=self.card_color, fg=self.success_color)
        self.totalnum.pack(side="right")

        tk.Label(self.main_frame, text="READY TO SCAN", font=("Segoe UI", 10), 
                 bg=self.bg_color, fg=self.accent_color).place(relx=0.1, rely=0.1)

        self.input_box = tk.Entry(self.main_frame, font=("Segoe UI", 22), bg=self.card_color, 
                                  fg=self.text_color, bd=0, insertbackground="white", justify="center")
        self.input_box.place(relx=0.1, rely=0.14, relwidth=0.35, relheight=0.07)
        self.input_box.focus_set()

        self.create_keypad()

        self.exit_btn = tk.Button(self.main_frame, text="EXIT", bg=self.danger_color, fg=self.text_color,
                                  font=("Segoe UI", 9, "bold"), bd=0, command=self.root.destroy)
        self.exit_btn.place(relx=0.92, rely=0.94, relwidth=0.06, relheight=0.04)

    def create_keypad(self):
        keypad_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        keypad_frame.place(relx=0.1, rely=0.25, relwidth=0.35, relheight=0.6)

        for i in range(3): keypad_frame.columnconfigure(i, weight=1)
        for i in range(4): keypad_frame.rowconfigure(i, weight=1)

        buttons = [
            ('7', self.card_color), ('8', self.card_color), ('9', self.card_color),
            ('4', self.card_color), ('5', self.card_color), ('6', self.card_color),
            ('1', self.card_color), ('2', self.card_color), ('3', self.card_color),
            ('C', "#333333"), ('0', self.card_color), ('ENTER', self.accent_color)
        ]

        row, col = 0, 0
        for (text, color) in buttons:
            action = lambda x=text: self.keypad_click(x)
            tk.Button(keypad_frame, text=text, font=("Segoe UI", 14, "bold"), bg=color, 
                      fg=self.text_color, bd=0, activebackground="#444", 
                      command=action).grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def keypad_click(self, char):
        if char == 'C':
            self.input_box.delete(0, tk.END)
        elif char == 'ENTER':
            self.add_item()
        else:
            self.input_box.insert(tk.END, char)
        self.input_box.focus_set()

    def add_item(self):
        item_id = self.input_box.get()
        # Search existing stock in memory
        for i in range(0, len(products), 5):
            if item_id == products[i]:
                # Try to remove 1 from database
                if quantity_remove(item_id, 1):
                    name = products[i+1].upper()
                    price = float(products[i+2])
                    
                    self.product_list.insert(tk.END, f"{item_id:<5} {name:<15} 1 {price:>10.2f}€")
                    self.sum += price
                    self.totalnum.config(text=f"{self.sum:.2f}€")
                    self.input_box.delete(0, tk.END)
                    self.product_list.yview(tk.END)
                return # Exit once found and processed
        
        messagebox.showerror("Error", "Product Not Recognized or Out of Stock")
        self.input_box.delete(0, tk.END)

    def change_quantity(self, event):
        selection = self.product_list.curselection()
        if not selection: return
        
        index = selection[0]
        line = self.product_list.get(index)
        parts = line.split()
        
        item_id = parts[0]
        old_cart_qty = int(parts[-2])
        price_per_unit = float(parts[-1].replace('€', '')) / old_cart_qty
        
        # Ask for the absolute new quantity in the cart
        new_cart_qty = simpledialog.askinteger("Edit Quantity", f"Current in cart: {old_cart_qty}\nEnter total quantity:", minvalue=0)
        
        if new_cart_qty is not None:
            # Calculate the difference to send to database
            # If new is 5 and old was 2, we need to remove 3 more from DB.
            # If new is 1 and old was 5, we need to add 4 back to DB (diff will be -4).
            diff = new_cart_qty - old_cart_qty
            
            if quantity_remove(item_id, diff):
                # Update the running total
                self.sum += (diff * price_per_unit)
                self.totalnum.config(text=f"{self.sum:.2f}€")
                
                # Update Listbox
                self.product_list.delete(index)
                if new_cart_qty > 0:
                    name = parts[1]
                    new_line_price = new_cart_qty * price_per_unit
                    self.product_list.insert(index, f"{item_id:<5} {name:<15} {new_cart_qty} {new_line_price:>10.2f}€")

    def stock(self):
        update_memory()
        self.clear_frame()
        self.sum = 0.0
        tk.Label(self.main_frame, text="INVENTORY", font=("Segoe UI", 20, "bold"), 
                 bg=self.bg_color, fg=self.text_color).pack(pady=30)
        
        list_container = tk.Frame(self.main_frame, bg=self.card_color)
        list_container.place(relx=0.15, rely=0.15, relwidth=0.7, relheight=0.6)

        self.stock_display = tk.Listbox(list_container, font=("Consolas", 11), bg=self.card_color, 
                                        fg=self.text_color, bd=0, highlightthickness=0)
        self.stock_display.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        for i in range(0, len(products), 5):
            self.stock_display.insert(tk.END, f"{products[i]:<10} {products[i+1].upper():<20} {products[i+4]:<10} {products[i+2]}€")

        tk.Button(self.main_frame, text="RETURN", bg=self.accent_color, fg=self.text_color, 
                  font=("Segoe UI", 10, "bold"), bd=0, command=self.show_pos_screen).place(relx=0.3, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="DELETE", bg=self.danger_color, fg=self.text_color, 
                  font=("Segoe UI", 10, "bold"), bd=0, command=self.delete_item).place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="ADD", bg=self.accent_color, fg=self.text_color, 
                  font=("Segoe UI", 10, "bold"), bd=0, command=self.add_screen).place(relx=0.6, rely=0.8, relwidth=0.1, relheight=0.05)

    def delete_item(self):
        selected = self.stock_display.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a product to delete.")
            return
            
        item_text = self.stock_display.get(selected[0])
        item_id = item_text.split()[0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete ID: {item_id}?"):
            delete_product(item_id)
            self.refresh_stock_list(self.stock_display)

    def refresh_stock_list(self, listbox):
        update_memory()
        listbox.delete(0, tk.END)
        for i in range(0, len(products), 5):
            listbox.insert(tk.END, f"{products[i]:<10} {products[i+1].upper():<20} {products[i+4]:<10} {products[i+2]}€")

    def add_screen(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add")
        add_window.geometry("600x500")
        add_window.configure(bg=self.bg_color)
        
        tk.Label(add_window, text="New Inventory", font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=10)
        
        fields = [("ID:", 0.2), ("Name:", 0.3), ("Retail:", 0.4), ("Whole:", 0.5), ("Stock:", 0.6)]
        entries = []
        for label_text, rely in fields:
            tk.Label(add_window, text=label_text, font=("Segoe UI", 14, "bold"), bg=self.bg_color, fg=self.text_color).place(relx=0.02, rely=rely)
            e = tk.Entry(add_window, font=("Segoe UI", 14), bg=self.card_color, fg=self.text_color, bd=0, insertbackground="white")
            e.place(relx=0.2, rely=rely, relwidth=0.7, relheight=0.05)
            entries.append(e)

        ide, namee, lianikie, xontrikie, quae = entries

        tk.Button(add_window, text="ADD PRODUCT", bg=self.accent_color, fg=self.text_color, font=("Segoe UI", 10, "bold"), bd=0, 
                  command=lambda: [
                      add_product(ide.get(), namee.get(), lianikie.get(), xontrikie.get(), quae.get()), 
                      self.refresh_stock_list(self.stock_display),
                      add_window.destroy()
                  ]).place(relx=0.3, rely=0.8, relwidth=0.4, relheight=0.1)


if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()