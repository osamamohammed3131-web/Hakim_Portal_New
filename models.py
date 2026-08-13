from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='student') # superadmin, admin, instructor, student
    is_admin = db.Column(db.Boolean, default=False)
    plan_type = db.Column(db.String(10), default='A') # 'A' أو 'B'

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    plan_type = db.Column(db.String(10), nullable=False) # 'A' أو 'B'
    description = db.Column(db.Text, nullable=True)

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.String(100), nullable=True)
    content_url = db.Column(db.String(300), nullable=True)

class StudentSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)
    status = db.Column(db.String(50), default='قادمة') # قادمة، بدأت، مكتملة، فائتة
    day_of_week = db.Column(db.String(50), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)

class KnowledgeFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=True)
    file_path = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(100), nullable=False)

class SupportKnowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(250), nullable=True)
    verified = db.Column(db.Boolean, default=True)
