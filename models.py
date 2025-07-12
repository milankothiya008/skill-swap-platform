from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    skills_offered = db.Column(db.String(200), nullable=False)
    skills_wanted = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    photo_filename = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.String(50), default='Flexible')