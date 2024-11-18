from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_is_a_very_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database connection
connection = sqlite3.connect('dojo.db', check_same_thread=False)

# Create users table with primary key for unique identification
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
""")
cursor.close()

# Flask-Login user loader
class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], name=user[1], email=user[2], password=user[3])
    return None

# Home route
@app.route('/')
@app.route('/home')
def home():
    return render_template('main.html')

# Products route
@app.route('/products')
def products():
    return render_template('products.html')

# About Us route
@app.route('/about_us')
def about():
    return render_template('about.html')

# Contact Us route
@app.route('/contact_us')
def contact():
    return render_template('contact.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('login.html')

# Customer Login route
@app.route('/customer-login')
def customer_login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[3], password):
            login_user(User(id=user[0], name=user[1], email=user[2], password=user[3]))
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')


    return render_template('customer-login.html')

# Admin Login route
@app.route('/admin-login')
def admin_login():
    return render_template('admin-login.html')

# Forgot Password route
@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
            connection.commit()
            cursor.close()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email.')
        
    return render_template('register.html')

# Events route
@app.route('/events')
def events():
    return render_template('events.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Error handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
