from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_bcrypt import Bcrypt
import datetime
import random
import string

app = Flask(__name__)
app.secret_key = 'password'
bcrypt = Bcrypt(app)

@app.context_processor
def inject_username():
    return dict(email=session.get('email'))

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
                cur.execute("SELECT password, role FROM users WHERE email = ?", (email,))
                data = cur.fetchone()
                if data and bcrypt.check_password_hash(data[0], password):
                    session['email'] = email  # Set the session variable
                    session['role'] = data[1]  # Set the role for the session
                    print(f"User  {email} logged in successfully.")  # Debug statement
                    return redirect(url_for('account'))  # Redirect to account page
                else:
                    error = "Invalid username or password"
        except sqlite3.Error as e:
            error = f"Database error: {e}"
    return render_template('customer-login.html', title="Customer Login", error=error)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                cur.execute("SELECT password, role FROM users WHERE email = ?", (email,))
                data = cur.fetchone()

                if data:
                    hashed_password, role = data
                    # Check the password
                    if data[1] != 'admin':
                        error = "Not an admin account"
                    elif bcrypt.check_password_hash(hashed_password, password) and role == 'admin':
                        session['email'] = email  # Set the session variable
                        session['role'] = role  # Set the role for the session
                        return redirect(url_for('admin_panel'))  
                    else:
                        error = "Invalid email or password"
                else:
                    error = "Invalid email or password"
        except sqlite3.Error as e:
            error = f"Database error: {e}"

    return render_template('admin-login.html', title="Admin Login", error=error)

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    
    error = None
    success = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_event':
            event_name = request.form.get('event_name')
            event_description = request.form.get('event_description')
            event_date = request.form.get('event_date')
            try:
                with sqlite3.connect("dojo.db") as con:
                    classID = ''.join(random.sample(string.ascii_letters, 15)) # Automatically generate a classID made of text
                    cur = con.cursor()
                    cur.execute("SELECT * FROM events WHERE classID = ?", (classID,)) # Check if classID already exists
                    while cur.fetchone():
                        classID = ''.join(random.sample(string.ascii_letters, 15)) # Automatically generate a classID made of text
                        cur.execute("SELECT * FROM events WHERE classID = ?", (classID,)) # Check if classID already exists
                    cur.execute("INSERT INTO events (name, description, date, classID) VALUES (?, ?, ?, ?)", (event_name, event_description, event_date, classID))
                    con.commit()
                    success = "Event added successfully!"
            except sqlite3.Error as e:
                error = f"Database error: {e}"
        elif action == 'remove_event':
            event_id = int(request.form.get('event_id'))
            try:
                with sqlite3.connect("dojo.db") as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM events WHERE eventID = ?", (event_id,))
                    con.commit()
                    success = "Event removed successfully!"
            except sqlite3.Error as e:
                error = f"Database error: {e}"

    # Fetch all events to display
    with sqlite3.connect("dojo.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM events")
        events = cur.fetchall()

    return render_template('admin-panel.html', title="Admin Panel", events=events, error=error, success=success)

#@app.route('/admin-dashboard')
#def admin_dashboard():
#    if 'email' not in session or session.get('role') != 'admin':
#        return redirect(url_for('admin_login'))  # Redirect to admin login if not logged in as admin
#    return render_template('admin-dashboard.html', title="Admin Dashboard")  # Render the admin dashboard page

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

@app.route('/cancel-booking', methods=['POST'])
def cancel_booking():
    error = None
    user_bookings = []  # Initialize user_bookings
    if 'email' not in session:
        error = "You must be logged in to cancel a booking."
    else:
        email = session['email']
        eventID = int(request.form.get('cancel-event'))
        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                cur.execute("""
                    DELETE FROM bookings 
                    WHERE eventID = ? AND userID = (SELECT userID FROM users WHERE email = ?)
                """, (eventID, email))
                con.commit()
                
                # Fetch updated user bookings
                cur.execute("""
                    SELECT e.name, e.date, b.booking_date, e.description, e.classID, e.eventID 
                    FROM bookings b 
                    JOIN events e ON b.eventID = e.eventID 
                    WHERE b.userID = (SELECT userID FROM users WHERE email = ?)
                """, (email,))
                user_bookings = cur.fetchall()
                flash('Your booking has been canceled successfully!', 'success')  # Flash success message
                return redirect(url_for('events'))  # Redirect to events page after cancellation
        except sqlite3.Error as e:
            error = f"Database error: {e}"

    return render_template('events.html', title="Events", user_bookings=user_bookings, error=error)

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

@app.route('/admin-register', methods=['GET', 'POST'])
def admin_register():
    error = None
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Hash the password for security
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        role = 'admin'  # Set role for admin

        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                
                # Check if the email already exists
                cur.execute("SELECT email FROM users WHERE email = ?", (email,))
                existing_email = cur.fetchone()
                
                if existing_email:
                    error = "Email address already exists. Please use a different email."
                else:
                    cur.execute("INSERT INTO users (username, email, password, firstName, lastName, phoneNumber, address, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (username, email, hashed_password, firstname, lastname, phone, address, role))
                    con.commit()
                    return redirect(url_for('admin_panel'))  # Redirect to admin panel after successful registration
        except sqlite3.Error as e:
            error = f"Database error: {e}"

    return render_template('admin-register.html', title="Admin Register", error=error)

@app.errorhandler(404)
def error_404(error):   
    return render_template('404.html', title="404")

@app.route('/account')
def account():
    if 'email' not in session:
        print("User  not logged in, redirecting to login.")  # Debug statement
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    email = session['email']
    print(f"Fetching account data for {email}.")  # Debug statement

    with sqlite3.connect("dojo.db") as con:
        cur = con.cursor()
        cur.execute("SELECT firstName, lastName, phoneNumber, address, role FROM users WHERE email = ?", (email,))
        data = cur.fetchone()

    if data:
        user_data = {
            'firstName': data[0],
            'lastName': data[1],
            'phoneNumber': data[2],
            'address': data[3],
            'role': data[4]
        }
        return render_template('account.html', title="Account", email=email, user_data=user_data)
    else:
        print("User  data not found, redirecting to home.")  # Debug statement
        return redirect(url_for('home'))  # Redirect to home if user data is not found

@app.route('/events', methods=['GET', 'POST'])
def events():
    user_bookings = []  # Initialize user_bookings
    error = None  # Initialize error variable

    if request.method == 'POST':
        # Handle booking logic here
        eventID = int(request.form.get('eventID'))
        email = session.get('email')

        if email:
            try:
                with sqlite3.connect("dojo.db") as con:
                    cur = con.cursor()
                    cur.execute("""
                        INSERT INTO bookings (eventID, userID, booking_date) 
                        VALUES (?, (SELECT userID FROM users WHERE email = ?), ?)
                    """, (eventID, email, datetime.datetime.now()))
                    con.commit()
                    flash('Your booking has been made successfully!', 'success')  # Flash success message
            except sqlite3.Error as e:
                error = f"Database error: {e}"
        else:
            flash('You must be logged in to book an event.', 'error')

    # Fetch upcoming events from the database
    with sqlite3.connect("dojo.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM events")
        events = cur.fetchall()

    # Fetch user bookings for display
    if 'email' in session:
        email = session['email']
        try:
            with sqlite3.connect("dojo.db") as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT e.name, e.date, b.booking_date, e.description, e.classID, e.eventID 
                    FROM bookings b 
                    JOIN events e ON b.eventID = e.eventID 
                    WHERE b.userID = (SELECT userID FROM users WHERE email = ?)
                """, (email,))
                user_bookings = cur.fetchall()
        except sqlite3.Error as e:
            error = f"Database error: {e}"

    return render_template('events.html', title="Events", events=events, user_bookings=user_bookings, error=error)

@app.route('/send-message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Save the message to the database
    try:
        with sqlite3.connect("dojo.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
                        (name, email, subject, message))
            con.commit()  # Commit the transaction
        flash('Your message has been sent successfully!', 'success')  # Set success message
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('There was an error sending your message. Please try again.', 'error')  # Set error message

    # Redirect to the contact page
    return redirect(url_for('contact'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('admin', None)
    session['role'] = None
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
