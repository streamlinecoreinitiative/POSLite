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

# Fetch inventory items
def fetch_inventory():
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    connection.close()
    return items

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

# Delete product from inventory
def delete_inventory_product(item_id):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    connection.commit()
    connection.close()

# Save sale to database
def save_sale(product_id, quantity, total):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO sales (product_id, quantity, total, sale_date) VALUES (?, ?, ?, ?)",
                   (product_id, quantity, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    connection.commit()
    connection.close()

# Fetch sales for report (used in report tab)
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

# Fetch recent sales for the Sales Tab
def fetch_recent_sales(limit=10):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    # Join with inventory to get the product name
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
        ORDER BY s.id DESC
        LIMIT ?
    """, (limit,))
    sales = cursor.fetchall()
    connection.close()
    return sales

# GUI Setup
class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POS Lite")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
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
        # Inventory Management Fields
        ttk.Label(self.inventory_tab, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
        self.product_name_entry = ttk.Entry(self.inventory_tab)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Quantity").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.inventory_tab)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Price").grid(row=2, column=0, padx=5, pady=5)
        self.price_entry = ttk.Entry(self.inventory_tab)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons for saving, updating, and deleting products
        self.save_button = ttk.Button(self.inventory_tab, text="Save Product", command=self.save_product)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.update_button = ttk.Button(self.inventory_tab, text="Update Product", command=self.update_product)
        self.update_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.delete_button = ttk.Button(self.inventory_tab, text="Delete Product", command=self.delete_product)
        self.delete_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Inventory Treeview
        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.grid(row=6, column=0, columnspan=2, pady=5)

        # Bind selection to auto-populate the entry fields
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.load_inventory()

    def setup_sales_tab(self):
        # Sales Management Fields
        ttk.Label(self.sales_tab, text="Product ID").grid(row=0, column=0, padx=5, pady=5)
        self.product_id_entry = ttk.Entry(self.sales_tab)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sales_tab, text="Quantity").grid(row=1, column=0, padx=5, pady=5)
        self.sale_quantity_entry = ttk.Entry(self.sales_tab)
        self.sale_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        self.sell_button = ttk.Button(self.sales_tab, text="Sell", command=self.sell_product)
        self.sell_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Sales Treeview (displays recent sales)
        self.sales_tree = ttk.Treeview(self.sales_tab, columns=("ID", "Name", "Quantity", "Total", "Date"), show="headings")
        self.sales_tree.heading("ID", text="Sale ID")
        self.sales_tree.heading("Name", text="Product Name")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Total", text="Total")
        self.sales_tree.heading("Date", text="Date/Time")
        self.sales_tree.grid(row=3, column=0, columnspan=2, pady=5)

        # Optional: Add a Refresh Button for Sales Tab
        self.refresh_sales_button = ttk.Button(self.sales_tab, text="Refresh Sales", command=self.load_sales)
        self.refresh_sales_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Load sales when starting up
        self.load_sales()

    def setup_report_tab(self):
        # Sales Report Fields
        ttk.Label(self.report_tab, text="Start Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(self.report_tab)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.report_tab, text="End Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(self.report_tab)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.report_button = ttk.Button(self.report_tab, text="Generate Report", command=self.generate_report)
        self.report_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Report Treeview
        self.report_tree = ttk.Treeview(self.report_tab, columns=("ID", "Name", "Quantity", "Total", "Date"), show="headings")
        self.report_tree.heading("ID", text="ID")
        self.report_tree.heading("Name", text="Name")
        self.report_tree.heading("Quantity", text="Quantity")
        self.report_tree.heading("Total", text="Total")
        self.report_tree.heading("Date", text="Date")
        self.report_tree.grid(row=3, column=0, columnspan=2, pady=5)

    # Auto-populate inventory fields on selection
    def on_tree_select(self, event):
        selected = self.inventory_tree.selection()
        if selected:
            values = self.inventory_tree.item(selected[0], "values")
            self.product_name_entry.delete(0, tk.END)
            self.product_name_entry.insert(0, values[1])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, values[2])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[3])

    def save_product(self):
        try:
            name = self.product_name_entry.get()
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
            save_product(name, quantity, price)
            messagebox.showinfo("Success", "Product saved successfully!")
            self.load_inventory()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {e}")

    def update_product(self):
        selected = self.inventory_tree.selection()
        if selected:
            item_id = self.inventory_tree.item(selected[0], "values")[0]
            try:
                name = self.product_name_entry.get()
                quantity = int(self.quantity_entry.get())
                price = float(self.price_entry.get())
                update_inventory_product(item_id, name, quantity, price)
                messagebox.showinfo("Success", "Product updated successfully!")
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")
        else:
            messagebox.showerror("Error", "No product selected!")

    def delete_product(self):
        selected = self.inventory_tree.selection()
        if selected:
            item_id = self.inventory_tree.item(selected[0], "values")[0]
            try:
                delete_inventory_product(item_id)
                messagebox.showinfo("Success", "Product deleted successfully!")
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")
        else:
            messagebox.showerror("Error", "No product selected!")

    def load_inventory(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
        for item in fetch_inventory():
            self.inventory_tree.insert("", tk.END, values=item)

    def load_sales(self):
        # Clear current sales tree
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        # Fetch recent sales and insert them into the sales tree
        for sale in fetch_recent_sales(limit=10):
            self.sales_tree.insert("", tk.END, values=sale)

    def sell_product(self):
        try:
            product_id = int(self.product_id_entry.get())
            quantity = int(self.sale_quantity_entry.get())
            inventory = fetch_inventory()
            for item in inventory:
                if item[0] == product_id:
                    if item[2] >= quantity:
                        total = quantity * item[3]
                        save_sale(product_id, quantity, total)
                        new_quantity = item[2] - quantity
                        update_inventory_product(product_id, item[1], new_quantity, item[3])
                        messagebox.showinfo("Success", f"Sale completed! Total: ${total}")
                        self.load_inventory()
                        self.load_sales()  # Refresh sales table after sale
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
        try:
            sales = fetch_sales_report(start_date, end_date)
            for row in self.report_tree.get_children():
                self.report_tree.delete(row)
            for sale in sales:
                self.report_tree.insert("", tk.END, values=sale)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()