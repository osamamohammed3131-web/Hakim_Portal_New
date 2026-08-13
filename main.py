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
        if getattr(current_user, 'is_admin', False) or getattr(current_user, 'role', '') in ['super_admin', 'admin'] or current_user.email == 'superadmin@hakim.com':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('auth.login'))

# --- 1. لوحة المشرف العام (Admin Dashboard) متكاملة ومباشرة ---
@app.route('/admin')
@app.route('/admin/')
@login_required
def admin_dashboard():
    is_admin_flag = getattr(current_user, 'is_admin', False)
    user_role = getattr(current_user, 'role', None)
    
    if is_admin_flag or user_role in ['super_admin', 'admin'] or current_user.email == 'superadmin@hakim.com':
        html_content = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>لوحة تحكم المشرف العام - منصة حكيم</title>
            <style>
                body { font-family: Tahoma, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; direction: rtl; }
                .header { background: #1e293b; color: white; padding: 20px; border-radius: 8px; text-align: center; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6; }
                .card h3 { margin-top: 0; color: #1e293b; }
                .logout { display: inline-block; margin-top: 20px; background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>لوحة تحكم المشرف العام (Super Admin)</h1>
                <p>مرحباً بك، {{ current_user.email }} - النظام متصل بقاعدة البيانات ويعمل بكامل الصلاحيات</p>
            </div>
            <div class="grid">
                <div class="card"><h3>إدارة الطلاب</h3><p>متابعة وحذف وتعديل بيانات الطلاب المسجلين.</p></div>
                <div class="card"><h3>المستخدمين والصلاحيات</h3><p>التحكم بالأدوار والصلاحيات الممنوحة للنظام.</p></div>
                <div class="card"><h3>أعضاء هيئة التدريس</h3><p>إدارة الأساتذة والمشرفين الأكاديميين.</p></div>
                <div class="card"><h3>المقررات والخطط</h3><p>تخطيط المسارات الأكاديمية (Plan A & Plan B).</p></div>
                <div class="card"><h3>الواجبات والاختبارات</h3><p>إدارة الكويزات، الاختبارات القصيرة، ودرجات الطلاب.</p></div>
                <div class="card"><h3>الإعلانات والإشعارات</h3><p>إرسال التعاميم والتنبيهات للعام الدراسي.</p></div>
                <div class="card"><h3>السجلات والأمان</h3><p>مراجعة حركات النظام وسجلات الدخول والخروج.</p></div>
                <div class="card"><h3>إعدادات النظام</h3><p>ضبط المتغيرات العامة للمنصة.</p></div>
            </div>
            <div style="text-align: center;">
                <a href="/logout" class="logout">تسجيل الخروج</a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_content, current_user=current_user)
    
    flash('غير مسموح لك بالوصول إلى لوحة المشرف.')
    return redirect(url_for('student_dashboard'))

# --- 2. لوحة الطالب (Student Dashboard) متكاملة ومباشرة ---
@app.route('/student')
@app.route('/student/')
@login_required
def student_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>لوحة الطالب الأكاديمية - منصة حكيم</title>
        <style>
            body { font-family: Tahoma, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; direction: rtl; }
            .header { background: #0f172a; color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 4px solid #10b981; }
            .card h3 { margin-top: 0; color: #0f172a; }
            .logout { display: inline-block; margin-top: 20px; background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>لوحة الطالب الأكاديمية</h1>
            <p>مرحباً بك، {{ current_user.email }}</p>
        </div>
        <div class="grid">
            <div class="card"><h3>المقررات الدراسية</h3><p>عرض المواد والكتب المقررة للفصل الحالي.</p></div>
            <div class="card"><h3>الخطط الدراسية</h3><p>متابعة المسارات الأكاديمية وخطط التخرج.</p></div>
            <div class="card"><h3>الواجبات والملفات</h3><p>تسليم الواجبات وتحميل الملازم والمراجع.</p></div>
            <div class="card"><h3>الاختبارات والكويزات</h3><p>التقييمات القصيرة والامتحانات النهائية.</p></div>
            <div class="card"><h3>الدرجات والنتائج</h3><p>متابعة السجل الأكاديمي وتوزيع الدرجات.</p></div>
            <div class="card"><h3>الجدول الدراسي</h3><p>مواعيد المحاضرات الحية والدروس.</p></div>
            <div class="card"><h3>الإعلانات والإشعارات</h3><p>آخر التنبيهات والأخبار الأكاديمية.</p></div>
            <div class="card"><h3>المجتمع والدعم</h3><p>التواصل مع الزملاء وطلب الدعم الفني.</p></div>
        </div>
        <div style="text-align: center;">
            <a href="/logout" class="logout">تسجيل الخروج</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, current_user=current_user)

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(email='superadmin@hakim.com').first()
    hashed_password = generate_password_hash('Admin@Hakim2026!', method='pbkdf2:sha256')
    
    if not admin:
        new_admin = User(
            username='SuperAdmin', 
            email='superadmin@hakim.com', 
            password_hash=hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
    else:
        admin.password_hash = hashed_password
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
