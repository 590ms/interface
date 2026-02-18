import tkinter as tk
from tkinter import messagebox
from backend import *

class POSSystem:
    def __init__(self, root):
        self.sum = 0.0
        self.root = root
        self.root.title("Nexus POS")
        self.root.attributes("-fullscreen", True)
        
        # Modern Color Palette
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

        # --- NAVIGATION (Smaller & Sleeker) ---
        self.navi1 = tk.Button(self.main_frame, text="STOCK", bg=self.card_color, fg=self.accent_color, 
                               font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", command=self.stock)
        self.navi1.place(relx=0.02, rely=0.02, relwidth=0.06, relheight=0.04)

        # --- RIGHT SIDE: ORDER PANEL (Narrower for more space) ---
        order_container = tk.Frame(self.main_frame, bg=self.card_color, bd=0)
        order_container.place(relx=0.62, rely=0.08, relwidth=0.35, relheight=0.8)

        tk.Label(order_container, text="CURRENT ORDER", font=("Segoe UI", 12, "bold"), 
                 bg=self.card_color, fg=self.text_color).pack(pady=10)

        self.product_list = tk.Listbox(order_container, font=("Consolas", 10), bg=self.bg_color, 
                                       fg=self.text_color, bd=0, highlightthickness=0)
        self.product_list.pack(padx=15, pady=5, fill="both", expand=True)

        total_frame = tk.Frame(order_container, bg=self.card_color)
        total_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(total_frame, text="TOTAL:", font=("Segoe UI", 14, "bold"), 
                 bg=self.card_color, fg=self.text_color).pack(side="left")
        
        self.totalnum = tk.Label(total_frame, text=f"{self.sum:.2f}€", font=("Segoe UI", 18, "bold"), 
                                 bg=self.card_color, fg=self.success_color)
        self.totalnum.pack(side="right")

        # --- LEFT SIDE: INPUT & KEYPAD (Centered and compact) ---
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
        # Keypad is now smaller (relwidth 0.35 instead of 0.42)
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
        if item_id in products:
            for i in range(0, len(products), 5):
                if item_id == products[i]:
                    name = products[i+1].upper()
                    price = f"{products[i+2]}€"
                    self.product_list.insert(tk.END, f"{name:<25} {price:>10}")
                    self.sum += float(products[i+2])
                    self.totalnum.config(text=f"{self.sum:.2f}€")
                    self.input_box.delete(0, tk.END)
                    self.product_list.yview(tk.END)
                    break
        else:
            messagebox.showerror("Error", "Product Not Recognized")
            self.input_box.delete(0, tk.END)
        self.input_box.focus_set()

    def stock(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="INVENTORY", font=("Segoe UI", 20, "bold"), 
                 bg=self.bg_color, fg=self.text_color).pack(pady=30)
        
        list_container = tk.Frame(self.main_frame, bg=self.card_color)
        list_container.place(relx=0.15, rely=0.15, relwidth=0.7, relheight=0.6)

        stock_display = tk.Listbox(list_container, font=("Consolas", 11), bg=self.card_color, 
                                   fg=self.text_color, bd=0, highlightthickness=0)
        stock_display.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        for i in range(0, len(products), 5):
            stock_display.insert(tk.END, f"{products[i]:<10} {products[i+1].upper():<30} {products[i+2]}€")

        back_btn = tk.Button(self.main_frame, text="RETURN", bg=self.accent_color, 
                             fg=self.text_color, font=("Segoe UI", 10, "bold"), bd=0, 
                             command=self.show_pos_screen)
        back_btn.place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.05)

if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()