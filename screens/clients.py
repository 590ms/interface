import tkinter as tk
from tkinter import messagebox
from backend import (clients, update_clients_memory, add_client, delete_client,
                     nclients, update_nclients_memory, add_nclient, delete_nclient)


class ClientsMixin:

    def clients_screen(self):
        self.save_cart_state()
        update_clients_memory()
        update_nclients_memory()
        self.clear_frame()

        # Track which tab is active
        self._active_tab = getattr(self, '_active_tab', 'cardholders')

        # ── Title ──────────────────────────────────────────────────────
        tk.Label(self.main_frame, text="CLIENT DATABASE", font=("Segoe UI", 20, "bold"),
                 bg=self.bg_color, fg=self.text_color).place(relx=0, rely=0, relwidth=1, relheight=0.12)

        # ── Tab Buttons ────────────────────────────────────────────────
        tab_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        tab_frame.place(relx=0.1, rely=0.12, relwidth=0.8, relheight=0.06)

        self._tab_card_btn = tk.Button(tab_frame, text="🪪  CARD HOLDERS",
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=lambda: self._switch_tab('cardholders'))
        self._tab_card_btn.pack(side="left", fill="both", expand=True, padx=(0, 2))

        self._tab_walk_btn = tk.Button(tab_frame, text="🚶  WALK-IN CLIENTS",
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=lambda: self._switch_tab('walkins'))
        self._tab_walk_btn.pack(side="left", fill="both", expand=True, padx=(2, 0))

        # ── List Container ─────────────────────────────────────────────
        list_container = tk.Frame(self.main_frame, bg=self.card_color)
        list_container.place(relx=0.1, rely=0.19, relwidth=0.8, relheight=0.55)

        self.clients_display = tk.Listbox(list_container, font=("Consolas", 11),
                                          bg=self.card_color, fg=self.text_color,
                                          bd=0, highlightthickness=0,
                                          selectbackground=self.accent_color)
        scrollbar = tk.Scrollbar(list_container, orient="vertical",
                                 command=self.clients_display.yview)
        self.clients_display.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.clients_display.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # ── Action Buttons ─────────────────────────────────────────────
        tk.Button(self.main_frame, text="RETURN", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self.show_pos_screen).place(relx=0.1, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="DELETE", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self._delete_action).place(relx=0.45, rely=0.8, relwidth=0.1, relheight=0.05)

        tk.Button(self.main_frame, text="ADD NEW", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self._add_action).place(relx=0.6, rely=0.8, relwidth=0.1, relheight=0.05)

        # ── Load active tab ────────────────────────────────────────────
        self._switch_tab(self._active_tab)

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------

    def _switch_tab(self, tab):
        self._active_tab = tab
        if tab == 'cardholders':
            self._tab_card_btn.configure(bg=self.accent_color, fg=self.text_color)
            self._tab_walk_btn.configure(bg=self.card_color,   fg=self.text_color)
            self._populate_cardholders(self.clients_display)
        else:
            self._tab_card_btn.configure(bg=self.card_color,   fg=self.text_color)
            self._tab_walk_btn.configure(bg=self.accent_color, fg=self.text_color)
            self._populate_walkins(self.clients_display)

    # ------------------------------------------------------------------
    # Populate helpers
    # ------------------------------------------------------------------

    def _populate_cardholders(self, listbox):
        """Card holders: id, name, phone, tin, balance — 5 fields each."""
        listbox.delete(0, tk.END)
        for i in range(0, len(clients), 5):
            listbox.insert(
                tk.END,
                f"ID: {clients[i]:<6} | {clients[i+1].upper():<20} | "
                f"TIN: {clients[i+3]:<12} | BAL: {clients[i+4]}€"
            )

    def _populate_walkins(self, listbox):
        """Walk-in clients: id, name, email, phone, tin, job_title — 6 fields each."""
        listbox.delete(0, tk.END)
        for i in range(0, len(nclients), 6):
            listbox.insert(
                tk.END,
                f"ID: {nclients[i]:<6} | {nclients[i+1].upper():<20} | "
                f"TIN: {nclients[i+4]:<12} | JOB: {nclients[i+5]}"
            )

    def refresh_clients_list(self):
        update_clients_memory()
        update_nclients_memory()
        if hasattr(self, 'clients_display'):
            self._switch_tab(self._active_tab)

    # ------------------------------------------------------------------
    # Actions — route to correct table based on active tab
    # ------------------------------------------------------------------

    def _delete_action(self):
        selected = self.clients_display.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a client to delete.")
            return

        item_text  = self.clients_display.get(selected[0])
        client_id  = item_text.split("|")[0].replace("ID:", "").strip()
        table_name = "Card Holder" if self._active_tab == 'cardholders' else "Walk-in Client"

        if messagebox.askyesno("Confirm Delete", f"Delete {table_name} ID: {client_id}?"):
            if self._active_tab == 'cardholders':
                delete_client(client_id)
            else:
                delete_nclient(client_id)
            self.refresh_clients_list()

    def _add_action(self):
        if self._active_tab == 'cardholders':
            self._add_cardholder_screen()
        else:
            self._add_walkin_screen()

    # ------------------------------------------------------------------
    # Add Card Holder
    # ------------------------------------------------------------------

    def _add_cardholder_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Register Card Holder")
        win.geometry("600x680")
        win.configure(bg=self.bg_color)

        tk.Label(win, text="🪪  CARD HOLDER REGISTRATION", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        fields = [
            ("Client ID:",       "client_id"),
            ("Name:",            "name"),
            ("Phone:",           "phone"),
            ("Email:",           "email"),
            ("TIN:",             "tin"),
            ("Profession:",      "profession"),
            ("Initial Balance:", "balance"),
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            rely = 0.15 + i * 0.1
            tk.Label(win, text=label, font=("Segoe UI", 11, "bold"),
                     bg=self.bg_color, fg=self.text_color).place(relx=0.05, rely=rely)
            e = tk.Entry(win, font=("Segoe UI", 12), bg=self.card_color,
                         fg=self.text_color, bd=0, insertbackground="white")
            e.place(relx=0.35, rely=rely, relwidth=0.55, relheight=0.06)
            entries[key] = e

        def save():
            add_client(entries['client_id'].get(), entries['name'].get(),
                       entries['phone'].get(),     entries['email'].get(),
                       entries['tin'].get(),       entries['profession'].get(),
                       entries['balance'].get() or 0)
            self.refresh_clients_list()
            win.destroy()

        tk.Button(win, text="CONFIRM REGISTRATION", bg=self.accent_color,
                  fg=self.text_color, font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=save).place(relx=0.3, rely=0.92, relwidth=0.4, relheight=0.06)

    # ------------------------------------------------------------------
    # Add Walk-in Client
    # ------------------------------------------------------------------

    def _add_walkin_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Register Walk-in Client")
        win.geometry("600x620")
        win.configure(bg=self.bg_color)

        tk.Label(win, text="🚶  WALK-IN CLIENT REGISTRATION", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        fields = [
            ("Client ID:", "client_id"),
            ("Name:",      "name"),
            ("Email:",     "email"),
            ("Phone:",     "phone"),
            ("TIN:",       "tin"),
            ("Job Title:", "job_title"),
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            rely = 0.15 + i * 0.1
            tk.Label(win, text=label, font=("Segoe UI", 11, "bold"),
                     bg=self.bg_color, fg=self.text_color).place(relx=0.05, rely=rely)
            e = tk.Entry(win, font=("Segoe UI", 12), bg=self.card_color,
                         fg=self.text_color, bd=0, insertbackground="white")
            e.place(relx=0.35, rely=rely, relwidth=0.55, relheight=0.06)
            entries[key] = e

        def save():
            add_nclient(entries['client_id'].get(), entries['name'].get(),
                        entries['email'].get(),     entries['phone'].get(),
                        entries['tin'].get(),       entries['job_title'].get())
            self.refresh_clients_list()
            win.destroy()

        tk.Button(win, text="CONFIRM REGISTRATION", bg=self.accent_color,
                  fg=self.text_color, font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
                  command=save).place(relx=0.3, rely=0.92, relwidth=0.4, relheight=0.06)