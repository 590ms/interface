# Interface (Nexus POS)

A point-of-sale desktop application built with Python and Tkinter, backed by a MySQL database. It covers the daily workflow of a small retail shop: selling products, managing stock, handling customers and loyalty members, and issuing receipts and invoices as PDFs.

## Features

- **Point of sale:** build a cart, check out, and generate a PDF receipt
- **Stock management:** add and remove products and track quantities
- **Clients:** cardholder clients with a balance, and walk-in clients identified by tax number
- **Loyalty program:** members with reward tracking and coupons
- **Invoices:** PDF invoices for client sales
- **Transaction history:** browse past receipts and cancel a transaction
- Dark-themed full-screen interface

## Tech stack

- Python 3, Tkinter
- MySQL via PyMySQL
- fpdf (PDF generation) and pdfplumber (reading receipts back)

## Setup

```bash
git clone https://github.com/590ms/interface.git
cd interface
pip install -r requirements.txt python-dotenv
```

Create a `.env` file in the project folder with your own database details:

```
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
```

Run the app:

```bash
python main.py
```

## Project structure

```
main.py          entry point
pos_system.py    combines the app and all screens
app.py           main window, theme and startup
backend.py       database access, receipts, invoices, loyalty logic
screens/         POS, stock, clients, loyalty and history screens
```

## Status

In active development. Feedback and contributions are welcome: open an issue or a pull request.
