import os
from flask import Flask, redirect, url_for, render_template_string, flash, request
from flask_login import login_required, current_user, LoginManager
from extensions import db
from models import User
from auth import auth_bp
from dashboard import dashboard_bp
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    if current_user.is_authenticated:
        role = getattr(current_user, 'role', 'student')
        is_admin_flag = getattr(current_user, 'is_admin', False)
        if is_admin_flag or role in ['super_admin', 'admin'] or current_user.email == 'superadmin@hakim.com':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/admin')
@app.route('/admin/')
@login_required
def admin_dashboard():
    role = getattr(current_user, 'role', 'student')
    is_admin_flag = getattr(current_user, 'is_admin', False)
    if not (is_admin_flag or role in ['super_admin', 'admin'] or current_user.email == 'superadmin@hakim.com'):
        return redirect(url_for('student_dashboard'))
    
    try:
        total_users = User.query.count()
    except Exception:
        total_users = 1

    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>لوحة المشرف العام</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .header { background: #0f172a; color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-top: 20px; }
        .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6; }
        .logout { display: inline-block; margin-top: 20px; background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style></head>
    <body>
        <div class="header">
            <h1>لوحة تحكم المشرف العام (Super Admin)</h1>
            <p>مرحباً: {{ current_user.email }} - إجمالي المستخدمين: {{ total_users }}</p>
        </div>
        <div class="grid">
            <div class="card"><h3>إدارة الطلاب</h3><p>قبول ورفض ومتابعة الطلاب.</p></div>
            <div class="card"><h3>المستخدمين والصلاحيات</h3><p>التحكم بالأدوار والصلاحيات.</p></div>
            <div class="card"><h3>أعضاء هيئة التدريس</h3><p>إدارة الأساتذة والمشرفين.</p></div>
            <div class="card"><h3>المقررات والخطط</h3><p>المسارات الأكاديمية (Plan A & B).</p></div>
            <div class="card"><h3>الواجبات والدرجات</h3><p>الكويزات، الاختبارات ورصد الدرجات.</p></div>
            <div class="card"><h3>الإعلانات والإشعارات</h3><p>التعاميم والتنبيهات العامة.</p></div>
            <div class="card"><h3>سجل العمليات والأمان</h3><p>مراجعة حركات النظام.</p></div>
            <div class="card"><h3>إعدادات المنصة</h3><p>ضبط المتغيرات العامة.</p></div>
        </div>
        <div style="text-align: center;"><a href="/logout" class="logout">تسجيل الخروج</a></div>
    </body></html>
    """
    return render_template_string(html_content, current_user=current_user, total_users=total_users)

@app.route('/student')
@app.route('/student/')
@login_required
def student_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>لوحة الطالب</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f8fafc; margin: 0; padding: 20px; direction: rtl; }
        .header { background: #0284c7; color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-top: 20px; }
        .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 4px solid #0284c7; }
        .logout { display: inline-block; margin-top: 20px; background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style></head>
    <body>
        <div class="header">
            <h1>لوحة الطالب الأكاديمية</h1>
            <p>مرحباً: {{ current_user.email }}</p>
        </div>
        <div class="grid">
            <div class="card"><h3>المقررات الدراسية</h3><p>المواد والكتب للفصل الحالي.</p></div>
            <div class="card"><h3>الخطط الدراسية</h3><p>مسارات التخرج وPlan A & B.</p></div>
            <div class="card"><h3>المحاضرات والمحتوى</h3><p>الملفات والمراجع العلمية.</p></div>
            <div class="card"><h3>الواجبات والكويزات</h3><p>التقييمات وتسليم الواجبات.</p></div>
            <div class="card"><h3>الدرجات والنتائج</h3><p>السجل الأكاديمي والمعدل.</p></div>
            <div class="card"><h3>الجدول والحضور</h3><p>مواعيد المحاضرات وسجل الحضور.</p></div>
            <div class="card"><h3>الإعلانات والمجتمع</h3><p>التنبيهات وقنوات النقاش.</p></div>
            <div class="card"><h3>الدعم والمساعدة</h3><p>التواصل مع الدعم الفني.</p></div>
        </div>
        <div style="text-align: center;"><a href="/logout" class="logout">تسجيل الخروج</a></div>
    </body></html>
    """
    return render_template_string(html_content, current_user=current_user)

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(email='superadmin@hakim.com').first()
    hashed_password = generate_password_hash('Admin@Hakim2026!', method='pbkdf2:sha256')
    if not admin:
        new_admin = User(username='SuperAdmin', email='superadmin@hakim.com', password_hash=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
    else:
        admin.password_hash = hashed_password
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
