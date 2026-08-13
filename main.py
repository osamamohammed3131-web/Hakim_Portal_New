import os
from flask import Flask, redirect, url_for, render_template_string, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Material, Lecture, StudentProgress, SmartScheduleItem
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

# --- مسار الدخول الموحد ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('بيانات الدخول غير صحيحة')
    return render_template_string('''
        <div style="direction:rtl; text-align:center; font-family:Tahoma; padding:50px;">
            <h2>تسجيل الدخول - منصة حكيم</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="البريد الإلكتروني" required><br>
                <input type="password" name="password" placeholder="كلمة المرور" required><br>
                <button type="submit">دخول</button>
            </form>
            <p><a href="/register">إنشاء حساب طالب</a></p>
        </div>''')

# --- مسار تسجيل الطالب ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password_hash=generate_password_hash(request.form.get('password')),
            role='student',
            plan_type=request.form.get('plan_type')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string('''
        <div style="direction:rtl; font-family:Tahoma; padding:50px;">
            <h2>تسجيل طالب جديد</h2>
            <form method="POST">
                <input name="username" placeholder="الاسم" required><br>
                <input name="email" placeholder="البريد" required><br>
                <input name="password" type="password" placeholder="كلمة المرور" required><br>
                <select name="plan_type"><option value="A">خطة A</option><option value="B">خطة B</option></select><br>
                <button type="submit">تسجيل</button>
            </form>
        </div>''')

# --- المسار الرئيسي الذكي ---
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.role == 'admin' or current_user.email == 'superadmin@hakim.com':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('student_dashboard'))

@app.route('/student')
@login_required
def student_dashboard():
    return f"<h1>أهلاً بك يا طالب في منصة حكيم</h1><p>خطة دراستك: {current_user.plan_type}</p><a href='/logout'>خروج</a>"

@app.route('/admin')
@login_required
def admin_dashboard():
    return "<h1>لوحة تحكم المشرف العام</h1><a href='/logout'>خروج</a>"

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- تهيئة النظام ---
with app.app_context():
    db.create_all()
    # التأكد من وجود المشرف دائماً
    if not User.query.filter_by(email='superadmin@hakim.com').first():
        admin = User(username='SuperAdmin', email='superadmin@hakim.com', 
                     password_hash=generate_password_hash('Admin@2026'), role='superadmin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
