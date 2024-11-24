from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask_bcrypt import Bcrypt
import datetime

app = Flask(__name__)
app.secret_key = 'password'
bcrypt = Bcrypt(app)

# Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', title="Home")

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
                    session['email'] = email
                    return redirect(url_for('account'))
                else:
                    error = "Invalid username or password"
        except sqlite3.Error as e:
            error = f"Database error: {e}"
    return render_template('customer-login.html', title="Customer Login", error=error)

@app.route('/admin-login')
def admin_login():
    return render_template('admin-login.html', title="Admin Login")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    success = None
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                cur.execute("SELECT email FROM users WHERE email = ?", (email,))
                data = cur.fetchone()
                if data:
                    #send email with password reset link
                    success = "Password reset link sent to your email"
                else:
                    error = "Email not found"
        except sqlite3.Error as e:
            error = f"Database error: {e}"
    return render_template('forgot-password.html', title="Forgot Password", error=error, success=success)

@app.route('/events', methods=['GET', 'POST'])
def events():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        event = request.form.get('event')
        form_id = request.form.get('form_id')
        if form_id == 'booking-form':
            try:
                with sqlite3.connect("dojo.db") as con:
                    quote = "SELECT id FROM users WHERE email = ?"
                    cur = con.cursor()
                    cur.execute(quote, (email,))
                    email = cur.fetchone()
                    if email:
                        quote = "INSERT INTO bookings (userID, eventID, booking_date) VALUES (?, ?, ?)"
                        if event == 'event1':
                            eventID = 1
                        elif event == 'event2':
                            eventID = 2
                        elif event == 'event3':
                            eventID = 3
                        else:
                            eventID = 4
                        eventTime = datetime.datetime.now()
                        eventTime = eventTime.strftime("%Y-%m-%d %H:%M:%S")
                        data = (email[0], eventID, eventTime)
                        cur.execute(quote, data)
                        con.commit()
                        con.close()
                        return render_template('events.html', title="Events")
                    else:
                        error = "User not found"
            except sqlite3.Error as e:
                error = f"Database error: {e}"
        elif form_id == 'waiting-list-form':
            #put main code here
            pass
    return render_template('events.html', title="Events", error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        address = request.form.get('address')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        current_time = datetime.datetime.now()
        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, email, password, firstName, lastName, phoneNumber, address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (username, email, hashed_password, firstname, lastname, phone, address, current_time))
                con.commit()
                session['email'] = email
                return redirect(url_for('account'))
        except sqlite3.Error as e:
            error = f"Database error: {e}"
    return render_template('register.html', title="Register", error=error)

@app.errorhandler(404)
def error_404(_):   
    return render_template('404.html', title="404")

@app.route('/account')
def account():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']

    with sqlite3.connect("dojo.db") as con:
        cur = con.cursor()
        cur.execute("SELECT firstName, lastName, phoneNumber, address FROM users WHERE email = ?", (email,))
        data = cur.fetchone()

    if data:
        user_data = {
            'firstName': data[0],
            'lastName': data[1],
            'phoneNumber': data[2],
            'address': data[3]
        }
        return render_template('account.html', title="Account", email=email, user_data=user_data)
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
