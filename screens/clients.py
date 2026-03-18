import tkinter as tk
from tkinter import messagebox
from backend import clients, update_clients_memory, add_client, delete_client


class ClientsMixin:


    def clients(self):
        self.save_cart_state()
        update_clients_memory()
        self.clear_frame()

        tk.Label(self.main_frame, text="CLIENT DATABASE", font=("Segoe UI", 20, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=30)

        list_container = tk.Frame(self.main_frame, bg=self.card_color)
        list_container.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.6)

        self.clients_display = tk.Listbox(list_container, font=("Consolas", 11),
                                          bg=self.card_color, fg=self.text_color,
                                          bd=0, highlightthickness=0)
        self.clients_display.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self._populate_clients_list(self.clients_display)

        tk.Button(self.main_frame, text="RETURN", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=self.show_pos_screen).place(relx=0.3, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="DELETE CLIENT", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=self.delete_client_action).place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="ADD NEW", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0,
                  command=self.add_screen_clients).place(relx=0.6, rely=0.8, relwidth=0.1, relheight=0.05)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _populate_clients_list(self, listbox):
        """Fill a listbox with current client data."""
        listbox.delete(0, tk.END)
        for i in range(0, len(clients), 5):
            listbox.insert(
                tk.END,
                f"ID: {clients[i]:<6} | NAME: {clients[i+1].upper():<20} | "
                f"TIN: {clients[i+3]:<12} | BAL: {clients[i+4]}€"
            )

    def refresh_clients_list(self):
        """Reload from memory and repopulate the listbox."""
        update_clients_memory()
        if hasattr(self, 'clients_display'):
            self._populate_clients_list(self.clients_display)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def delete_client_action(self):
        selected = self.clients_display.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a client to delete.")
            return

        item_text = self.clients_display.get(selected[0])
        client_id = item_text.split("|")[0].replace("ID:", "").strip()

        if messagebox.askyesno("Confirm Delete", f"Delete Client ID: {client_id}?"):
            delete_client(client_id)
            self.refresh_clients_list()

    def add_screen_clients(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Register New Client")
        add_window.geometry("600x650")
        add_window.configure(bg=self.bg_color)

        tk.Label(add_window, text="CLIENT REGISTRATION", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        client_fields = [
            ("Client ID:",       0.15),
            ("Name:",            0.25),
            ("Phone:",           0.35),
            ("Email:",           0.45),
            ("TIN:",             0.55),
            ("Profession:",      0.65),
            ("Initial Balance:", 0.75),
        ]

        self.client_entries = []
        for label_text, rely in client_fields:
            tk.Label(add_window, text=label_text, font=("Segoe UI", 11, "bold"),
                     bg=self.bg_color, fg=self.text_color).place(relx=0.05, rely=rely)
            e = tk.Entry(add_window, font=("Segoe UI", 12), bg=self.card_color,
                         fg=self.text_color, bd=0, insertbackground="white")
            e.place(relx=0.35, rely=rely, relwidth=0.55, relheight=0.05)
            self.client_entries.append(e)

        def save_action():
            data = [entry.get() for entry in self.client_entries]
            add_client(*data)
            self.refresh_clients_list()
            add_window.destroy()

        tk.Button(add_window, text="CONFIRM REGISTRATION", bg=self.accent_color,
                  fg=self.text_color, font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=save_action).place(relx=0.3, rely=0.88, relwidth=0.4, relheight=0.07)
