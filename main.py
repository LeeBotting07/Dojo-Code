from flask import Flask, render_template
 
app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('main.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/about_us')
def about():
    return render_template('about.html')

@app.route('/contact_us')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
