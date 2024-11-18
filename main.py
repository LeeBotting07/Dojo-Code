from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'password'
bcrypt = Bcrypt(app)

# Routes
@app.route('/')
def home():
    return render_template('main.html', title="Home")

@app.route('/products')
def products():
    return render_template('products.html', title="Products")

@app.route('/about')
def about():
    return render_template('about.html', title="About Us")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title="Login")

@app.route('/customer-login', methods=['GET', 'POST'])
def customer_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                cur.execute("SELECT password FROM users WHERE email = ?", (email,))
                data = cur.fetchone()
                if data and bcrypt.check_password_hash(data[0], password):
                    print("Logged in")
                    return redirect(url_for('home'))
                else:
                    error = "Invalid username or password"
        except sqlite3.Error as e:
            error = f"Database error: {e}"
    return render_template('customer-login.html', title="Customer Login", error=error)

@app.route('/admin-login')
def admin_login():
    return render_template('admin-login.html', title="Admin Login")

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html', title="Forgot Password")

@app.route('/events')
def events():
    return render_template('events.html', title="Events")

if __name__ == '__main__':
    app.run(debug=True)
