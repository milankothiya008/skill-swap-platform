from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os

# Initialize app
app = Flask(__name__)
app.secret_key = 'super_secret_123'  # Change in production

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Change this
app.config['MAIL_PASSWORD'] = 'your_app_password'    # Change this (use app password)
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'
mail = Mail(app)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:peVthhPDvnNYcKvDuuatisHZIdPyxBWr@shuttle.proxy.rlwy.net:36844/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    skills_offered = db.Column(db.String(200), nullable=False)
    skills_wanted = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    photo_filename = db.Column(db.String(120), nullable=True)

# Request model
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_requested = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    requester = db.relationship('User', foreign_keys=[requester_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])

# Home route
@app.route('/')
def home():
    query = request.args.get('q', '')
    availability = request.args.get('availability', '')

    users = User.query

    if query:
        users = users.filter(User.skills_offered.like(f'%{query}%'))

    return render_template('home.html', users=users.all())

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        skills_offered = request.form['skills_offered']
        skills_wanted = request.form['skills_wanted']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Try logging in.', 'error')
            return redirect(url_for('signup'))

        # Handle file upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{email.split('@')[0]}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                photo_filename = unique_filename

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            email=email,
            password=hashed_pw,
            name=name,
            skills_offered=skills_offered,
            skills_wanted=skills_wanted,
            photo_filename=photo_filename
        )
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash('Signup successful!', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Profile route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    # Get pending requests
    pending_requests = Request.query.filter_by(recipient_id=user.id, status='pending').all()
    return render_template('profile.html', user=user, pending_requests=pending_requests)

# Request skill route
@app.route('/request/<int:user_id>', methods=['GET', 'POST'])
def request_skill(user_id):
    if 'user_id' not in session:
        flash('Please login to send requests', 'error')
        return redirect(url_for('login'))
    
    recipient = User.query.get_or_404(user_id)
    requester = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        skill_requested = request.form['skill_requested']
        message = request.form.get('message', '')
        
        # Create new request
        new_request = Request(
            requester_id=requester.id,
            recipient_id=recipient.id,
            skill_requested=skill_requested,
            message=message
        )
        db.session.add(new_request)
        db.session.commit()
        
        # Send email
        try:
            msg = Message(
                subject=f"New Skill Swap Request for {skill_requested}",
                recipients=[recipient.email],
                body=f"""Hello {recipient.name},

{requester.name} has requested to swap skills with you for: {skill_requested}

Message: {message}

Please login to your account to respond to this request.

Best regards,
Skill Swap Team
"""
            )
            mail.send(msg)
            flash('Request sent successfully!', 'success')
        except Exception as e:
            print(f"Error sending email: {e}")
            flash('Request saved but email could not be sent', 'warning')
        
        return redirect(url_for('home'))
    
    return render_template('request.html', recipient=recipient)

# Handle request response
@app.route('/request/<int:request_id>/<action>')
def handle_request(request_id, action):
    if 'user_id' not in session:
        flash('Please login to manage requests', 'error')
        return redirect(url_for('login'))
    
    req = Request.query.get_or_404(request_id)
    
    if req.recipient_id != session['user_id']:
        flash('Unauthorized action', 'error')
        return redirect(url_for('home'))
    
    if action == 'accept':
        req.status = 'accepted'
        # Send acceptance email
        try:
            msg = Message(
                subject=f"Your skill swap request was accepted!",
                recipients=[req.requester.email],
                body=f"""Hello {req.requester.name},

{req.recipient.name} has accepted your skill swap request for: {req.skill_requested}

You can now contact them at: {req.recipient.email}

Happy skill swapping!

Best regards,
Skill Swap Team
"""
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending acceptance email: {e}")
    elif action == 'reject':
        req.status = 'rejected'
    
    db.session.commit()
    flash(f"Request {action}ed!", 'success')
    return redirect(url_for('profile'))

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have logged out.', 'info')
    return redirect(url_for('home'))

# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)