import tkinter as tk
from pos_system import POSSystem

if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()