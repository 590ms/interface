import tkinter as tk
from tkinter import messagebox, simpledialog
from backend import products, check_stock, process_checkout, update_member_rewards


class POSMixin:

    def show_pos_screen(self):
        self.clear_frame()
        self.root.bind("<Return>", lambda e: self.add_item())

        # --- Navigation ---
        tk.Button(self.main_frame, text="STOCK", bg=self.card_color, fg=self.accent_color,
                  font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                  command=self.stock).place(relx=0.02, rely=0.02, relwidth=0.06, relheight=0.04)

        tk.Button(self.main_frame, text="CLIENTS", bg=self.card_color, fg=self.accent_color,
                  font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                  command=self.clients).place(relx=0.1, rely=0.02, relwidth=0.06, relheight=0.04)

        # --- Order Panel (right side) ---
        order_container = tk.Frame(self.main_frame, bg=self.card_color, bd=0)
        order_container.place(relx=0.62, rely=0.08, relwidth=0.35, relheight=0.8)

        tk.Label(order_container, text="CURRENT ORDER", font=("Segoe UI", 12, "bold"),
                 bg=self.card_color, fg=self.text_color).pack(pady=10)

        self.product_list = tk.Listbox(order_container, font=("Consolas", 10),
                                       bg=self.bg_color, fg=self.text_color,
                                       bd=0, highlightthickness=0)
        self.product_list.pack(padx=15, pady=5, fill="both", expand=True)
        self.product_list.bind("<Double-Button-1>", self.change_quantity)

        total_frame = tk.Frame(order_container, bg=self.card_color)
        total_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(total_frame, text="TOTAL:", font=("Segoe UI", 14, "bold"),
                 bg=self.card_color, fg=self.text_color).pack(side="left")

        self.totalnum = tk.Label(total_frame, text=f"{self.sum:.2f}€",
                                  font=("Segoe UI", 18, "bold"),
                                  bg=self.card_color, fg=self.success_color)
        self.totalnum.pack(side="right")

        # --- Scan Input ---
        tk.Label(self.main_frame, text="READY TO SCAN", font=("Segoe UI", 10),
                 bg=self.bg_color, fg=self.accent_color).place(relx=0.1, rely=0.1)

        self.input_box = tk.Entry(self.main_frame, font=("Segoe UI", 22),
                                  bg=self.card_color, fg=self.text_color,
                                  bd=0, insertbackground="white", justify="center")
        self.input_box.place(relx=0.1, rely=0.14, relwidth=0.35, relheight=0.07)
        self.input_box.focus_set()

        # --- Keypad ---
        self.create_keypad()

        # --- Action Buttons ---
        tk.Button(self.main_frame, text="EXIT", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 9, "bold"), bd=0,
                  command=self.root.destroy).place(relx=0.92, rely=0.94, relwidth=0.06, relheight=0.04)

        tk.Button(self.main_frame, text="CASH", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 9, "bold"), bd=0,
                  command=self.handle_cash).place(relx=0.5, rely=0.325 , relwidth=0.08, relheight=0.05)

        tk.Button(self.main_frame, text="REMOVE PRODUCT", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 9, "bold"), bd=0,
                  command=self.line_removal).place(relx=0.5, rely=0.256, relwidth=0.08, relheight=0.05)


        tk.Button(self.main_frame, text="LOYALTY", bg="#f39c12", fg=self.text_color,
                  font=("Segoe UI", 9, "bold"), bd=0,
                  command=self.loyalty_menu).place(relx=0.1, rely=0.86, relwidth=0.35, relheight=0.05)
        
        tk.Button(self.main_frame, text="TRANSACRION HISTORY", bg=self.card_color, fg=self.accent_color,
          font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
          command=self.transaction_history).place(relx=0.18, rely=0.02, relwidth=0.06, relheight=0.04)

        # --- Restore cart ---
        for item in self.temp_cart:
            self.product_list.insert(tk.END, item)
        self.totalnum.config(text=f"{self.sum:.2f}€")

    # ------------------------------------------------------------------
    # Keypad
    # ------------------------------------------------------------------

    def create_keypad(self):
        keypad_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        keypad_frame.place(relx=0.1, rely=0.25, relwidth=0.35, relheight=0.6)

        for i in range(3):
            keypad_frame.columnconfigure(i, weight=1)
        for i in range(4):
            keypad_frame.rowconfigure(i, weight=1)

        buttons = [
            ('7', self.card_color), ('8', self.card_color), ('9', self.card_color),
            ('4', self.card_color), ('5', self.card_color), ('6', self.card_color),
            ('1', self.card_color), ('2', self.card_color), ('3', self.card_color),
            ('C', "#333333"),       ('0', self.card_color), ('ENTER', self.accent_color),
        ]

        row, col = 0, 0
        for text, color in buttons:
            tk.Button(keypad_frame, text=text, font=("Segoe UI", 14, "bold"),
                      bg=color, fg=self.text_color, bd=0, activebackground="#444",
                      command=lambda x=text: self.keypad_click(x)
                      ).grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
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

    # ------------------------------------------------------------------
    # Cart Management
    # ------------------------------------------------------------------

    def add_item(self):
        item_id = self.input_box.get()
        for i in range(0, len(products), 5):
            if item_id == products[i]:
                name  = products[i + 1].upper()
                price = float(products[i + 2])

                if int(products[i + 4]) <= 0:
                    messagebox.showerror("Stock Error", f"{name} is out of stock.")
                    self.input_box.delete(0, tk.END)
                    return

                self.product_list.insert(tk.END, f"{item_id:<5} {name:<15} 1 {price:>10.2f}€")
                self.temp_cart = list(self.product_list.get(0, tk.END))
                self.sum += price
                self.totalnum.config(text=f"{self.sum:.2f}€")
                self.input_box.delete(0, tk.END)
                self.product_list.yview(tk.END)
                return

        messagebox.showerror("Error", "Product Not Recognized or Out of Stock")
        self.input_box.delete(0, tk.END)

    def change_quantity(self, event):
        selection = self.product_list.curselection()
        if not selection:
            return

        index = selection[0]
        line  = self.product_list.get(index)
        parts = line.split()

        item_id       = parts[0]
        old_cart_qty  = int(parts[-2])
        price_per_unit = float(parts[-1].replace('€', '')) / old_cart_qty

        new_cart_qty = simpledialog.askinteger(
            "Edit Quantity",
            f"Current in cart: {old_cart_qty}\nEnter total quantity:",
            minvalue=0
        )

        if new_cart_qty is None:
            return

        # Verify against live DB stock (moved from inline connection to backend helper)
        server_stock = check_stock(item_id)
        if server_stock is not None and new_cart_qty > server_stock:
            messagebox.showerror("Stock Error",
                                 f"Cannot add {new_cart_qty} units.\n"
                                 f"Only {server_stock} available in total stock.")
            return

        diff = new_cart_qty - old_cart_qty
        self.sum += diff * price_per_unit
        self.totalnum.config(text=f"{self.sum:.2f}€")

        self.product_list.delete(index)
        if new_cart_qty > 0:
            name = parts[1]
            new_line_price = new_cart_qty * price_per_unit
            self.product_list.insert(index, f"{item_id:<5} {name:<15} {new_cart_qty} {new_line_price:>10.2f}€")

        self.temp_cart = list(self.product_list.get(0, tk.END))

    def line_removal(self):
        selection = self.product_list.curselection()
        if not selection:
            messagebox.showwarning("Line Removal", "Select an item to remove.")
            return

        index = selection[0]
        line = self.product_list.get(index)
        parts = line.split()

        # Parse price from the line and subtract from total
        price = float(parts[-1].replace('€', ''))
        self.sum -= price
        self.sum = max(self.sum, 0.0)  # guard against floating point drift

        self.product_list.delete(index)
        self.temp_cart = list(self.product_list.get(0, tk.END))
        self.totalnum.config(text=f"{self.sum:.2f}€")

    # ------------------------------------------------------------------
    # Checkout
    # ------------------------------------------------------------------

    def handle_cash(self):
        if not self.product_list.get(0, tk.END):
            return

        current_sale_sum  = self.sum
        member_to_update  = self.active_member
        final_member_data = None

        if member_to_update:
            used = member_to_update.get('used', 0)
            final_member_data = update_member_rewards(member_to_update['id'], current_sale_sum, used)
            if final_member_data:
                final_member_data['name'] = member_to_update['name']

        if process_checkout(self.product_list, current_sale_sum, final_member_data):
            self.product_list.delete(0, tk.END)
            self.temp_cart    = []
            self.sum          = 0.0
            self.active_member = None
            self.totalnum.config(text="0.00€")
