import tkinter as tk
from tkinter import messagebox
import os
from datetime import date
import pdfplumber
from backend import cancel_transaction, parse_receipt_pdf




class HistoryMixin:

    def transaction_history(self):
        self.save_cart_state()
        self.clear_frame()

        # ── Title ──────────────────────────────────────────────────────────
        tk.Label(self.main_frame, text="TRANSACTION HISTORY",
                 font=("Segoe UI", 20, "bold"),
                 bg=self.bg_color, fg=self.text_color).pack(pady=(20, 5))

        # ── Top bar: date picker + search ──────────────────────────────────
        top_bar = tk.Frame(self.main_frame, bg=self.bg_color)
        top_bar.pack(fill="x", padx=40, pady=(0, 10))

        tk.Label(top_bar, text="📅", font=("Segoe UI", 14),
                 bg=self.bg_color, fg=self.accent_color).pack(side="left", padx=(0, 6))

        today = date.today()
        self.hist_day   = tk.StringVar(value=str(today.day).zfill(2))
        self.hist_month = tk.StringVar(value=str(today.month).zfill(2))
        self.hist_year  = tk.StringVar(value=str(today.year))

        spin_cfg = dict(bg=self.card_color, fg=self.text_color,
                        font=("Segoe UI", 12), bd=0, highlightthickness=0,
                        insertbackground="white", buttonbackground=self.card_color,
                        relief="flat")

        tk.Spinbox(top_bar, from_=1, to=31, width=3,
                   textvariable=self.hist_day, **spin_cfg).pack(side="left")
        tk.Label(top_bar, text="/", bg=self.bg_color,
                 fg=self.text_color, font=("Segoe UI", 12)).pack(side="left")
        tk.Spinbox(top_bar, from_=1, to=12, width=3,
                   textvariable=self.hist_month, **spin_cfg).pack(side="left")
        tk.Label(top_bar, text="/", bg=self.bg_color,
                 fg=self.text_color, font=("Segoe UI", 12)).pack(side="left")
        tk.Spinbox(top_bar, from_=2020, to=2100, width=6,
                   textvariable=self.hist_year, **spin_cfg).pack(side="left", padx=(0, 12))

        tk.Button(top_bar, text="🔍  SEARCH", bg=self.accent_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, padx=16, pady=4, cursor="hand2",
                  command=self._load_receipts).pack(side="left")

        # Daily total shown after search
        self.daily_total_label = tk.Label(top_bar, text="",
                                          font=("Segoe UI", 10, "bold"),
                                          bg=self.bg_color, fg=self.success_color)
        self.daily_total_label.pack(side="right", padx=10)

        # ── Scrollable receipt list ────────────────────────────────────────
        list_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        self.hist_canvas = tk.Canvas(list_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                 command=self.hist_canvas.yview)
        self.hist_scroll_frame = tk.Frame(self.hist_canvas, bg=self.bg_color)

        self.hist_scroll_frame.bind(
            "<Configure>",
            lambda e: self.hist_canvas.configure(
                scrollregion=self.hist_canvas.bbox("all")))

        self.hist_canvas.create_window((0, 0), window=self.hist_scroll_frame, anchor="nw")
        self.hist_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.hist_canvas.pack(side="left", fill="both", expand=True)
        self.hist_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.hist_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Placeholder
        self.hist_placeholder = tk.Label(
            self.hist_scroll_frame,
            text="Select a date and press SEARCH",
            font=("Segoe UI", 12), bg=self.bg_color, fg="#555555")
        self.hist_placeholder.pack(pady=40)

        # ── Back button ────────────────────────────────────────────────────
        tk.Button(self.main_frame, text="← BACK TO POS",
                  bg=self.danger_color, fg=self.text_color,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self.show_pos_screen).pack(pady=(0, 15))

        # Auto-load today on open
        self._load_receipts()

    # ──────────────────────────────────────────────────────────────────────

    def _load_receipts(self):
        for widget in self.hist_scroll_frame.winfo_children():
            widget.destroy()

        try:
            day = self.hist_day.get().zfill(2)
            month = self.hist_month.get().zfill(2)
            year = self.hist_year.get()
            folder = f"{year}-{month}-{day}"
        except Exception:
            messagebox.showerror("Date Error", "Invalid date selected.")
            return

        if not os.path.exists(folder):
            tk.Label(self.hist_scroll_frame, text=f"No transactions found for {day}/{month}/{year}",
                     font=("Segoe UI", 12), bg=self.bg_color, fg="#555555").pack(pady=40)
            self.daily_total_label.config(text="")
            return

        pdf_files = sorted([f for f in os.listdir(folder) if f.endswith(".pdf")])

        daily_total = 0.0
        row_num = 0
        for fname in pdf_files:
            filepath = os.path.join(folder, fname)
            is_cancelled = fname.startswith("CANCELLED_")

            # Skip internal cancellation receipts
            if fname.lower().startswith("cancelled_receipt_"):
                continue

            row_num += 1

            # --- ROBUST TIME EXTRACTION ---
            # Instead of replacing specific words, we just take the digits
            try:
                # Clean name to find the HHMMSS part
                clean_name = fname.replace("CANCELLED_", "").replace(".pdf", "")
                # Find the first sequence of 6 digits
                import re
                time_match = re.search(r'\d{6}', clean_name)
                if time_match:
                    t = time_match.group()
                    time_str = f"{t[:2]}:{t[2:4]}:{t[4:6]}"
                else:
                    time_str = "??:??:??"
            except:
                time_str = "??:??:??"

            # Use our new universal parser
            items, total = parse_receipt_pdf(filepath)

            if total and not is_cancelled:
                daily_total += total

            # Pass a flag if it's an invoice to show a different icon
            is_invoice = "invoice" in fname.lower()
            self._add_receipt_row(row_num, time_str, filepath, items, total, is_cancelled, is_invoice)

        self.daily_total_label.config(text=f"Day Total:  {daily_total:.2f} EUR")

    # ──────────────────────────────────────────────────────────────────────

    def _add_receipt_row(self, number, time_str, filepath, items, total, is_cancelled=False, is_invoice=False):
        # Cancelled rows get a dark red tint, normal rows use card color
        card_bg = "#2a1010" if is_cancelled else self.card_color
        card = tk.Frame(self.hist_scroll_frame, bg=card_bg,
                        highlightbackground="#8b0000" if is_cancelled else "#333333",
                        highlightthickness=1)
        card.pack(fill="x", pady=5, padx=5)

        # ── Header row ────────────────────────────────────────────────────
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", padx=15, pady=10)

        arrow_var = tk.StringVar(value="▶")
        arrow_lbl = tk.Label(header, textvariable=arrow_var,
                             font=("Segoe UI", 10), bg=card_bg,
                             fg=self.accent_color, cursor="hand2")
        arrow_lbl.pack(side="left", padx=(0, 6))

        # 1. Determine the Label text and Color based on status
        if is_cancelled:
            label_text = f"TRANSACTION #{number:02d} [CANCELLED]"
            label_color = "#ff6b6b"  # Red for cancelled
            icon = "🚫"
        elif is_invoice:
            label_text = f"INVOICE #{number:02d}"
            label_color = self.text_color
            icon = "🏢"
        else:
            label_text = f"RECEIPT #{number:02d}"
            label_color = self.text_color
            icon = "🧾"

        # 2. Create the Icon Label
        tk.Label(header, text=icon, font=("Segoe UI", 16),
                 bg=card_bg).pack(side="left", padx=(0, 8))

        # 3. Create the Main Info Label (Replaces your old code)
        tk.Label(header,
                 text=f"{label_text}   —   {time_str}",
                 font=("Segoe UI", 11, "bold"),
                 bg=card_bg, fg=label_color).pack(side="left")

        if total is not None:
            amount_color = "#ff6b6b" if is_cancelled else self.success_color
            tk.Label(header, text=f"{total:.2f} EUR",
                     font=("Segoe UI", 11, "bold"),
                     bg=card_bg, fg=amount_color).pack(side="left", padx=20)

        # Cancel button — only shown on non-cancelled receipts
        if not is_cancelled:
            tk.Button(header, text="✕  CANCEL",
                      bg=self.danger_color, fg=self.text_color,
                      font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3,
                      cursor="hand2",
                      command=lambda fp=filepath, i=items, t=total, c=card, h=header:
                          self._confirm_cancel(fp, i, t, c, h)
                      ).pack(side="right", padx=(6, 0))

        preview_btn = tk.Button(header, text="👁  PREVIEW",
                                bg=self.accent_color, fg=self.text_color,
                                font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=3,
                                cursor="hand2")
        preview_btn.pack(side="right")

        # ── Inline panel (hidden by default) ─────────────────────────────
        panel = tk.Frame(card, bg="#161616")
        # panel is NOT packed yet — toggle will show/hide it

        # Divider line at top of panel
        tk.Frame(panel, bg="#333333", height=1).pack(fill="x")

        inner_pad = tk.Frame(panel, bg="#161616")
        inner_pad.pack(fill="x", padx=20, pady=10)

        # Column headers
        col_hdr = tk.Frame(inner_pad, bg="#161616")
        col_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(col_hdr, text="PRODUCT", font=("Segoe UI", 9, "bold"),
                 bg="#161616", fg=self.accent_color, width=30, anchor="w").pack(side="left")
        tk.Label(col_hdr, text="QTY", font=("Segoe UI", 9, "bold"),
                 bg="#161616", fg=self.accent_color, width=6, anchor="center").pack(side="left")
        tk.Label(col_hdr, text="TOTAL", font=("Segoe UI", 9, "bold"),
                 bg="#161616", fg=self.accent_color, width=12, anchor="e").pack(side="right")

        tk.Frame(inner_pad, bg="#333333", height=1).pack(fill="x", pady=(0, 6))

        # Item rows
        if not items:
            tk.Label(inner_pad, text="Could not parse receipt items.",
                     font=("Segoe UI", 10), bg="#161616", fg="#888888").pack(pady=8)
        else:
            for item in items:
                row = tk.Frame(inner_pad, bg="#161616")
                row.pack(fill="x", pady=2)
                if item.get('is_discount'):
                    c = "#9b59b6"
                    tk.Label(row, text="⭐ LOYALTY DISCOUNT",
                             font=("Segoe UI", 10, "italic"),
                             bg="#161616", fg=c, width=30, anchor="w").pack(side="left")
                    tk.Label(row, text="—",
                             font=("Segoe UI", 10), bg="#161616", fg=c,
                             width=6, anchor="center").pack(side="left")
                    tk.Label(row, text=f"-{item['total']} €",
                             font=("Segoe UI", 10, "bold"),
                             bg="#161616", fg=c, width=12, anchor="e").pack(side="right")
                else:
                    tk.Label(row, text=item['name'],
                             font=("Segoe UI", 10),
                             bg="#161616", fg=self.text_color,
                             width=30, anchor="w").pack(side="left")
                    tk.Label(row, text=item['qty'],
                             font=("Segoe UI", 10),
                             bg="#161616", fg="#aaaaaa",
                             width=6, anchor="center").pack(side="left")
                    tk.Label(row, text=f"{item['total']} €",
                             font=("Segoe UI", 10, "bold"),
                             bg="#161616", fg=self.success_color,
                             width=12, anchor="e").pack(side="right")

        # Total footer inside panel
        tk.Frame(inner_pad, bg="#333333", height=1).pack(fill="x", pady=(8, 4))
        footer = tk.Frame(inner_pad, bg="#161616")
        footer.pack(fill="x")
        tk.Label(footer, text="TOTAL PAID", font=("Segoe UI", 11, "bold"),
                 bg="#161616", fg=self.text_color).pack(side="left")
        total_text = f"{total:.2f} EUR" if total is not None else "N/A"
        tk.Label(footer, text=total_text, font=("Segoe UI", 13, "bold"),
                 bg="#161616", fg=self.success_color).pack(side="right")

        # ── Toggle logic ──────────────────────────────────────────────────
        is_open = [False]

        def toggle(event=None):
            if is_open[0]:
                panel.pack_forget()
                arrow_var.set("▶")
                preview_btn.config(text="👁  PREVIEW")
            else:
                panel.pack(fill="x")
                arrow_var.set("▼")
                preview_btn.config(text="▲  CLOSE")
            is_open[0] = not is_open[0]
            # Refresh scroll region
            self.hist_scroll_frame.update_idletasks()
            self.hist_canvas.configure(
                scrollregion=self.hist_canvas.bbox("all"))

        preview_btn.config(command=toggle)
        arrow_lbl.bind("<Button-1>", toggle)
        header.bind("<Button-1>", toggle)

    # ──────────────────────────────────────────────────────────────────────

    def _confirm_cancel(self, filepath, items, total, card, header):
        confirmed = messagebox.askyesno(
            "Cancel Transaction",
            f"Are you sure you want to cancel this transaction?\n\n"
            f"Total: {total:.2f} EUR\n"
        )
        if not confirmed:
            return

        success = cancel_transaction(filepath, items, total)
        if success:
            # Visually mark the card as cancelled immediately
            card.config(bg="#2a1010", highlightbackground="#8b0000")
            for widget in header.winfo_children():
                try:
                    widget.config(bg="#2a1010")
                except Exception:
                    pass
                # swap icon and label text
                if isinstance(widget, tk.Label):
                    if widget.cget("text") == "🧾":
                        widget.config(text="🚫")
                    current = widget.cget("text")
                    if "TRANSACTION" in current and "[CANCELLED]" not in current:
                        widget.config(text=current + "   [CANCELLED]", fg="#ff6b6b")
                # remove the cancel button
                if isinstance(widget, tk.Button) and "CANCEL" in widget.cget("text"):
                    widget.destroy()