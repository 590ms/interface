import tkinter as tk
from backend import update_memory, update_clients_memory


class POSApp:


    def __init__(self, root):
        self.root = root
        self.sum = 0.0
        self.temp_cart = []
        self.active_member = None

        self.root.title("Nexus POS")
        self.root.attributes("-fullscreen", True)

        # --- Theme Colors ---
        self.bg_color      = "#121212"
        self.card_color    = "#1e1e1e"
        self.accent_color  = "#3498db"
        self.text_color    = "#ffffff"
        self.danger_color  = "#e74c3c"
        self.success_color = "#2ecc71"

        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill="both")

        # Load data and show the main POS screen
        update_memory()
        update_clients_memory()
        self.show_pos_screen()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def save_cart_state(self):
        try:
            if hasattr(self, 'product_list') and self.product_list.winfo_exists():
                self.temp_cart = list(self.product_list.get(0, tk.END))
        except Exception:
            pass
