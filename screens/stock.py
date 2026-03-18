import tkinter as tk
from tkinter import messagebox
from backend import products, update_memory, delete_product, add_product


class StockMixin:


    def stock(self):
        self.save_cart_state()
        update_memory()
        self.clear_frame()
        

        tk.Label(self.main_frame, text="INVENTORY", font=("Segoe UI", 20, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=30)

        list_container = tk.Frame(self.main_frame, bg=self.card_color)
        list_container.place(relx=0.15, rely=0.15, relwidth=0.7, relheight=0.6)

        self.stock_display = tk.Listbox(list_container, font=("Consolas", 11),
                                        bg=self.card_color, fg=self.text_color,
                                        bd=0, highlightthickness=0)
        self.stock_display.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self._populate_stock_list(self.stock_display)

        tk.Button(self.main_frame, text="RETURN", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=self.show_pos_screen).place(relx=0.3, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="DELETE", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=self.delete_item).place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="ADD", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=self.add_screen).place(relx=0.6, rely=0.8, relwidth=0.1, relheight=0.05)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _populate_stock_list(self, listbox):
        """Fill a listbox with current product data."""
        listbox.delete(0, tk.END)
        for i in range(0, len(products), 5):
            listbox.insert(
                tk.END,
                f"{products[i]:<10} {products[i+1].upper():<20} {products[i+4]:<10} {products[i+2]}€"
            )

    def refresh_stock_list(self, listbox=None):
        """Reload from memory and repopulate the listbox."""
        update_memory()
        target = listbox if listbox else getattr(self, 'stock_display', None)
        if target:
            self._populate_stock_list(target)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def delete_item(self):
        selected = self.stock_display.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a product to delete.")
            return

        item_text = self.stock_display.get(selected[0])
        item_id   = item_text.split()[0]

        if messagebox.askyesno("Confirm Delete", f"Delete ID: {item_id}?"):
            delete_product(item_id)
            self.refresh_stock_list(self.stock_display)

    def add_screen(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add / Update Product")
        add_window.geometry("600x500")
        add_window.configure(bg=self.bg_color)
        

        tk.Label(add_window, text="New Inventory", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=10)

        fields = [
            ("ID:",     0.2),
            ("Name:",   0.3),
            ("Retail:", 0.4),
            ("Whole:",  0.5),
            ("Stock:",  0.6),
        ]
        entries = []
        for label_text, rely in fields:
            tk.Label(add_window, text=label_text, font=("Segoe UI", 14, "bold"),
                     bg=self.bg_color, fg=self.text_color).place(relx=0.02, rely=rely)
            e = tk.Entry(add_window, font=("Segoe UI", 14), bg=self.card_color,
                         fg=self.text_color, bd=0, insertbackground="white")
            e.place(relx=0.2, rely=rely, relwidth=0.7, relheight=0.05)
            entries.append(e)

        ide, namee, retaile, wholee, stocke = entries

        def save():
            add_product(ide.get(), namee.get(), retaile.get(), wholee.get(), stocke.get())
            self.refresh_stock_list(self.stock_display)
            add_window.destroy()

        tk.Button(add_window, text="ADD PRODUCT", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=save).place(relx=0.3, rely=0.8, relwidth=0.4, relheight=0.1)
        stocke.bind("<Return>", lambda e: save())
