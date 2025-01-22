import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Initialize Database
def initialize_db():
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            total REAL,
            sale_date TEXT,
            FOREIGN KEY (product_id) REFERENCES inventory (id)
        )
    """)
    connection.commit()
    connection.close()

# Save product to inventory
def save_product(name, quantity, price):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO inventory (product_name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    connection.commit()
    connection.close()

# Fetch inventory
def fetch_inventory():
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    connection.close()
    return items

# Save sale to database
def save_sale(product_id, quantity, total):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO sales (product_id, quantity, total, sale_date) VALUES (?, ?, ?, ?)",
                   (product_id, quantity, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    connection.commit()
    connection.close()

# Fetch sales for report
def fetch_sales_report(start_date, end_date):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            s.id, 
            i.product_name, 
            s.quantity, 
            s.total, 
            s.sale_date
        FROM 
            sales s
        JOIN 
            inventory i 
        ON 
            s.product_id = i.id
        WHERE 
            DATE(s.sale_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    sales = cursor.fetchall()
    connection.close()
    return sales

# Update product in inventory
def update_inventory_product(item_id, name, quantity, price):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE inventory
        SET product_name = ?, quantity = ?, price = ?
        WHERE id = ?
    """, (name, quantity, price, item_id))
    connection.commit()
    connection.close()

# GUI Setup
class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POS Lite")

        # Frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.inventory_tab = ttk.Frame(self.notebook)
        self.sales_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.sales_tab, text="Sales")
        self.notebook.add(self.report_tab, text="Reports")

        self.setup_inventory_tab()
        self.setup_sales_tab()
        self.setup_report_tab()

    def setup_inventory_tab(self):
        # Inventory Management
        ttk.Label(self.inventory_tab, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
        self.product_name_entry = ttk.Entry(self.inventory_tab)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Quantity").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.inventory_tab)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Price").grid(row=2, column=0, padx=5, pady=5)
        self.price_entry = ttk.Entry(self.inventory_tab)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        self.save_button = ttk.Button(self.inventory_tab, text="Save Product", command=self.save_product)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.update_button = ttk.Button(self.inventory_tab, text="Update Product", command=self.update_product)
        self.update_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.grid(row=5, column=0, columnspan=2, pady=10)

        self.load_inventory()

    def setup_sales_tab(self):
        # Sales Management
        ttk.Label(self.sales_tab, text="Product ID").grid(row=0, column=0, padx=5, pady=5)
        self.product_id_entry = ttk.Entry(self.sales_tab)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sales_tab, text="Quantity").grid(row=1, column=0, padx=5, pady=5)
        self.sale_quantity_entry = ttk.Entry(self.sales_tab)
        self.sale_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        self.sell_button = ttk.Button(self.sales_tab, text="Sell", command=self.sell_product)
        self.sell_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.sales_tree = ttk.Treeview(self.sales_tab, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Name", text="Name")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Price", text="Price")
        self.sales_tree.grid(row=3, column=0, columnspan=2, pady=10)

    def setup_report_tab(self):
        # Sales Report
        ttk.Label(self.report_tab, text="Start Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(self.report_tab)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.report_tab, text="End Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(self.report_tab)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.report_button = ttk.Button(self.report_tab, text="Generate Report", command=self.generate_report)
        self.report_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.report_tree = ttk.Treeview(self.report_tab, columns=("ID", "Name", "Quantity", "Total", "Date"), show="headings")
        self.report_tree.heading("ID", text="ID")
        self.report_tree.heading("Name", text="Name")
        self.report_tree.heading("Quantity", text="Quantity")
        self.report_tree.heading("Total", text="Total")
        self.report_tree.heading("Date", text="Date")
        self.report_tree.grid(row=3, column=0, columnspan=2, pady=10)

    def save_product(self):
        name = self.product_name_entry.get()
        quantity = int(self.quantity_entry.get())
        price = float(self.price_entry.get())
        save_product(name, quantity, price)
        messagebox.showinfo("Success", "Product saved successfully!")
        self.load_inventory()

    def update_product(self):
        selected = self.inventory_tree.selection()
        if selected:
            item_id = self.inventory_tree.item(selected[0], "values")[0]  # Get ID from selected row
            name = self.product_name_entry.get()
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
            try:
                update_inventory_product(item_id, name, quantity, price)  # Call the fixed function
                messagebox.showinfo("Success", "Product updated successfully!")
                self.load_inventory()  # Refresh inventory
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")
        else:
            messagebox.showerror("Error", "No product selected!")

    def load_inventory(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
        for item in fetch_inventory():
            self.inventory_tree.insert("", tk.END, values=item)

    def sell_product(self):
        try:
            product_id = int(self.product_id_entry.get())
            quantity = int(self.sale_quantity_entry.get())
            inventory = fetch_inventory()
            for item in inventory:
                if item[0] == product_id:  # Match product by ID
                    if item[2] >= quantity:  # Check inventory quantity
                        total = quantity * item[3]  # Calculate total price
                        save_sale(product_id, quantity, total)  # Save the sale
                        new_quantity = item[2] - quantity  # Update inventory
                        update_inventory_product(product_id, item[1], new_quantity, item[3])  # Reflect new inventory quantity
                        messagebox.showinfo("Success", f"Sale completed! Total: ${total}")
                        self.load_inventory()  # Refresh inventory
                        return
                    else:
                        messagebox.showerror("Error", "Not enough inventory!")
                        return
            messagebox.showerror("Error", "Product not found!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_report(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        sales = fetch_sales_report(start_date, end_date)
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)
        for sale in sales:
            self.report_tree.insert("", tk.END, values=sale)


# Initialize app
if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()