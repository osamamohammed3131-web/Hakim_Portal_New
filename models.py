from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='student') # superadmin, admin, student
    plan_type = db.Column(db.String(10), default='A') # 'A' أو 'B'

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    plan_type = db.Column(db.String(10), nullable=False) # 'A' أو 'B'
    description = db.Column(db.Text, nullable=True)
    lectures = db.relationship('Lecture', backref='material', lazy=True)

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    content_summary = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(300), nullable=True)

class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

class SmartScheduleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    day_of_week = db.Column(db.String(50), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='قادمة') # قادمة، بدأت، مكتملة، فائتة
