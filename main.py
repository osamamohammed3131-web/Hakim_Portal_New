import os
from flask import Flask, redirect, url_for, render_template_string, request
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

# --- لوحة الطالب الفعلية بالهيكل المطلوب ---
@app.route('/student')
@login_required
def student_dashboard():
    return render_template_string('''
        <div style="direction:rtl; font-family:Tahoma; padding:30px; background:#f4f7f6; min-height:100vh;">
            <h1>مرحباً بك يا {{ current_user.username }} في منصة حكيم</h1>
            <div style="display:flex; gap:20px; margin-top:20px;">
                <div style="background:white; padding:20px; border-radius:10px; width:300px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <h3>خطة الدراسية ({{ current_user.plan_type }})</h3>
                    <a href="/plan" style="text-decoration:none; color:#2c3e50;">عرض المقررات والمحاضرات</a>
                </div>
                <div style="background:white; padding:20px; border-radius:10px; width:300px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <h3>الجدول الذكي</h3>
                    <a href="/schedule" style="text-decoration:none; color:#2c3e50;">إدارة المهام والجدول</a>
                </div>
            </div>
            <br><a href="/logout">تسجيل الخروج</a>
        </div>
    ''')

# --- عرض المقررات الفعلية ---
@app.route('/plan')
@login_required
def plan():
    materials = Material.query.filter_by(plan_type=current_user.plan_type).all()
    return render_template_string('''
        <div style="direction:rtl; font-family:Tahoma; padding:30px;">
            <h2>مقرراتك الدراسية - الخطة {{ current_user.plan_type }}</h2>
            {% for m in materials %}
                <div style="border:1px solid #ddd; padding:15px; margin-bottom:10px; border-radius:8px;">
                    <h3>{{ m.name }}</h3>
                    <p>{{ m.description }}</p>
                </div>
            {% endfor %}
            <br><a href="/student">عودة</a>
        </div>
    ''', materials=materials)

# --- لوحة المشرف الفعلية ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin' and current_user.email != 'superadmin@hakim.com':
        return "غير مسموح لك بالدخول", 403
    return render_template_string('''
        <div style="direction:rtl; font-family:Tahoma; padding:30px;">
            <h1>لوحة تحكم المشرف</h1>
            <p>إدارة النظام بالكامل، متابعة الطلاب، وتحديث المحتوى العلمي.</p>
            <ul>
                <li><a href="#">إضافة محاضرة جديدة</a></li>
                <li><a href="#">تعديل الجدول الذكي</a></li>
            </ul>
            <a href="/logout">خروج</a>
        </div>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('home'))
    return render_template_string('<div style="text-align:center; padding:50px;"><h2>تسجيل الدخول - منصة حكيم</h2><form method="POST"><input name="email" placeholder="البريد"><input name="password" type="password" placeholder="كلمة المرور"><button>دخول</button></form></div>')

@app.route('/')
def home():
    if not current_user.is_authenticated: return redirect(url_for('login'))
    return redirect(url_for('admin_dashboard')) if current_user.role == 'admin' else redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- تهيئة النظام ---
with app.app_context():
    db.create_all()
    # إضافة المشرف إذا لم يكن موجوداً
    if not User.query.filter_by(email='superadmin@hakim.com').first():
        admin = User(username='Admin', email='superadmin@hakim.com', password_hash=generate_password_hash('Admin2026!'), role='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
