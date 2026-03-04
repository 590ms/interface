import tkinter as tk
from tkinter import messagebox, simpledialog
from backend import *

class POSSystem:
    def __init__(self, root):
        self.sum = 0.0
        self.root = root
        self.temp_cart = []
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


        self.navi2 = tk.Button(self.main_frame, text="CLIENTS", bg=self.card_color, fg=self.accent_color,
                                font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", command=self.clients)
        self.navi2.place(relx=0.1, rely=0.02, relwidth=0.06, relheight=0.04)


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

        self.cash_btn = tk.Button(self.main_frame, text="CASH", bg=self.success_color, fg=self.text_color,
                                  font=("Segoe UI", 9, "bold"), bd=0, command=self.handle_cash)
        self.cash_btn.place(relx=0.5, rely=0.30, relwidth=0.08, relheight=0.05)

        if self.temp_cart:
            for item in self.temp_cart:
                self.product_list.insert(tk.END, item)


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
                name = products[i+1].upper()
                price = float(products[i+2])
                if int(products[i+4]) <= 0:
                    messagebox.showerror("Stock Error", f"{name} is out of stock.")
                    self.input_box.delete(0, tk.END)
                    return
                    
                self.product_list.insert(tk.END, f"{item_id:<5} {name:<15} 1 {price:>10.2f}€")
                self.sum += price
                self.totalnum.config(text=f"{self.sum:.2f}€")
                self.input_box.delete(0, tk.END)
                self.product_list.yview(tk.END)
                return 
        
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
        
        new_cart_qty = simpledialog.askinteger("Edit Quantity", f"Current in cart: {old_cart_qty}\nEnter total quantity:", minvalue=0)
        
        if new_cart_qty is not None:
            # CHECK SERVER STOCK BEFORE UPDATING CART
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT stock FROM products WHERE code = %s", (item_id,))
                res = cursor.fetchone()
                conn.close()

                if res:
                    server_stock = int(res[0])
                    if new_cart_qty > server_stock:
                        messagebox.showerror("Stock Error", 
                                             f"Cannot add {new_cart_qty} units.\n"
                                             f"Only {server_stock} available in total stock.")
                        return 
            except Exception as e:
                print(f"Stock check failed: {e}")
            

            diff = new_cart_qty - old_cart_qty
            self.sum += (diff * price_per_unit)
            self.totalnum.config(text=f"{self.sum:.2f}€")
            
            self.product_list.delete(index)
            if new_cart_qty > 0:
                name = parts[1]
                new_line_price = new_cart_qty * price_per_unit
                self.product_list.insert(index, f"{item_id:<5} {name:<15} {new_cart_qty} {new_line_price:>10.2f}€")

    def handle_cash(self):
        # Database quantity removal and PDF generation
        if process_checkout(self.product_list, self.sum):
            self.product_list.delete(0, tk.END)
            self.temp_cart = []
            self.sum = 0.0
            self.totalnum.config(text="0.00€")

    def stock(self):
        if hasattr(self, 'product_list'):
            self.temp_cart = list(self.product_list.get(0, tk.END))
            
        update_memory()
        self.clear_frame()
        
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

    def clients(self):
        if hasattr(self, 'product_list'):
            self.temp_cart = list(self.product_list.get(0, tk.END))
            
        update_clients_memory()
        self.clear_frame()

        tk.Label(self.main_frame, text="CLIENT DATABASE", font=("Segoe UI", 20, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=30)

        list_container = tk.Frame(self.main_frame, bg=self.card_color)
        list_container.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.6)

        self.clients_display = tk.Listbox(list_container, font=("Consolas", 11), bg=self.card_color,
                                          fg=self.text_color, bd=0, highlightthickness=0)
        self.clients_display.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        
        for i in range(0, len(clients), 5):
            self.clients_display.insert(tk.END,
                                        f"ID: {clients[i]:<6} | NAME: {clients[i + 1].upper():<20} | TIN: {clients[i + 3]:<12} | BAL: {clients[i + 4]}€")

        # Navigation Buttons
        tk.Button(self.main_frame, text="RETURN", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, command=self.show_pos_screen).place(relx=0.3, rely=0.8,
                                                                                           relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="DELETE CLIENT", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, command=self.delete_item).place(relx=0.45, rely=0.8,
                                                                                                relwidth=0.1,
                                                                                                relheight=0.05)

        tk.Button(self.main_frame, text="ADD NEW", bg=self.success_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, command=self.add_screen_clients).place(relx=0.6, rely=0.8,
                                                                                              relwidth=0.1,
                                                                                              relheight=0.05)

    def add_screen_clients(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Register New Client")
        add_window.geometry("600x650")
        add_window.configure(bg=self.bg_color)

        tk.Label(add_window, text="CLIENT REGISTRATION", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        # Define the 7 fields required by backend add_client function
        # Each tuple is (Label Name, Vertical Position)
        client_fields = [
            ("Client ID:", 0.15),
            ("Name:", 0.25),
            ("Phone:", 0.35),
            ("Email:", 0.45),
            ("TIN:", 0.55),
            ("Profession:", 0.65),
            ("Initial Balance:", 0.75)
        ]

        self.client_entries = []  # Using self to keep track of them easily

        # Loop through the list to create ALL fields
        for label_text, rely in client_fields:
            tk.Label(add_window, text=label_text, font=("Segoe UI", 11, "bold"),
                     bg=self.bg_color, fg=self.text_color).place(relx=0.05, rely=rely)

            e = tk.Entry(add_window, font=("Segoe UI", 12), bg=self.card_color,
                         fg=self.text_color, bd=0, insertbackground="white")
            e.place(relx=0.35, rely=rely, relwidth=0.55, relheight=0.05)
            self.client_entries.append(e)

        # Save Function that collects data from all fields
        def save_action():
            data = [entry.get() for entry in self.client_entries]
            # Unpacks the list into: id, name, phone, email, tin, profession, balance
            add_client(*data)
            self.refresh_clients_list()
            add_window.destroy()

        tk.Button(add_window, text="CONFIRM REGISTRATION", bg=self.success_color,
                  fg=self.text_color, font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=save_action).place(relx=0.3, rely=0.88, relwidth=0.4, relheight=0.07)
    def refresh_clients_list(self):
        update_clients_memory()
        if hasattr(self, 'clients_display'):
            self.clients_display.delete(0, tk.END)
            for i in range(0, len(clients), 5):
                self.clients_display.insert(tk.END,
                                            f"ID: {clients[i]:<6} | NAME: {clients[i + 1].upper():<20} | TIN: {clients[i + 3]:<12} | BAL: {clients[i + 4]}€")


if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()