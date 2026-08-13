import os
from flask import Flask, redirect, url_for, render_template_string, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Material, Lecture, SmartScheduleItem
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- المسارات: هنا يتم تطبيق كل وظائف المنصة الفعلية ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('student_dashboard'))
    return render_template_string('<div style="text-align:center;"><h2>دخول حكيم</h2><form method="POST"><input name="email" placeholder="البريد"><input name="password" type="password" placeholder="كلمة المرور"><button>دخول</button></form></div>')

@app.route('/student')
@login_required
def student_dashboard():
    return render_template_string('<h1>لوحة الطالب - خطة {{ current_user.plan_type }}</h1><ul><li><a href="/plan">المقررات</a></li><li><a href="/schedule">الجدول الذكي</a></li></ul>')

@app.route('/plan')
@login_required
def plan():
    materials = Material.query.filter_by(plan_type=current_user.plan_type).all()
    return render_template_string('<h2>مقرراتك</h2><ul>{% for m in materials %}<li>{{ m.name }}</li>{% endfor %}</ul>')

@app.route('/schedule')
@login_required
def schedule():
    items = SmartScheduleItem.query.filter_by(user_id=current_user.id).all()
    return render_template_string('<h2>جدولك الذكي</h2><ul>{% for i in items %}<li>{{ i.title }}</li>{% endfor %}</ul>')

@app.route('/support')
def support():
    return render_template_string('<h2>بوابة دعم حكيم</h2><p>اسأل عن القبول والتسجيل هنا...</p>')

# --- تهيئة البيانات ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@hakim.com').first():
        admin = User(username='Admin', email='admin@hakim.com', password_hash=generate_password_hash('Admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
