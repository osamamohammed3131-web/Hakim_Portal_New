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
    return render_template_string('''
        <div style="text-align:center; margin-top:50px; font-family:Tahoma; direction:rtl;">
            <h2>تسجيل الدخول - منصة حكيم</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="البريد الإلكتروني" style="padding:10px; margin:5px; width:250px;"><br>
                <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; margin:5px; width:250px;"><br>
                <button type="submit" style="padding:10px 20px; background:#0284c7; color:white; border:none; border-radius:5px; cursor:pointer;">دخول</button>
            </form>
            <p style="margin-top:15px;"><a href="/register" style="color:#0284c7; text-decoration:none;">تسجيل طالب جديد</a></p>
        </div>''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            return "البريد مستخدم مسبقاً! <a href='/register'>رجوع</a>"
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='student',
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string('''
        <div style="text-align:center; margin-top:50px; font-family:Tahoma; direction:rtl;">
            <h2>تسجيل حساب طالب جديد - منصة حكيم</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم" style="padding:10px; margin:5px; width:250px;" required><br>
                <input type="email" name="email" placeholder="البريد الإلكتروني" style="padding:10px; margin:5px; width:250px;" required><br>
                <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; margin:5px; width:250px;" required><br>
                <button type="submit" style="padding:10px 20px; background:#10b981; color:white; border:none; border-radius:5px; cursor:pointer;">إتمام التسجيل</button>
            </form>
            <p style="margin-top:15px;"><a href="/login" style="color:#0284c7; text-decoration:none;">العودة لتسجيل الدخول</a></p>
        </div>''')

@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if getattr(current_user, 'is_admin', False) or current_user.email == 'superadmin@hakim.com':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('student_dashboard'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px; background:#f8fafc;">
            <h1 style="color:#0f172a;">لوحة تحكم المشرف العام</h1>
            <p>أهلاً بك: <b>{{ current_user.email }}</b></p>
            <hr>
            <h3>روابط وأقسام الإدارة:</h3>
            <ul>
                <li><a href="/student">معاينة لوحة الطالب</a></li>
                <li>إدارة الطلاب وقبولهم</li>
                <li>المقررات والخطط الدراسية</li>
                <li>الدرجات والتقييمات</li>
            </ul>
            <br><a href="/logout" style="background:#ef4444; color:white; padding:8px 15px; text-decoration:none; border-radius:5px;">تسجيل الخروج</a>
        </div>''', current_user=current_user)

@app.route('/student')
@login_required
def student_dashboard():
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px; background:#f0f9ff;">
            <h1 style="color:#0369a1;">لوحة الطالب الأكاديمية</h1>
            <p>أهلاً بك: <b>{{ current_user.email }}</b></p>
            <hr>
            <h3>أقسام الطالب:</h3>
            <ul>
                <li>المقررات المسجلة</li>
                <li>الخطط الدراسية (Plan A & B)</li>
                <li>الواجبات والكويزات</li>
                <li>الدرجات والنتائج</li>
                <li>الجدول الدراسي</li>
            </ul>
            <br><a href="/logout" style="background:#ef4444; color:white; padding:8px 15px; text-decoration:none; border-radius:5px;">تسجيل الخروج</a>
        </div>''', current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

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
