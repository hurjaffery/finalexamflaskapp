from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import logging

app = Flask(__name__)

# Set the secret key to enable session management
app.config['SECRET_KEY'] = 'ilovePakistan'  # Replace with a secure key for production

# Configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

# Configure Flask-Talisman for security headers
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"]
}
Talisman(
    app,
    content_security_policy=csp,
    strict_transport_security=True,  # Enable HSTS
    strict_transport_security_preload=True,
    strict_transport_security_max_age=31536000,  # 1 year
    frame_options="DENY"  # X-Frame-Options
)

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger()

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    website = db.Column(db.String(120))
    message = db.Column(db.Text, nullable=False)

# Default route redirects to /login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            logger.info(f"Successful login for user: {username}")
            return redirect(url_for('contact'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('User already exists. Choose a different username.', 'warning')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"New user registered: {username}")
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Contact form submission
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        website = request.form['website']
        message = request.form['message']

        new_contact = Contact(name=name, email=email, phone=phone, website=website, message=message)
        db.session.add(new_contact)
        db.session.commit()
        logger.info(f"New contact message from: {email}")
        flash('Thank you! We have received your message.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
