import tkinter as tk
from tkinter import messagebox, simpledialog
from backend import products, check_stock, process_checkout, update_member_rewards, find_card_client, find_walkin_client, deduct_balance
from click import command


class POSMixin:



    def show_pos_screen(self):
        self.clear_frame()
        self.root.bind("<Return>", lambda e: self.add_item())

        # --- Navigation ---
        if self.user_role == "admin":
            tk.Button(self.main_frame, text="STOCK", bg=self.card_color, fg=self.accent_color,
                      font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                      command=self.stock).place(relx=0.02, rely=0.02, relwidth=0.06, relheight=0.04)

            tk.Button(self.main_frame, text="TRANSACRION HISTORY", bg=self.card_color, fg=self.accent_color,
                      font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                      command=self.transaction_history).place(relx=0.18, rely=0.02, relwidth=0.06, relheight=0.04)

        admin_btn_text = "EXIT ADMIN" if self.user_role == "admin" else "ADMIN LOGIN"
        admin_btn_color = self.danger_color if self.user_role == "admin" else "#333333"
        self.admin_toggle = tk.Button(
            self.main_frame,
            text=admin_btn_text,
            command=self.toggle_admin_mode,
            bg=admin_btn_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10
        )
        self.admin_toggle.place(relx=0.01, rely=0.98, anchor="sw")
        tk.Button(self.main_frame, text="CLIENTS", bg=self.card_color, fg=self.accent_color,
                  font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
                  command=self.clients_screen).place(relx=0.1, rely=0.02, relwidth=0.06, relheight=0.04)
        mode_btn_text = "WHOLESALE" if self.user_mode == "retail" else "RETAIL"
        mode_btn_color = self.accent_color if self.user_mode == "retail" else "#f39c12"
        tk.Button(self.main_frame, text=mode_btn_text,
                  command=self.toggle_mode,
                  bg=mode_btn_color, fg="white",
                  font=("Arial", 10, "bold"), relief="flat", padx=10
                  ).place(relx=0.12, rely=0.98, anchor="sw")

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
                  command=self.change_window).place(relx=0.5, rely=0.325 , relwidth=0.08, relheight=0.05)

        tk.Button(self.main_frame, text="REMOVE PRODUCT", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 9, "bold"), bd=0,
                  command=self.line_removal).place(relx=0.5, rely=0.256, relwidth=0.08, relheight=0.05)
        if self.user_mode == "wholesale" :
            tk.Button(self.main_frame, text="Nexus Card", bg=self.accent_color, fg=self.text_color,
                      font=("Segoe UI", 9, "bold"), bd=0,
                      command=self.attach_clientcard).place(relx=0.5, rely=0.394, relwidth=0.08, relheight=0.05)
            tk.Button(self.main_frame, text="Invoice", bg=self.accent_color, fg=self.text_color,
                      font=("Segoe UI", 9, "bold"), bd=0,
                      command=self.attach_client).place(relx=0.5, rely=0.463, relwidth=0.08, relheight=0.05)


        tk.Button(self.main_frame, text="LOYALTY", bg="#f39c12", fg=self.text_color,
                  font=("Segoe UI", 9, "bold"), bd=0,
                  command=self.loyalty_menu).place(relx=0.1, rely=0.86, relwidth=0.35, relheight=0.05)
        


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
                price = float(products[i + 2]) if self.user_mode == "retail" else float(products[i + 3])

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
                self.button_var = tk.StringVar(value=str(self.sum))
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

        if process_checkout(self.product_list, current_sale_sum, final_member_data,
                            mode=self.user_mode,
                            client_data=self.active_client or self.active_walkin):
            self.product_list.delete(0, tk.END)
            self.temp_cart    = []
            self.sum          = 0.0
            self.active_member = None
            self.active_walkin = None
            self.totalnum.config(text="0.00€")

    def nexuscard_checkout(self, client_data):
        if client_data['balance'] < self.sum:
            messagebox.showerror("Insufficient Funds",
                                 f"Card Balance: {client_data['balance']:.2f}€\nTotal: {self.sum:.2f}€")
            return

        cart_items = list(self.product_list.get(0, "end"))
        if not cart_items:
            messagebox.showerror("Cart Empty", "Please add something to the cart first.")
            return

        deduct_balance(client_data['id'], self.sum)

        final_member_data = None
        if self.active_member:
            used = self.active_member.get('used', 0)
            final_member_data = update_member_rewards(self.active_member['id'], self.sum, used)
            if final_member_data:
                final_member_data['name'] = self.active_member['name']

        client_data['balance_after'] = client_data['balance'] - self.sum

        if process_checkout(self.product_list, self.sum, final_member_data,
                            mode="wholesale",  # Usually cards trigger invoices
                            client_data=client_data):
            self.product_list.delete(0, "end")
            self.temp_cart = []
            self.sum = 0.0
            self.active_member = None
            self.active_client = None  # Clear attached client
            self.totalnum.config(text="0.00€")
            messagebox.showinfo("Success", "Nexus Card Payment Processed!")

    def attach_client(self):
        addc_window = tk.Toplevel(self.root)
        addc_window.title("Attach Client")
        addc_window.geometry("600x300")
        addc_window.configure(bg=self.bg_color)

        tk.Label(addc_window, text="ATTACH WALK-IN CLIENT", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        tk.Label(addc_window, text="Enter TIN:", font=("Segoe UI", 10, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack()

        ide = tk.Entry(addc_window, font=("Segoe UI", 14), bg=self.card_color,
                       fg=self.text_color, bd=0, insertbackground="white", justify="center")
        ide.pack(padx=60, pady=10, fill="x")
        ide.focus_set()

        def findc():
            client = ide.get().strip()
            search = find_walkin_client(client)
            if search:
                self.active_walkin = {
                    'id': search[0],
                    'name': search[1],
                    'email': search[2],
                    'phone': search[3],
                    'tin': search[4],
                    'job_title': search[5],
                    'is_card_client': False
                }
                messagebox.showinfo("Client Attached", f"Client: {search[1]}\nTIN: {search[4]}")
                addc_window.destroy()
            else:
                messagebox.showerror("Not Found", "No client found with that TIN.")

        tk.Button(addc_window, text="ATTACH CLIENT", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=findc).pack(pady=10, padx=60, fill="x", ipady=8)
        addc_window.bind("<Return>", lambda e: findc())

    def attach_clientcard(self):
        addc_window = tk.Toplevel(self.root)
        addc_window.title("Nexus Card Payment")
        addc_window.geometry("500x350")
        addc_window.configure(bg=self.bg_color)

        tk.Label(addc_window, text="SCAN NEXUS CARD", font=("Segoe UI", 16, "bold"),
                     bg=self.bg_color, fg=self.accent_color).pack(pady=20)

        ide = tk.Entry(addc_window, font=("Segoe UI", 16), bg=self.card_color,
                           fg=self.text_color, bd=0, insertbackground="white", justify="center")
        ide.pack(padx=60, pady=10, fill="x")
        ide.focus_set()

        def findcard():
            card_id = ide.get().strip()
            search = find_card_client(card_id)

            if search:
                client_dict = {
                    'id': search[0],
                    'name': search[1],
                    'phone': search[2],
                    'tin': search[3],
                    'balance': float(search[4]),
                    'is_card_client': True
                }
                addc_window.destroy()
                self.nexuscard_checkout(client_dict)
            else:
                messagebox.showerror("Not Found", "Invalid Card ID or Card Inactive.")

        tk.Button(addc_window, text="PAY WITH CARD", bg=self.success_color, fg=self.text_color,
                    font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2",
                    command=findcard).pack(pady=20, padx=60, fill="x", ipady=10)

        addc_window.bind("<Return>", lambda e: findcard())



    def change_window(self):

        if not self.product_list.get(0, tk.END):
            messagebox.showwarning("Transaction", "Cart is empty please add something...")
            return
        if self.user_mode == "wholesale":
            if self.active_client is None and self.active_walkin is None:
                messagebox.showwarning("Transaction", "No client attached please attach client...")
                return

        add_change_window = tk.Toplevel(self.root)
        add_change_window .title("Change Window")
        add_change_window .geometry("600x650")
        add_change_window .update_idletasks()
        x = (add_change_window .winfo_screenwidth() // 2) - (700 // 2)
        y = (add_change_window .winfo_screenheight() // 2) - (500 // 2)
        add_change_window .geometry(f"700x500+{x}+{y}")
        add_change_window.configure(bg=self.bg_color)

        tk.Button(add_change_window , textvariable=self.button_var, bg=self.card_color,
                  fg=self.text_color, font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=lambda:[self.handle_cash(),add_change_window.destroy()],).place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.07)
        #input box
        display_var = tk.StringVar(value="0")
        self.input = tk.Entry(add_change_window , font=("Segoe UI", 22),
                                  bg=self.card_color, fg=self.text_color,
                                  bd=0, insertbackground="white", justify="center")
        self.input.place(relx=0.1, rely=0.14, relwidth=0.8, relheight=0.07)
        self.input.focus_set()

        def changes():
            amount = self.input.get()
            change=float(amount)-self.sum


            popup = tk.Toplevel(add_change_window)
            popup.title("Change")
            popup.resizable(False, False)
            popup.configure(bg=self.bg_color)

            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (300 // 2)
            y = (popup.winfo_screenheight() // 2) - (200 // 2)
            popup.geometry(f"300x200+{x}+{y}")

            tk.Label(popup, text="Change Amount:",
                     font=("Segoe UI", 11), bg=self.bg_color,
                     fg=self.text_color).place(relx=0.1, rely=0.15)

            tk.Label(popup, text=f"{float(change):.2f}€",
                     font=("Segoe UI", 24, "bold"), bg=self.bg_color,
                     fg=self.accent_color).place(relx=0.1, rely=0.35)

            tk.Button(popup, text="OK",
                      bg=self.accent_color, fg=self.text_color,
                      font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                      command=lambda: [self.handle_cash(),popup.destroy(),add_change_window.destroy()]
                      ).place(relx=0.25, rely=0.7,relwidth=0.5, relheight=0.15)




         #press keybad
        def press(val):
            current = display_var.get()
            if val == "C":
                self.input.delete(0, tk.END)
            elif val == "⌫":
                self.input.delete(self.input.index("end") - 1)
            elif val == ".":
                if "." not in current:
                    display_var.set(current + ".")
            else:
                self.input.insert(tk.END, val)
                # display_var.set(val if current == "0" else current + val)

        keypad_frame = tk.Frame(add_change_window, bg=self.bg_color)
        keypad_frame.place(relx=0.05, rely=0.25, relwidth=0.9, relheight=0.6)

        buttons = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            ["C", "0", "⌫"],
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, label in enumerate(row):
                if label == "C":
                    bg = "#e74c3c"
                elif label == "⌫":
                    bg = "#e67e22"
                else:
                    bg = self.card_color

                tk.Button(keypad_frame, text=label,
                          font=("Segoe UI", 16, "bold"),
                          bg=bg, fg=self.text_color,
                          bd=0, cursor="hand2", relief="groove",
                          command=lambda v=label: press(v)
                          ).grid(row=row_idx, column=col_idx,
                                 padx=5, pady=5, sticky="nsew")

        # Make grid cells expand evenly
        for i in range(3):
            keypad_frame.columnconfigure(i, weight=1)
        for i in range(4):
            keypad_frame.rowconfigure(i, weight=1)



        # --- ENTER button ---
        add_change_window.bind("<Return>", lambda event: changes())
        tk.Button(add_change_window, text="ENTER",
                  bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=changes).place(relx=0.05, rely=0.88,
                                                  relwidth=0.45, relheight=0.08)
        tk.Button(add_change_window, text="CLOSE",
                  bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=add_change_window.destroy).place(relx=0.55, rely=0.88,
                                                    relwidth=0.4, relheight=0.08)
















