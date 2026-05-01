import sqlite3
from sqlite3 import Error
from datetime import date
import hashlib

# Initialize Database Connection
def CreateConnection():
    conn = None
    try:
        conn = sqlite3.connect("GroceryStore.db")
        return conn
    except Error as e:
        print(f"Database Connection Error: {e}")
    return conn

# Build the Database
def BuildDatabase(conn):
    tables = [
        """CREATE TABLE IF NOT EXISTS Categories (
            CategoryID INTEGER PRIMARY KEY,
            CategoryName VARCHAR (50) NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INTEGER PRIMARY KEY,
            SupplierName VARCHAR (50) NOT NULL,
            Phone VARCHAR (15)
        );""",
        """CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY,
            SKU VARCHAR (30) UNIQUE NOT NULL,
            ProductName VARCHAR (50) NOT NULL,
            Price DECIMAL (8,2) NOT NULL,
            StockQuantity INTEGER NOT NULL,
            CategoryID INTEGER,
            SupplierID INTEGER,
            FOREIGN KEY (CategoryID) REFERENCES Categories (CategoryID),
            FOREIGN KEY (SupplierID) REFERENCES Suppliers (SupplierID)
        );""",
        """CREATE TABLE IF NOT EXISTS Customers (
            CustomerID INTEGER PRIMARY KEY,
            FirstName VARCHAR (30) NOT NULL,
            LastName VARCHAR (30) NOT NULL,
            Phone VARCHAR (15),
            PasswordHash VARCHAR (100) NOT NULL,
            IsAdmin BOOLEAN NOT NULL CHECK (IsAdmin IN (0, 1))
        );""",
        """CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY,
            CustomerID INTEGER,
            OrderDate DATE NOT NULL,
            TotalAmount DECIMAL (8,2) NOT NULL,
            FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
        );""",
        """CREATE TABLE IF NOT EXISTS OrderItems (
            OrderItemID INTEGER PRIMARY KEY,
            OrderID INTEGER,
            ProductID INTEGER,
            Quantity INTEGER NOT NULL,
            ItemPrice DECIMAL (7,2) NOT NULL,
            FOREIGN KEY (OrderID) REFERENCES Orders (OrderID),
            FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
        );"""
    ]

    try:
        c = conn.cursor()
        for table in tables:
            c.execute(table)
        conn.commit()
        print("Database successfully built.")
    except Error as e:
        print(f"Error building database: {e}")

# Insert some initial data into the database
def InitialData(conn):
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM Categories")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO Categories (CategoryName) VALUES 
            ('Produce'), ('Dairy & Eggs'), ('Bakery'), 
            ('Meat & Seafood'), ('Pantry & Dry Goods'), ('Beverages')""")
        
        c.execute("""INSERT INTO Suppliers (SupplierName, Phone) VALUES 
            ('Local Farms', '432-562-7654'), ('Dairy Co', '734-474-2356'), 
            ('Daily Bread Bakery', '251-474-2828'), ('Prime Cuts Meat', '117-745-6327'), 
            ('Global Goods Dist.', '760-954-2167'), ('Liquid Assets Bev.', '891-237-568')""")
        
        c.execute("""INSERT INTO Products (SKU, ProductName, Price, StockQuantity, CategoryID, SupplierID) VALUES 
            ('PRD-APP-01', 'Fuji Apples (1lb)', 1.99, 100, 1, 1),
            ('PRD-BAN-01', 'Organic Bananas (1lb)', 0.69, 150, 1, 1),
            ('DRY-MLK-01', 'Whole Milk (1 Gallon)', 3.49, 50, 2, 2),
            ('DRY-EGG-01', 'Large Brown Eggs (Dozen)', 4.99, 40, 2, 2),
            ('BKY-BRD-01', 'Sourdough Loaf', 5.99, 20, 3, 3),
            ('BKY-MFF-01', 'Blueberry Muffins (4-pack)', 6.49, 15, 3, 3),
            ('MEA-CHK-01', 'Chicken Breasts (1lb)', 6.49, 30, 4, 4),
            ('MEA-BEE-01', 'Ground Beef 80/20 (1lb)', 5.49, 35, 4, 4),
            ('PAN-PAS-01', 'Spaghetti (16oz)', 1.29, 200, 5, 5),
            ('PAN-RIC-01', 'Jasmine Rice (2lbs)', 3.99, 80, 5, 5),
            ('BEV-WAT-01', 'Spring Water (24 pk)', 4.99, 100, 6, 6),
            ('BEV-CFF-01', 'Cold Brew Coffee (32oz)', 5.99, 45, 6, 6)""")

    c.execute("SELECT COUNT(*) FROM Customers")
    if c.fetchone()[0] == 0:
        adminPW = hashlib.sha256("admin1337".encode()).hexdigest()
        c.execute("INSERT INTO Customers (FirstName, LastName, Phone, PasswordHash, IsAdmin) VALUES ('John', 'Doe', '897-516-9503', ?, 1)", (adminPW,))
        
        custPW = hashlib.sha256("shopper1738".encode()).hexdigest()
        c.execute("INSERT INTO Customers (FirstName, LastName, Phone, PasswordHash, IsAdmin) VALUES ('Jane', 'Doe', '973-377-0514', ?, 0)", (custPW,))
        
        c.execute("""INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES 
            (2, '2026-04-28', 12.47),
            (1, '2026-04-29', 24.96),
            (2, '2026-05-01', 9.98)""")
            
        c.execute("""INSERT INTO OrderItems (OrderID, ProductID, Quantity, ItemPrice) VALUES 
            (1, 3, 2, 3.49),  
            (1, 8, 1, 5.49),  
            (2, 7, 2, 6.49),  
            (2, 5, 2, 5.99),  
            (3, 11, 2, 4.99)""")

    conn.commit()

def AuthUser(conn):
    print("----- Grocery Store Login -----")
    first = input("First Name: ").strip()
    last = input("Last Name: ").strip()
    pw = input("Password: ").strip()
    hashPW = hashlib.sha256(pw.encode()).hexdigest()

    try:
        c = conn.cursor()
        c.execute(" SELECT CustomerID, IsAdmin FROM Customers WHERE FirstName = ? AND LastName = ? AND PasswordHash = ?", (first, last, hashPW))
        user = c.fetchone()

        if user:
            print(f"\nAuthentication Success! Welcome Back, {first}!")
            return {"id": user[0], "isAdmin": user[1], "name": first}
        else:
            print("\nError: Invalid credentials. Please try again.")
            return None
    except Error as e:
        print(f"Database Error during login: {e}")
        return None

# Add a product
def AddProduct(conn):
    try:
        sku = input("Enter SKU: ")
        name = input("Enter Product Name: ")
        price = float(input("Enter Price: "))
        stock = int(input("Enter Initial Stock: "))
        catID = int(input("Enter Category ID [1 - Produce, 2 - Dairy, 3 - Bakery]: "))
        supID = int(input("Enter Supplier ID [1 - Local Farms, 2 - Dairy Co]: "))

        code = '''INSERT INTO Products (SKU, ProductName, Price, StockQuantity, CategoryID, SupplierID) VALUES (?, ?, ?, ?, ?, ?)'''
        c = conn.cursor()
        c.execute(code, (sku, name,  price, stock, catID, supID))
        conn.commit()
        print(f"\nSuccess! Product '{name}' added!")
    except ValueError:
        print("\nError: Invalid number format entered.")
    except Error as e:
        print(f"Database Error: {e}")

# View all products
def ViewProducts(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT ProductID, SKU, ProductName, Price, StockQuantity FROM Products")
        rows = c.fetchall()
        print("\n--- Inventory ---")
        if not rows:
            print("No products in inventory.")
        for row in rows:
            print(f"ID: {row[0]} | SKU: {row[1]} | Name: {row[2]} | Price: ${row[3]:.2f} | Stock: {row[4]}")
    except Error as e:
        print(f"Error reading products: {e}")

# Udpate product stock
def UpdateStock(conn):
    try:
        ViewProducts(conn)
        prodID = int(input("\nEnter the Product ID to update: "))
        NewStock = int(input("Enter the new stock quantity: "))
        
        code = '''UPDATE Products SET StockQuantity = ? WHERE ProductID = ?'''
        c = conn.cursor()
        c.execute(code, (NewStock, prodID))
        conn.commit()
        print(f"\nSuccess! Stock updated.")
    except ValueError:
        print("\nError: Please enter valid numbers.")
    except Error as e:
        print(f"\nDatabase Error: {e}")

# Place an order
def PlaceOrder(conn, user):
    try:
        cust = user['id']
        orderDate = date.today().strftime("%Y-%m-%d")
        
        print("\n--- Start Adding Items to Order ---")
        ViewProducts(conn)
        
        items = []
        total = 0.0
        
        while True:
            prodID = int(input("\nEnter Product ID to buy (or 0 to finish): "))
            if prodID == 0:
                break
                
            qty = int(input("Enter quantity: "))
            
            c = conn.cursor()
            c.execute("SELECT Price, ProductName, StockQuantity FROM Products WHERE ProductID = ?", (prodID,))
            product = c.fetchone()
            
            if product:
                price = product[0]
                name = product[1]
                stock = product[2]
                
                if qty > stock:
                    print(f"Not enough stock for {name}. Only {stock} available.")
                    continue
                
                items.append((prodID, qty, price))
                total += (price * qty)
                print(f"Added {qty}x {name} to order.")
            else:
                print("Invalid Product ID.")

        if not items:
            print("Order cancelled - no items added.")
            return

        c = conn.cursor()
        c.execute("INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES(?,?,?)", (cust, orderDate, total))
        orderID = c.lastrowid
        
        for item in items:
            c.execute("INSERT INTO OrderItems (OrderID, ProductID, Quantity, ItemPrice) VALUES(?,?,?,?)",
                        (orderID, item[0], item[1], item[2]))
            
            c.execute("UPDATE Products SET StockQuantity = StockQuantity - ? WHERE ProductID = ?",
                        (item[1], item[0]))
            
        conn.commit()
        print(f"\nSuccess! Order #{orderID} placed successfully! Total: ${total:.2f}")

    except ValueError:
        print("\nError: Please enter valid numbers.")
    except Error as e:
        print(f"\nDatabase Error: {e}")

# View orders
def ViewOrders(conn, user):
    try:
        c = conn.cursor()
        if user['isAdmin'] == 1:
            c.execute("SELECT OrderID, CustomerID, OrderDate, TotalAmount FROM Orders")
            print("\n--- All Store Orders (Admin View) ---")
        else:
            c.execute("SELECT OrderID, CustomerID, OrderDate, TotalAmount FROM Orders WHERE CustomerID = ?", (user['id'],))
            print("\n--- My Order History ---")

        rows = c.fetchall()
        if not rows:
            print("No orders have been placed yet.")
        for row in rows:
            print(f"Order #{row[0]} | Date: {row[2]} | Customer ID: {row[1]} | Total: ${row[3]:.2f}")
    except Error as e:
        print(f"Error reading orders: {e}")

# Main menu
def MainMenu(user):
    role = "Admin" if user['isAdmin'] else "Shopper"
    print(f"\n----- Grocery Database | Logged in as: {user['name']} ({role}) -----")
    
    print("1. View Inventory")
    
    if user['isAdmin'] == 1:
        print("2. Add New Product")
        print("3. Update Product Stock")
        
    print("4. Place a New Order")
    
    if user['isAdmin'] == 1:
        print("5. View All Orders")
    else:
        print("5. View My Orders")
        
    print("0. Log Out / Exit")

# Run everything
def run():
    conn = CreateConnection()
    if conn:
        BuildDatabase(conn)
        InitialData(conn)

        user = None
        while user is None:
            user = AuthUser(conn)
            if not user:
                retry = input("Press Enter to try again or type '0' to exit: ")
                if retry == '0':
                    print("Exiting...")
                    return

        while True:
            MainMenu(user)
            choice = input("Select an option (0-5): ")
            
            if choice == '1':
                ViewProducts(conn)
            elif choice == '2' and user['isAdmin'] == 1:
                AddProduct(conn)
            elif choice == '3' and user['isAdmin'] == 1:
                UpdateStock(conn)
            elif choice == '4':
                PlaceOrder(conn, user)
            elif choice == '5':
                ViewOrders(conn, user)
            elif choice == '0':
                print("\nSaving database and exiting... Goodbye!")
                conn.close()
                break
            else:
                print("\nInvalid choice or unauthorized action. Please try again.")
    else:
        print("Could not start application due to database connection failure.")

# hello
run()