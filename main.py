import tkinter as tk
from tkinter import messagebox
from backend import *


class POSSystem:

    def __init__(self, root):
        self.sum = 0.0
        self.root = root
        self.root.title("Python POS System")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Return>", lambda e: self.add_item())


        # Main Background
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(expand=True, fill="both")

        # --- RIGHT SIDE: Entry and Keypad ---
        self.cart_label = tk.Label(self.main_frame, text="Current Order", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.cart_label.place(relx=0.6, rely=0.1)

        self.total = tk.Label(self.main_frame, text="Total Amount:", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.total.place(relx=0.6, rely=0.63)

        self.totalnum = tk.Label(self.main_frame, text="", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.totalnum.place(relx=0.85, rely=0.63)

        self.product_list = tk.Listbox(self.main_frame, font=("Arial", 14), width=50, height=22)
        self.product_list.place(relx=0.6, rely=0.15)

        # --- LEFT SIDE: Scanned Products ---
        # Entry box for Barcode or Quantity
        self.entry_label = tk.Label(self.main_frame, text="Enter Product ID:", font=("Arial", 14), bg="#f0f0f0")
        self.entry_label.place(relx=0.05, rely=0.1)

        self.input_box = tk.Entry(self.main_frame, font=("Arial", 24), width=30)
        self.input_box.place(relx=0.05, rely=0.15)
        self.input_box.focus_set()

        # Create the Number Pad using a loop
        self.create_keypad()

        self.exit_btn = tk.Button(self.main_frame, text="EXIT SYSTEM", bg="#e74c3c", fg="white",
                                  font=("Arial", 12, "bold"), width=15, height=2, command=self.root.destroy)
        self.exit_btn.place(relx=0.90, rely=0.95)

    def create_keypad(self):
        # We use a frame specifically to hold the buttons in a grid
        keypad_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        keypad_frame.place(relx=0.047, rely=0.2)

        buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            'C', '0', 'Enter'
        ]

        row = 0
        col = 0
        for button in buttons:
            # We use a lambda to pass the specific button text to the function
            action = lambda x=button: self.keypad_click(x)

            tk.Button(keypad_frame, text=button, width=10, height=3, font=("Arial", 17, "bold"),
                      command=action).grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col > 2:
                col = 0
                row += 1

    def keypad_click(self, char):
        if char == 'C':
            self.input_box.delete(0, tk.END)
            self.input_box.focus_set()
        elif char == 'Enter':
            self.add_item()
            self.input_box.focus_set()
        else:
            self.input_box.insert(tk.END, char)
            self.input_box.focus_set()

    def add_item(self):
        length = len(products)
        item_id = self.input_box.get()
        if item_id in products:
            for i in range(length):
                if  item_id == products[i]:
                    # In a real app, you'd look up the ID in a database
                    self.product_list.insert(tk.END, f"{products[i+1].title():<90} {products[i+2]}€")
                    self.input_box.delete(0, tk.END)
                    self.sum += float(products[i+2])
                    self.totalnum.config(text=f"{self.sum:.2f}")
                    self.input_box.focus_set()







        else:
            messagebox.showwarning("Input Error", "Please enter a Product ID!")
            self.input_box.delete(0, tk.END)





if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()