import tkinter as tk
from tkinter import messagebox
import random
import string
from backend import find_loyalty_member, add_loyalty_member,delete_loyalty_member as db_delete_loyalty_member


class LoyaltyMixin:


    def loyalty_menu(self):
        self.save_cart_state()
        self.clear_frame()
        


        tk.Label(self.main_frame, text="LOYALTY MANAGEMENT", font=("Segoe UI", 20, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=30)

        container = tk.Frame(self.main_frame, bg=self.card_color, bd=0)
        container.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.6)

        tk.Label(container, text="SCAN CARD OR ENTER PHONE", font=("Segoe UI", 10, "bold"),
                 bg=self.card_color, fg=self.accent_color).pack(pady=(20, 5))

        id_entry = tk.Entry(container, font=("Segoe UI", 16), bg=self.bg_color, fg=self.text_color,
                            bd=0, insertbackground="white", justify="center")
        id_entry.pack(pady=10, padx=40, fill="x")
        id_entry.focus_set()

        # Show currently active member (if any)
        if self.active_member:
            tk.Label(container,
                     text=f"✓ ACTIVE: {self.active_member['name']}  |  Coupons: {self.active_member['coupons']}",
                     font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.success_color
                     ).pack(pady=(0, 5))
        id_entry.bind("<Return>", lambda e: perform_search())

        def perform_search():
            val = id_entry.get().strip()
            if not val:
                messagebox.showwarning("Input Error", "Please enter a card ID or phone number.")
                return
            res = find_loyalty_member(val)
            print(f"DEBUG - Member found: {res}")
            if res:
                self.active_member = {
                    'id':      res[0],
                    'name':    res[1],
                    'points':  int(res[2]),
                    'coupons': int(res[3]),
                    'used':    0,
                }
                messagebox.showinfo("Member Active",
                                    f"Customer: {res[1]}\nPoints: {int(res[2])}\nAvailable Coupons: {int(res[3])}")
                self.loyalty_menu()  # Refresh to show coupon button
            else:
                messagebox.showerror("Error", "No member found with that ID or Phone.")

        tk.Button(container, text="ASSIGN TO ORDER", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=perform_search).pack(pady=10, padx=40, fill="x", ipady=5)

        tk.Button(container, text="REGISTER NEW MEMBER", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self.add_loyalty_screen).pack(pady=10, padx=40, fill="x", ipady=5)
        
        tk.Button(container, text="DELETE MEMBER", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self.delete_loyalty_member).pack(pady=10, padx=40, fill="x", ipady=5)

        # Show redeem button only if member has coupons
        if self.active_member and int(self.active_member.get('coupons', 0)) > 0:
            tk.Button(container,
                      text=f"REDEEM COUPONS  ({self.active_member['coupons']} available)",
                      bg="#9b59b6", fg=self.text_color,
                      font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                      command=self.open_coupon_redemption).pack(pady=5, padx=40, fill="x", ipady=5)

        tk.Button(self.main_frame, text="BACK TO POS", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self.show_pos_screen).place(relx=0.45, rely=0.85, relwidth=0.1, relheight=0.05)

    # ------------------------------------------------------------------
    # Coupon Redemption Popup
    # ------------------------------------------------------------------

    def open_coupon_redemption(self):
        if self.active_member.get('used', 0) > 0:
            messagebox.showwarning("Warning", "Coupons already applied to this order.")
            return

        redeem_win = tk.Toplevel(self.root)
        redeem_win.title("Redeem Coupons")
        redeem_win.geometry("600x750")
        redeem_win.configure(bg=self.bg_color)

        selected_coupons = set()
        coupon_buttons   = {}

        # --- Helpers ---
        def update_button_ui(btn, is_selected):
            btn.configure(bg=self.success_color if is_selected else self.card_color,
                          fg="white" if is_selected else self.text_color)

        def select_all():
            for cpn_id, btn in coupon_buttons.items():
                selected_coupons.add(cpn_id)
                update_button_ui(btn, True)

        def deselect_all():
            selected_coupons.clear()
            for btn in coupon_buttons.values():
                update_button_ui(btn, False)

        def toggle_coupon(btn, cpn_id):
            if cpn_id in selected_coupons:
                selected_coupons.discard(cpn_id)
                update_button_ui(btn, False)
            else:
                selected_coupons.add(cpn_id)
                update_button_ui(btn, True)

        def confirm_selection():
            count = len(selected_coupons)
            redeem_win.destroy()
            if count == 0:
                return

            discount = count * 3.0
            if discount > self.sum:
                messagebox.showerror("Error",
                                     f"Discount ({discount:.2f}€) exceeds order total ({self.sum:.2f}€).")
                return

            self.active_member['used'] = count
            self.sum -= discount
            self.temp_cart.append(f"LOYALTY  DISC x{count}  -{discount:>15.2f}€")
            self.show_pos_screen()

        # --- Layout ---
        tk.Label(redeem_win, text="AVAILABLE COUPONS", font=("Segoe UI", 18, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(side="top", pady=(20, 10))

        action_bar = tk.Frame(redeem_win, bg=self.bg_color)
        action_bar.pack(side="bottom", fill="x", pady=20)

        tk.Button(action_bar, text="APPLY SELECTED", bg=self.accent_color, fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, padx=40,
                  command=confirm_selection).pack(side="right", padx=40)
        tk.Button(action_bar, text="CLOSE", bg=self.danger_color, fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, padx=40,
                  command=redeem_win.destroy).pack(side="left", padx=40)

        ctrl_frame = tk.Frame(redeem_win, bg=self.bg_color)
        ctrl_frame.pack(side="top", fill="x", padx=30, pady=10)

        tk.Button(ctrl_frame, text="SELECT ALL", bg=self.card_color, fg=self.accent_color,
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10,
                  command=select_all).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="DESELECT ALL", bg=self.card_color, fg=self.danger_color,
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10,
                  command=deselect_all).pack(side="left", padx=5)

        # Scrollable coupon list
        container = tk.Frame(redeem_win, bg=self.bg_color)
        container.pack(side="top", fill="both", expand=True, padx=20)

        canvas    = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg_color)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=540)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        available_count = int(self.active_member.get('coupons', 0))
        for _ in range(available_count):
            rand_id = "CPN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            btn = tk.Button(scroll_frame,
                            text=f"🎟️  {rand_id}    |    VALUE: 3.00€",
                            font=("Segoe UI", 12, "bold"), bg=self.card_color, fg=self.text_color,
                            bd=0, padx=20, pady=15, cursor="hand2", anchor="w", justify="left")
            btn.pack(fill="x", pady=5, padx=10)
            btn.configure(command=lambda b=btn, r=rand_id: toggle_coupon(b, r))
            coupon_buttons[rand_id] = btn

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ------------------------------------------------------------------
    # New Member Registration Popup
    # ------------------------------------------------------------------

    def add_loyalty_screen(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("New Loyalty Member")
        reg_win.geometry("500x400")
        reg_win.configure(bg=self.bg_color)
        phone_e.bind("<Return>", lambda e: save())


        tk.Label(reg_win, text="MEMBER REGISTRATION", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        tk.Label(reg_win, text="FULL NAME:", font=("Segoe UI", 10, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(pady=(10, 0))
        name_e = tk.Entry(reg_win, font=("Segoe UI", 14), bg=self.card_color, fg=self.text_color,
                          bd=0, insertbackground="white", justify="center")
        name_e.pack(pady=5, padx=50, fill="x")

        tk.Label(reg_win, text="PHONE NUMBER:", font=("Segoe UI", 10, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(pady=(10, 0))
        phone_e = tk.Entry(reg_win, font=("Segoe UI", 14), bg=self.card_color, fg=self.text_color,
                           bd=0, insertbackground="white", justify="center")
        phone_e.pack(pady=5, padx=50, fill="x")

        def save():
            if add_loyalty_member(name_e.get(), phone_e.get()):
                reg_win.destroy()
                self.loyalty_menu()

        tk.Button(reg_win, text="CONFIRM & GENERATE CARD", bg=self.success_color, fg=self.text_color,
                  font=("Segoe UI", 11, "bold"), bd=0,
                  command=save).pack(pady=30, padx=50, fill="x", ipady=10)

    def delete_loyalty_member(self):
        def delete():
            db_delete_loyalty_member(cardid_e.get())
            del_win.destroy()
            self.loyalty_menu()
        del_win = tk.Toplevel(self.root)
        del_win.title("New Loyalty Member")
        del_win.geometry("500x400")
        del_win.configure(bg=self.bg_color)
        

        tk.Label(del_win, text="MEMBER DELETION", font=("Segoe UI", 16, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=20)

        tk.Label(del_win, text="CARD ID:", font=("Segoe UI", 10, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(pady=(10, 0))
        cardid_e = tk.Entry(del_win, font=("Segoe UI", 14), bg=self.card_color, fg=self.text_color,
                          bd=0, insertbackground="white", justify="center")
        cardid_e.pack(pady=5, padx=50, fill="x")

        tk.Button(del_win, text="CONFIRM", bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 11, "bold"), bd=0,
                  command=delete).pack(pady=30, padx=50, fill="x", ipady=10)
        cardid_e.bind("<Return>", lambda e: delete())


        

        
