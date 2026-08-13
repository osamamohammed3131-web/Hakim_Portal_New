import os
from flask import Flask, redirect, url_for, render_template_string, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db
from models import User
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

# --- المسارات ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('خطأ في البيانات')
    return render_template_string('''<form method="POST" style="text-align:center; margin-top:50px; font-family:Tahoma;">
        <h2>تسجيل الدخول - منصة حكيم</h2>
        <input type="email" name="email" placeholder="البريد الإلكتروني" style="padding:10px; margin:5px; width:250px;"><br>
        <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; margin:5px; width:250px;"><br>
        <button type="submit" style="padding:10px 20px; background:#0284c7; color:white; border:none; border-radius:5px; cursor:pointer;">دخول</button></form>''')

@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.is_admin or current_user.email == 'superadmin@hakim.com':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('student_dashboard'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template_string('<h1>لوحة تحكم المشرف العام</h1><p>أهلاً بك: {{ current_user.email }}</p><a href="/logout">تسجيل الخروج</a>')

@app.route('/student')
@login_required
def student_dashboard():
    return render_template_string('<h1>لوحة الطالب الأكاديمية</h1><p>أهلاً بك: {{ current_user.email }}</p><a href="/logout">تسجيل الخروج</a>')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- تهيئة قاعدة البيانات ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='superadmin@hakim.com').first():
        new_admin = User(username='Admin', email='superadmin@hakim.com', 
                         password_hash=generate_password_hash('Admin@Hakim2026!'), is_admin=True)
        db.session.add(new_admin)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
