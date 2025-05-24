from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

if not os.path.exists('database'):
    os.makedirs('database')

def init_db():
    conn = sqlite3.connect('database/insurance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            dob DATE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Policies (
            policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT,
            type TEXT,
            coverage_amount REAL,
            premium REAL,
            duration INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            policy_id INTEGER,
            purchase_date DATE,
            premium_due_date DATE,
            FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
            FOREIGN KEY(policy_id) REFERENCES Policies(policy_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER,
            payment_date DATE,
            amount_paid REAL,
            FOREIGN KEY(purchase_id) REFERENCES Purchases(purchase_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER,
            claim_date DATE,
            claim_amount REAL,
            status TEXT,
            FOREIGN KEY(purchase_id) REFERENCES Purchases(purchase_id)
        )
    ''')

    c.execute("INSERT OR IGNORE INTO Customers (customer_id, name, email, phone, address, dob) VALUES (1, 'Jane Doe', 'jane@example.com', '8888888888', 'Mumbai', '1995-05-20')")
    c.execute("INSERT OR IGNORE INTO Policies (policy_id, policy_name, type, coverage_amount, premium, duration) VALUES (1, 'Health Plus', 'Health', 500000, 1500, 12)")
    c.execute("INSERT OR IGNORE INTO Purchases (purchase_id, customer_id, policy_id, purchase_date, premium_due_date) VALUES (1, 1, 1, DATE('now'), DATE('now', '+30 days'))")
    c.execute("INSERT OR IGNORE INTO Payments (payment_id, purchase_id, payment_date, amount_paid) VALUES (1, 1, DATE('now'), 1500)")
    c.execute("INSERT OR IGNORE INTO Claims (claim_id, purchase_id, claim_date, claim_amount, status) VALUES (1, 1, DATE('now'), 25000, 'Approved')")

    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('database/insurance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    customer_count = conn.execute('SELECT COUNT(*) FROM Customers').fetchone()[0]
    policy_count = conn.execute('SELECT COUNT(*) FROM Policies').fetchone()[0]
    purchase_count = conn.execute('SELECT COUNT(*) FROM Purchases').fetchone()[0]
    claim_count = conn.execute('SELECT COUNT(*) FROM Claims').fetchone()[0]
    conn.close()
    return render_template('index.html', customers=customer_count, policies=policy_count,
                           purchases=purchase_count, claims=claim_count)

@app.route('/customers')
def view_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM Customers').fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

@app.route('/add-customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob']

        conn = get_db_connection()
        conn.execute('INSERT INTO Customers (name, email, phone, address, dob) VALUES (?, ?, ?, ?, ?)',
                     (name, email, phone, address, dob))
        conn.commit()
        conn.close()
        return redirect('/customers')
        
    return render_template('add_customer.html')

@app.route('/policies')
def view_policies():
    conn = get_db_connection()
    policies = conn.execute('SELECT * FROM Policies').fetchall()
    conn.close()
    return render_template('policies.html', policies=policies)

@app.route('/add-policy', methods=['GET', 'POST'])
def add_policy():
    if request.method == 'POST':
        policy_name = request.form['policy_name']
        type = request.form['type']
        coverage = request.form['coverage']
        premium = request.form['premium']
        duration = request.form['duration']

        conn = get_db_connection()
        conn.execute('INSERT INTO Policies (policy_name, type, coverage_amount, premium, duration) VALUES (?, ?, ?, ?, ?)',
                     (policy_name, type, coverage, premium, duration))
        conn.commit()
        conn.close()
        return redirect('/policies')
    
    return render_template('add_policy.html')


@app.route('/purchases')
def view_purchases():
    conn = get_db_connection()
    purchases = conn.execute('SELECT * FROM Purchases').fetchall()
    conn.close()
    return render_template('purchases.html', purchases=purchases)

@app.route('/add-purchase', methods=['GET', 'POST'])
def add_purchase():
    conn = get_db_connection()
    customers = conn.execute('SELECT customer_id, name FROM Customers').fetchall()
    policies = conn.execute('SELECT policy_id, policy_name FROM Policies').fetchall()
    
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        policy_id = request.form['policy_id']
        purchase_date = request.form['purchase_date']
        due_date = request.form['premium_due_date']

        conn.execute('INSERT INTO Purchases (customer_id, policy_id, purchase_date, premium_due_date) VALUES (?, ?, ?, ?)',
                     (customer_id, policy_id, purchase_date, due_date))
        conn.commit()
        conn.close()
        return redirect('/purchases')
    
    return render_template('add_purchase.html', customers=customers, policies=policies)


@app.route('/payments')
def view_payments():
    conn = get_db_connection()
    payments = conn.execute('SELECT * FROM Payments').fetchall()
    conn.close()
    return render_template('payments.html', payments=payments)

@app.route('/add-payment', methods=['GET', 'POST'])
def add_payment():
    conn = get_db_connection()
    purchases = conn.execute('''
        SELECT Purchases.purchase_id, Customers.name || ' - ' || Policies.policy_name AS info
        FROM Purchases
        JOIN Customers ON Purchases.customer_id = Customers.customer_id
        JOIN Policies ON Purchases.policy_id = Policies.policy_id
    ''').fetchall()

    if request.method == 'POST':
        purchase_id = request.form['purchase_id']
        payment_date = request.form['payment_date']
        amount_paid = request.form['amount_paid']

        conn.execute('INSERT INTO Payments (purchase_id, payment_date, amount_paid) VALUES (?, ?, ?)',
                     (purchase_id, payment_date, amount_paid))
        conn.commit()
        conn.close()
        return redirect('/payments')
    
    return render_template('add_payment.html', purchases=purchases)


@app.route('/claims')
def view_claims():
    conn = get_db_connection()
    claims = conn.execute('SELECT * FROM Claims').fetchall()
    conn.close()
    return render_template('claims.html', claims=claims)

@app.route('/add-claim', methods=['GET', 'POST'])
def add_claim():
    conn = get_db_connection()
    purchases = conn.execute('''
        SELECT Purchases.purchase_id, Customers.name || ' - ' || Policies.policy_name AS info
        FROM Purchases
        JOIN Customers ON Purchases.customer_id = Customers.customer_id
        JOIN Policies ON Purchases.policy_id = Policies.policy_id
    ''').fetchall()

    if request.method == 'POST':
        purchase_id = request.form['purchase_id']
        claim_date = request.form['claim_date']
        claim_amount = request.form['claim_amount']
        status = request.form['status']

        conn.execute('INSERT INTO Claims (purchase_id, claim_date, claim_amount, status) VALUES (?, ?, ?, ?)',
                     (purchase_id, claim_date, claim_amount, status))
        conn.commit()
        conn.close()
        return redirect('/claims')
    
    return render_template('add_claim.html', purchases=purchases)


if __name__ == '__main__':
    app.run(debug=True)
