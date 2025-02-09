import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, date
import shutil
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------- Multi-language Support ----------------------
translations = {
    "en": {
        "title": "POS Lite",
        "inventory_tab": "Inventory",
        "sales_tab": "Sales",
        "reports_tab": "Reports",
        "product_name": "Product Name",
        "quantity": "Quantity",
        "price": "Price",
        "threshold": "Threshold",
        "save_product": "Save Product",
        "update_product": "Update Product",
        "delete_product": "Delete Product",
        "product_id": "Product ID",
        "sale_quantity": "Sale Quantity",
        "payment_method": "Payment Method",
        "sell": "Sell",
        "refresh_sales": "Refresh Sales",
        "start_date": "Start Date (YYYY-MM-DD)",
        "end_date": "End Date (YYYY-MM-DD)",
        "generate_report": "Generate Report",
        "sales_chart": "Show Sales Chart",
        "inventory_chart": "Show Inventory Chart",
        "backup": "Backup DB",
        "restore": "Restore DB",
        "export_csv": "Export CSV",
        "dashboard": "Dashboard: Total Products: {total_products} | Low Stock: {low_stock} | Today's Sales: ${today_sales:.2f}",
        "login_title": "Login",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "help": "Help",
        "help_text": "This POS system supports Inventory, Sales, and Reports. Use the menus to switch languages and view help.",
        "invalid_credentials": "Invalid username or password.",
        "select_product": "No product selected!",
        "not_enough_inventory": "Not enough inventory!",
        "sale_completed": "Sale completed! Total: ${total}",
        "backup_success": "Backup successful!",
        "restore_success": "Restore successful!",
        "export_success": "Export successful!",
        "choose_language": "Choose Language"
    },
    "sw": {
        "title": "POS Lite",
        "inventory_tab": "Bidhaa",
        "sales_tab": "Uuzaji",
        "reports_tab": "Ripoti",
        "product_name": "Jina la Bidhaa",
        "quantity": "Kiasi",
        "price": "Bei",
        "threshold": "Kipimo cha chini",
        "save_product": "Hifadhi Bidhaa",
        "update_product": "Sasisha Bidhaa",
        "delete_product": "Futa Bidhaa",
        "product_id": "ID ya Bidhaa",
        "sale_quantity": "Kiasi cha Uuzaji",
        "payment_method": "Njia ya Malipo",
        "sell": "Uza",
        "refresh_sales": "Sasisha Uuzaji",
        "start_date": "Tarehe ya Mwanzo (YYYY-MM-DD)",
        "end_date": "Tarehe ya Mwisho (YYYY-MM-DD)",
        "generate_report": "Tengeneza Ripoti",
        "sales_chart": "Onyesha Chati ya Uuzaji",
        "inventory_chart": "Onyesha Chati ya Bidhaa",
        "backup": "Hifadhi Nakala",
        "restore": "Rejesha Nakala",
        "export_csv": "Hamisha CSV",
        "dashboard": "Dashibodi: Jumla Bidhaa: {total_products} | Bidhaa Zenye kipimo cha chini: {low_stock} | Mauzo ya Leo: ${today_sales:.2f}",
        "login_title": "Ingia",
        "username": "Jina la Mtumiaji",
        "password": "Nywila",
        "login": "Ingia",
        "help": "Msaada",
        "help_text": "Mfumo huu wa POS unaunga mkono Bidhaa, Uuzaji, na Ripoti. Tumia menyu kubadilisha lugha na kuona msaada.",
        "invalid_credentials": "Jina la mtumiaji au nywila si sahihi.",
        "select_product": "Hakuna bidhaa imechaguliwa!",
        "not_enough_inventory": "Hakuna bidhaa za kutosha!",
        "sale_completed": "Uuzaji umefanikiwa! Jumla: ${total}",
        "backup_success": "Hifadhi nakala imefanikiwa!",
        "restore_success": "Rejesha nakala imefanikiwa!",
        "export_success": "Hamisha imefanikiwa!",
        "choose_language": "Chagua Lugha"
    }
}
current_lang = "en"


def t(key, **kwargs):
    return translations[current_lang].get(key, key).format(**kwargs)


# ---------------------- Database Functions ----------------------
def initialize_db():
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    # Inventory table with threshold
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            threshold INTEGER NOT NULL DEFAULT 0
        )
    """)
    # Sales table with payment_method
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            total REAL,
            sale_date TEXT,
            payment_method TEXT,
            FOREIGN KEY (product_id) REFERENCES inventory (id)
        )
    """)
    connection.commit()
    connection.close()


def db_save_product(name, quantity, price, threshold):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO inventory (product_name, quantity, price, threshold) VALUES (?, ?, ?, ?)",
                   (name, quantity, price, threshold))
    connection.commit()
    connection.close()


def db_fetch_inventory():
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    connection.close()
    return items


def db_update_product(item_id, name, quantity, price, threshold):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE inventory
        SET product_name = ?, quantity = ?, price = ?, threshold = ?
        WHERE id = ?
    """, (name, quantity, price, threshold, item_id))
    connection.commit()
    connection.close()


def db_delete_product(item_id):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    connection.commit()
    connection.close()


def db_save_sale(product_id, quantity, total, payment_method):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO sales (product_id, quantity, total, sale_date, payment_method) VALUES (?, ?, ?, ?, ?)",
                   (product_id, quantity, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), payment_method))
    connection.commit()
    connection.close()


def db_fetch_sales_report(start_date, end_date):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            s.id, 
            i.product_name, 
            s.quantity, 
            s.total, 
            s.sale_date,
            s.payment_method
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


def db_fetch_recent_sales(limit=10):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            s.id, 
            i.product_name, 
            s.quantity, 
            s.total, 
            s.sale_date,
            s.payment_method
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


def backup_db():
    try:
        shutil.copy("pos_lite.db", "pos_lite_backup.db")
        return True
    except Exception as e:
        return False


def restore_db():
    try:
        shutil.copy("pos_lite_backup.db", "pos_lite.db")
        return True
    except Exception as e:
        return False


def export_inventory_to_csv(filename="inventory_export.csv"):
    items = db_fetch_inventory()
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Product Name", "Quantity", "Price", "Threshold"])
        writer.writerows(items)
    return True


def export_sales_to_csv(filename="sales_export.csv"):
    connection = sqlite3.connect("pos_lite.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    connection.close()
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Product ID", "Quantity", "Total", "Sale Date", "Payment Method"])
        writer.writerows(sales)
    return True


# ---------------------- Login Screen ----------------------
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title(t("login_title"))
        self.root.geometry("300x150")

        tk.Label(root, text=t("username")).pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text=t("password")).pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text=t("login"), command=self.check_login).pack(pady=10)

        # Hard-coded credentials for simplicity
        self.credentials = {"admin": "admin", "cashier": "1234"}

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in self.credentials and self.credentials[username] == password:
            self.root.destroy()
            main_app = tk.Tk()
            POSApp(main_app)
            main_app.mainloop()
        else:
            messagebox.showerror(t("login_title"), t("invalid_credentials"))


# ---------------------- Main POS Application ----------------------
class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title(t("title"))

        # Dashboard at the top
        self.dashboard_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
        self.dashboard_label.pack(pady=5)
        self.update_dashboard()

        # Menu for language selection and help
        self.menu_bar = tk.Menu(root)
        language_menu = tk.Menu(self.menu_bar, tearoff=0)
        language_menu.add_command(label="English", command=lambda: self.set_language("en"))
        language_menu.add_command(label="Swahili", command=lambda: self.set_language("sw"))
        self.menu_bar.add_cascade(label=t("choose_language"), menu=language_menu)
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label=t("help"), command=self.show_help)
        self.menu_bar.add_cascade(label=t("help"), menu=help_menu)
        root.config(menu=self.menu_bar)

        # Main frame with notebook
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.inventory_tab = ttk.Frame(self.notebook)
        self.sales_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.inventory_tab, text=t("inventory_tab"))
        self.notebook.add(self.sales_tab, text=t("sales_tab"))
        self.notebook.add(self.report_tab, text=t("reports_tab"))

        self.setup_inventory_tab()
        self.setup_sales_tab()
        self.setup_report_tab()

    def set_language(self, lang):
        global current_lang
        current_lang = lang
        # Update menu labels and notebook tabs
        self.menu_bar.entryconfig(0, label=t("choose_language"))
        self.menu_bar.entryconfig(1, label=t("help"))
        self.notebook.tab(0, text=t("inventory_tab"))
        self.notebook.tab(1, text=t("sales_tab"))
        self.notebook.tab(2, text=t("reports_tab"))
        self.update_dashboard()

    def show_help(self):
        messagebox.showinfo(t("help"), t("help_text"))

    def update_dashboard(self):
        inventory = db_fetch_inventory()
        total_products = len(inventory)
        low_stock = sum(1 for item in inventory if item[2] < item[4])
        # Today's sales
        today = date.today().strftime("%Y-%m-%d")
        connection = sqlite3.connect("pos_lite.db")
        cursor = connection.cursor()
        cursor.execute("SELECT SUM(total) FROM sales WHERE DATE(sale_date)=?", (today,))
        result = cursor.fetchone()
        connection.close()
        today_sales = result[0] if result[0] is not None else 0.0
        dashboard_text = t("dashboard", total_products=total_products, low_stock=low_stock, today_sales=today_sales)
        self.dashboard_label.config(text=dashboard_text)

    # ---------------------- Inventory Tab ----------------------
    def setup_inventory_tab(self):
        ttk.Label(self.inventory_tab, text=t("product_name")).grid(row=0, column=0, padx=5, pady=5)
        self.product_name_entry = ttk.Entry(self.inventory_tab)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text=t("quantity")).grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.inventory_tab)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text=t("price")).grid(row=2, column=0, padx=5, pady=5)
        self.price_entry = ttk.Entry(self.inventory_tab)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text=t("threshold")).grid(row=3, column=0, padx=5, pady=5)
        self.threshold_entry = ttk.Entry(self.inventory_tab)
        self.threshold_entry.grid(row=3, column=1, padx=5, pady=5)

        self.save_button = ttk.Button(self.inventory_tab, text=t("save_product"), command=self.save_product)
        self.save_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.update_button = ttk.Button(self.inventory_tab, text=t("update_product"), command=self.update_product)
        self.update_button.grid(row=5, column=0, columnspan=2, pady=5)

        self.delete_button = ttk.Button(self.inventory_tab, text=t("delete_product"), command=self.delete_product)
        self.delete_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Name", "Quantity", "Price", "Threshold"),
                                           show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text=t("product_name"))
        self.inventory_tree.heading("Quantity", text=t("quantity"))
        self.inventory_tree.heading("Price", text=t("price"))
        self.inventory_tree.heading("Threshold", text=t("threshold"))
        self.inventory_tree.grid(row=7, column=0, columnspan=2, pady=5)
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_inventory_select)

        self.load_inventory()

    def on_inventory_select(self, event):
        selected = self.inventory_tree.selection()
        if selected:
            values = self.inventory_tree.item(selected[0], "values")
            self.product_name_entry.delete(0, tk.END)
            self.product_name_entry.insert(0, values[1])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, values[2])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[3])
            self.threshold_entry.delete(0, tk.END)
            self.threshold_entry.insert(0, values[4])

    def save_product(self):
        try:
            name = self.product_name_entry.get()
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
            threshold = int(self.threshold_entry.get())
            db_save_product(name, quantity, price, threshold)
            messagebox.showinfo(t("title"), t("save_product") + " successful!")
            self.load_inventory()
            self.update_dashboard()
        except Exception as e:
            messagebox.showerror(t("title"), f"Error saving product: {e}")

    def update_product(self):
        selected = self.inventory_tree.selection()
        if selected:
            item_id = self.inventory_tree.item(selected[0], "values")[0]
            try:
                name = self.product_name_entry.get()
                quantity = int(self.quantity_entry.get())
                price = float(self.price_entry.get())
                threshold = int(self.threshold_entry.get())
                db_update_product(item_id, name, quantity, price, threshold)
                messagebox.showinfo(t("title"), t("update_product") + " successful!")
                self.load_inventory()
                self.update_dashboard()
            except Exception as e:
                messagebox.showerror(t("title"), f"Error updating product: {e}")
        else:
            messagebox.showerror(t("title"), t("select_product"))

    def delete_product(self):
        selected = self.inventory_tree.selection()
        if selected:
            item_id = self.inventory_tree.item(selected[0], "values")[0]
            try:
                db_delete_product(item_id)
                messagebox.showinfo(t("title"), t("delete_product") + " successful!")
                self.load_inventory()
                self.update_dashboard()
            except Exception as e:
                messagebox.showerror(t("title"), f"Error deleting product: {e}")
        else:
            messagebox.showerror(t("title"), t("select_product"))

    def load_inventory(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
        for item in db_fetch_inventory():
            self.inventory_tree.insert("", tk.END, values=item)

    # ---------------------- Sales Tab ----------------------
    def setup_sales_tab(self):
        ttk.Label(self.sales_tab, text=t("product_id")).grid(row=0, column=0, padx=5, pady=5)
        self.product_id_entry = ttk.Entry(self.sales_tab)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sales_tab, text=t("sale_quantity")).grid(row=1, column=0, padx=5, pady=5)
        self.sale_quantity_entry = ttk.Entry(self.sales_tab)
        self.sale_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.sales_tab, text=t("payment_method")).grid(row=2, column=0, padx=5, pady=5)
        self.payment_method_combobox = ttk.Combobox(self.sales_tab, values=["Cash", "Mobile Money", "Other"],
                                                    state="readonly")
        self.payment_method_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.payment_method_combobox.current(0)

        self.sell_button = ttk.Button(self.sales_tab, text=t("sell"), command=self.sell_product)
        self.sell_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.sales_tree = ttk.Treeview(self.sales_tab, columns=("ID", "Name", "Quantity", "Total", "Date", "Payment"),
                                       show="headings")
        self.sales_tree.heading("ID", text="Sale ID")
        self.sales_tree.heading("Name", text="Product Name")
        self.sales_tree.heading("Quantity", text=t("sale_quantity"))
        self.sales_tree.heading("Total", text="Total")
        self.sales_tree.heading("Date", text="Date/Time")
        self.sales_tree.heading("Payment", text=t("payment_method"))
        self.sales_tree.grid(row=4, column=0, columnspan=2, pady=5)

        self.refresh_sales_button = ttk.Button(self.sales_tab, text=t("refresh_sales"), command=self.load_sales)
        self.refresh_sales_button.grid(row=5, column=0, columnspan=2, pady=5)

        self.load_sales()

    def sell_product(self):
        try:
            product_id = int(self.product_id_entry.get())
            quantity = int(self.sale_quantity_entry.get())
            payment_method = self.payment_method_combobox.get()
            inventory = db_fetch_inventory()
            for item in inventory:
                if item[0] == product_id:
                    if item[2] >= quantity:
                        total = quantity * item[3]
                        db_save_sale(product_id, quantity, total, payment_method)
                        new_quantity = item[2] - quantity
                        db_update_product(product_id, item[1], new_quantity, item[3], item[4])
                        messagebox.showinfo(t("title"), t("sale_completed").replace("${total}", f"{total}"))
                        self.load_inventory()
                        self.load_sales()
                        self.update_dashboard()
                        return
                    else:
                        messagebox.showerror(t("title"), t("not_enough_inventory"))
                        return
            messagebox.showerror(t("title"), "Product not found!")
        except Exception as e:
            messagebox.showerror(t("title"), f"Error: {e}")

    def load_sales(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        for sale in db_fetch_recent_sales(limit=10):
            self.sales_tree.insert("", tk.END, values=sale)

    # ---------------------- Reports Tab ----------------------
    def setup_report_tab(self):
        ttk.Label(self.report_tab, text=t("start_date")).grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(self.report_tab)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.report_tab, text=t("end_date")).grid(row=1, column=0, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(self.report_tab)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.report_button = ttk.Button(self.report_tab, text=t("generate_report"), command=self.generate_report)
        self.report_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.report_tree = ttk.Treeview(self.report_tab, columns=("ID", "Name", "Quantity", "Total", "Date"),
                                        show="headings")
        self.report_tree.heading("ID", text="ID")
        self.report_tree.heading("Name", text="Product Name")
        self.report_tree.heading("Quantity", text=t("quantity"))
        self.report_tree.heading("Total", text="Total")
        self.report_tree.heading("Date", text="Date")
        self.report_tree.grid(row=3, column=0, columnspan=2, pady=5)

        # Buttons for charts, backup/restore, export
        self.sales_chart_button = ttk.Button(self.report_tab, text=t("sales_chart"), command=self.show_sales_chart)
        self.sales_chart_button.grid(row=4, column=0, columnspan=2, pady=5)
        self.inventory_chart_button = ttk.Button(self.report_tab, text=t("inventory_chart"),
                                                 command=self.show_inventory_chart)
        self.inventory_chart_button.grid(row=5, column=0, columnspan=2, pady=5)
        self.backup_button = ttk.Button(self.report_tab, text=t("backup"), command=self.backup_db)
        self.backup_button.grid(row=6, column=0, columnspan=2, pady=5)
        self.restore_button = ttk.Button(self.report_tab, text=t("restore"), command=self.restore_db)
        self.restore_button.grid(row=7, column=0, columnspan=2, pady=5)
        self.export_button = ttk.Button(self.report_tab, text=t("export_csv"), command=self.export_csv)
        self.export_button.grid(row=8, column=0, columnspan=2, pady=5)

    def generate_report(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        try:
            sales = db_fetch_sales_report(start_date, end_date)
            for row in self.report_tree.get_children():
                self.report_tree.delete(row)
            for sale in sales:
                self.report_tree.insert("", tk.END, values=sale)
        except Exception as e:
            messagebox.showerror(t("title"), f"Error generating report: {e}")

    def show_sales_chart(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        if not start_date or not end_date:
            messagebox.showerror(t("title"), "Please enter start and end dates.")
            return
        sales = db_fetch_sales_report(start_date, end_date)
        if not sales:
            messagebox.showinfo(t("title"), "No sales data found for this period.")
            return
        sales_by_date = {}
        for sale in sales:
            date_str = sale[4][:10]
            total = sale[3]
            sales_by_date[date_str] = sales_by_date.get(date_str, 0) + total
        dates = sorted(sales_by_date.keys())
        totals = [sales_by_date[d] for d in dates]
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Sales Chart")
        fig = plt.Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        ax.bar(dates, totals, color="blue")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Sales ($)")
        ax.set_title("Sales Over Time")
        for label in ax.get_xticklabels():
            label.set_rotation(45)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_inventory_chart(self):
        inventory = db_fetch_inventory()
        if not inventory:
            messagebox.showinfo(t("title"), "No inventory data found.")
            return
        product_names = [item[1] for item in inventory]
        quantities = [item[2] for item in inventory]
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Inventory Chart")
        fig = plt.Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        ax.bar(product_names, quantities, color="green")
        ax.set_xlabel("Product")
        ax.set_ylabel("Quantity")
        ax.set_title("Current Inventory Levels")
        for label in ax.get_xticklabels():
            label.set_rotation(45)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def backup_db(self):
        if backup_db():
            messagebox.showinfo(t("title"), t("backup_success"))
        else:
            messagebox.showerror(t("title"), "Backup failed.")

    def restore_db(self):
        if restore_db():
            messagebox.showinfo(t("title"), t("restore_success"))
            self.load_inventory()
            self.load_sales()
            self.update_dashboard()
        else:
            messagebox.showerror(t("title"), "Restore failed.")

    def export_csv(self):
        if export_inventory_to_csv() and export_sales_to_csv():
            messagebox.showinfo(t("title"), t("export_success"))
        else:
            messagebox.showerror(t("title"), "Export failed.")


# ---------------------- Main ----------------------
if __name__ == "__main__":
    initialize_db()
    # Start with the login window
    login_root = tk.Tk()
    LoginApp(login_root)
    login_root.mainloop()